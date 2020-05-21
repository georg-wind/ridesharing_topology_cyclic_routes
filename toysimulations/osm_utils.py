import osmnx as ox
import networkx as nx
import numpy as np
from copy import deepcopy
from shapely.geometry import Point, Polygon
from collections import namedtuple
from pyproj import CRS, Transformer
import math

XY = namedtuple('XY', field_names=('x', 'y'))


def _overpass_filter_highway_upto_level(level):
    """
    Generates an overpass filter (See https://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide)
    for selecting only streets upto importance `level`.

    Also deselects streets not relevant for public routing, e.g. provate pr driveways.
    """
    street_impotance_levels = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary']
    assert level in street_impotance_levels

    highway_types_to_include = street_impotance_levels[:street_impotance_levels.index(level)+1]
    custom_filter='|'.join(highway_types_to_include)
    return f'["area"!~"yes"]["highway"~"{custom_filter}"]'\
           f'["motor_vehicle"!~"no"]["motorcar"!~"no"]["access"!~"private"]'\
           f'["service"!~"parking|parking_aisle|driveway|private|emergency_access"]'

def download_streetnetwork(center, meter_distance, upto='primary'):
    """
    Using OSMnx, downloads streetnetwork upto certain importance level.
    Desired area is specified by means of a center and a radius.
    """
    custom_filter = _overpass_filter_highway_upto_level(upto)
    G = ox.graph_from_point(center, distance=meter_distance, simplify=True,
                            truncate_by_edge=False, distance_type='bbox',
                            custom_filter=custom_filter)
    return G

def download_streetnetwork_from_bbox(north, south, east, west, upto='primary'):
    """
    Same as download-streetnetwork. Desired area is specified by means of
    a bbox.
    """
    custom_filter = _overpass_filter_highway_upto_level(upto)
    G = ox.graph_from_bbox(north, south, east, west, simplify=True,
                           truncate_by_edge=False,
                           custom_filter=custom_filter)
    return G

def download_streetnetwork_from_polygon(vertices, upto='primary'):
    """
    Same as download-streetnetwork. Desired area is specified by means of
    a polygon.
    """

    custom_filter = _overpass_filter_highway_upto_level(upto)
    poly = Polygon(shell=vertices)
    G = ox.graph_from_polygon(poly, simplify=True,
                           truncate_by_edge=False,
                           custom_filter=custom_filter)
    return G

def giant_component(G):
    """
    Returns the biggest connected component of G.
    """
    Gcc = max(nx.connected_components(G), key=lambda x:len(x))
    return nx.subgraph(G, Gcc)

def postprocess_osm_network(G, coarse_grain=15, return_node_mapping=False):
    """
    Accepts a streetnetwork returned by ox.graph_from_.*, and converts it into
    an undirected networkx graph, coarse graining it as per the supplied
    `coarse_graining` parameter, which is to be supplied in meters. See the
    docstring of `coarse_grain_osm_network` for details.

    If the resulting graph is disconnected, only returns the biggest connected
    component.

    If `return_node_mapping` is true, then a mapping between the original
    (non coarse grained) and the new (coarse grained) node labels are 
    returned.
    """
    if return_node_mapping == True:
        coarse, mapping = coarse_grain_osm_network(G, tolerance=coarse_grain,
            return_node_mapping=return_node_mapping)

        return giant_component(coarse), mapping
    else:
        coarse = coarse_grain_osm_network(G, tolerance=coarse_grain,
            return_node_mapping=return_node_mapping)
        return giant_component(coarse)


def coarse_grain_osm_network(G, tolerance=10, return_node_mapping=False):
    """
    Accepts an (unprojected) osmnx graph and coarse grains it.
    Tolerance is specified in meters. The coarse graining is performed as
    follows:
    1. Around each node, a circle of radius=tolerance meters is drawn.
    2. If any two (or more) nodes' circles overlap, they are coarse-grained
       into a single node.
    3. The edges are naturally rewired whenever one (or both) of its endpoints
       are coarse grained.
    4. If the previous step results in a self-loop, it is discarded.
    """
    metadata = G.graph
    if 'proj' in metadata and metadata['proj'] == 'utm':
        G_proj = G
    else:
        G_proj = ox.project_graph(G)
    gdf_nodes = ox.graph_to_gdfs(G_proj, edges=False)
    buffered_nodes = gdf_nodes.buffer(tolerance).unary_union

    old2new = dict() # key=old node label, value={'label': new_node_label, 'x': coord_x,
                                             #'y': coord_y, 'lat': ?, 'lon': ?}
    for node, data in G_proj.nodes(data=True):
        x, y = data['x'], data['y']
        lon, lat = data['lon'], data['lat']
        osm_id = data['osmid']

        for poly_idx, polygon in enumerate(buffered_nodes):
            if polygon.contains(Point(x,y)):
                poly_centroid = polygon.centroid
                poly_centroid_latlon = utm_to_latlon(XY(x=poly_centroid.x,
                                                        y=poly_centroid.y),
                                                     utm_zone=CRS.from_string(G_proj.graph['crs']).to_dict()['zone']
                                                    )
                old2new[node] = dict(label=poly_idx, x=poly_centroid.x, y=poly_centroid.y,
                                     lon=poly_centroid_latlon.x, lat=poly_centroid_latlon.y)
                break

    H = nx.Graph()

    for node in G_proj.nodes():
        new_node_data = old2new[node]
        new_label = new_node_data['label']

        H.add_node(new_label, **new_node_data)

    for u,v, data  in G_proj.edges(data=True):
        u2,v2 = old2new[u]['label'], old2new[v]['label']

        if u2 != v2:
            H.add_edge(u2, v2, **data)
    H.graph = {'crs': G_proj.graph['crs'], 'name': G_proj.graph['name']}
    if return_node_mapping is True:
        return H, {old_node: data['label'] for old_node, data in old2new.items()}
    else:
        return H

def homogenize_edge_lengths(G, target_edge_length=100):
    """
    Adds intermediate nodes in edges to achieve a homogeneous edge
    length in G.
    """
    H = nx.Graph()
    for u,v,data in G.edges(data=True):
        length = data['length'] # in meters


        H.add_node(u, **G.nodes[u])
        H.add_node(v, **G.nodes[v])

        num_new_nodes, last_edge_length = divmod(length, target_edge_length)
        num_new_nodes = int(num_new_nodes)
        if num_new_nodes == 0:
            H.add_edge(u, v, **data)
            continue

        frac_arr = np.arange(0, length, target_edge_length)/length
        frac_arr = frac_arr.reshape(len(frac_arr), 1)

        u_dat = np.array([G.nodes[u]['lat'], G.nodes[u]['lon'], G.nodes[u]['y'], G.nodes[u]['x']])
        v_dat = np.array([G.nodes[v]['lat'], G.nodes[v]['lon'], G.nodes[v]['y'], G.nodes[v]['x']])

        intermediate_nodes_dat = (1-frac_arr)*u_dat + frac_arr*v_dat

        prev_node_label = u
        for i in range(num_new_nodes):
            new_lat, new_lon, new_y, new_x = intermediate_nodes_dat[i, :]
            new_node_label = f"{u}_{v}_{i+1}"
            H.add_node(new_node_label, lat=new_lat, lon=new_lon, x=new_x, y=new_y)
            H.add_edge(prev_node_label, new_node_label, length=target_edge_length)
            prev_node_label = new_node_label
        # now the last segment
        H.add_edge(prev_node_label, v, length=last_edge_length)

    H.graph = {'crs': G.graph['crs'], 'name': G.graph['name']}
    return H

def latlon_to_utm(latlon):
    utm_zone = int(math.floor((latlon.x + 180) / 6.) + 1)
    crs_local_utm = CRS(proj='utm', zone=utm_zone, ellps='WGS84')

    transformer_to_utm = Transformer.from_crs("EPSG:4326", crs_local_utm, always_xy=True)

    x, y = transformer_to_utm.transform(latlon.x, latlon.y)
    return XY(x=x, y=y)

def utm_to_latlon(xy, utm_zone):
    crs_local_utm = CRS(proj='utm', zone=utm_zone, ellps='WGS84')

    transformer_to_utm = Transformer.from_crs(crs_local_utm, "EPSG:4326", always_xy=True)

    x, y = transformer_to_utm.transform(xy.x, xy.y)
    return XY(x=x, y=y)

