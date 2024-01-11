from collections import defaultdict

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import plotly.graph_objects as go
from tqdm import tqdm
# from utils.mongo_db_connect import cache_to_mongodb

def plot_new_nodes_share(routespace_walk):
    """
    Function to plot the share of new nodes over time.
    :param routespace_walk:
    :return:
    """

    observed_nodes = set()
    new_nodes_count = 0
    share_new_nodes = []

    for route in routespace_walk:
        if route not in observed_nodes:
            observed_nodes.add(route)
            new_nodes_count += 1
        share_new_nodes.append(new_nodes_count / len(observed_nodes))

    # plotting
    plt.figure(figsize=(10, 6))
    plt.plot(share_new_nodes, label="Share of New Nodes")
    plt.xlabel("Time")
    plt.ylabel("Share of New Nodes")
    plt.title("Share of Newly Added Nodes Over Time")
    plt.legend()
    plt.grid(True)
    plt.show()


def visualize_3d_spacewalk_new(G, base_net):
    base_traces = generate_base_graph_traces(base_net)
    df = build_vis_df(G, base_net)
    node_traces_on_lvls = generate_node_traces(df)

    fig = go.Figure(data=node_traces_on_lvls + base_traces,
                    skip_invalid=True)
    fig.show()


def generate_base_graph_traces(base_net):
    base_positions = [base_net["nodes"][node] for node in sorted(base_net["nodes"].keys())]
    x_base, y_base = zip(*base_positions)
    z_base = [0] * len(base_positions)  # setting all z-coordinates for base nodes to 0
    base_net_node_trace = go.Scatter3d(x=x_base, y=y_base, z=z_base,
                                       mode='markers+text',
                                       marker=dict(size=6,
                                                   color="blue"),
                                       text=sorted(base_net["nodes"].keys()),
                                       textposition="top center",
                                       showlegend=False,
                                       name="Base Graph Nodes")

    base_edge_positions = [(base_net["nodes"][edge[0]], base_net["nodes"][edge[1]]) for edge in base_net["edges"]]
    base_edges = {"x": [], "y": [], "z": []}

    for start, end in base_edge_positions:
        base_edges["x"].extend([start[0], end[0], None])
        base_edges["y"].extend([start[1], end[1], None])
        base_edges["z"].extend([0, 0, None])

    base_edge_trace = go.Scatter3d(x=base_edges["x"], y=base_edges["y"], z=base_edges["z"],
                                   mode='lines',
                                   line=dict(width=2,
                                             color="blue"),
                                   showlegend=False,
                                   name="Base Graph Edges")

    return [base_edge_trace, base_net_node_trace]

# @cache_to_mongodb()
def build_vis_df(G, base_net):
    # Extract routes and data (which includes "visits") from G nodes
    routes, data = zip(*G.nodes(data=True))

    # Extract "visits" from data
    visits = [len(d["visits"]) for d in data]
    del data

    # Initialize DataFrame with routes and visits
    df = pd.DataFrame({"routes": routes, "visit_count": visits})

    # Vectorized approach to generate binary columns for each edge in base_net["edges"]
    for base_edge in base_net["edges"]:
        df[base_edge] = df['routes'].apply(lambda route: (base_edge in route) * 1).astype('int8')

    # Compute edgeset_position in a vectorized manner
    positions = df['routes'].apply(lambda route: edgeset_position(route, base_net)).tolist()
    df[['x', 'y', 'z']] = pd.DataFrame(positions)

    # Compute color column using vectorized operations
    max_visit_count = df["visit_count"].max()
    cmap = cm.get_cmap('YlOrRd')
    df["color"] = df["visit_count"].apply(lambda count: cmap(count / max_visit_count))

    return df


def edgeset_position(edge_set, base_net):
    # returns the coordinates of the middle of the edges in the edge-set
    x_total, y_total, edge_count_not_in_base_net = 0, 0, 0
    for edge in edge_set:
        x, y = edge_position(edge[0], edge[1], base_net)
        x_total += x
        y_total += y
        if edge not in base_net["edges"]:
            edge_count_not_in_base_net += 1
    return (x_total / len(edge_set),
            y_total / len(edge_set),
            len(edge_set) + edge_count_not_in_base_net)  # (x, y, z)


def edge_position(start_node, end_node, base_net):
    """
    :param start_node:
    :param end_node:
    :return: coordinates of the middle of the edge
    """
    # assert (start_node, end_node) in base_net["edges"]
    return ((base_net["nodes"][start_node][0] + base_net["nodes"][end_node][0]) / 2,
            (base_net["nodes"][start_node][1] + base_net["nodes"][end_node][1]) / 2)


def generate_node_traces(df):
    node_traces = []
    for level in sorted(df['z'].unique().tolist()):
        df_lvl = df[df['z'] == level].copy()
        df_lvl = add_jitter(df_lvl)
        node_traces.append(go.Scatter3d(x=df_lvl['x'], y=df_lvl['y'], z=df_lvl['z_adj'],
                                        mode="markers",
                                        marker=dict(size=6,
                                                    color=df_lvl['color']),
                                        text=[f"{row['routes']}<br>Visit-Count: {row['visit_count']}" for _, row in
                                              df_lvl.iterrows()],
                                        hoverinfo="text",
                                        name=f"Edge-Sets of Size {str(level)}")
                           )
    return node_traces


def add_jitter(df):
    df['z_adj'] = df['z']

    # Create a dictionary to store counts of each (x, y) coordinate
    coord_counts = df.groupby(['x', 'y']).size().to_dict()
    coord_counts = {k: iter(range(1, v + 1)) for k, v in coord_counts.items()}  # convert counts to iterators

    # Function to compute jitter based on coordinate count
    def compute_jitter(row):
        count = next(coord_counts[(row['x'], row['y'])])
        jitter = (count - count % 2) * 0.05 * (-1) ** count  # alternating jitter
        return row['z'] + jitter

    df['z_adj'] = df.apply(compute_jitter, axis=1)
    return df


## OLD implementation without pandas

# 3D Graph Visualization
def visualize_3d_spacewalk(G, base_net):
    # edges are located in the middle between the base_net["nodes"]

    def rel_indegree(deg, min_indegs, max_indegs):
        return (deg - min_indegs + 0.1) / (max_indegs - min_indegs + 0.1)

    def find_duplicate_coords(G):
        coord_counts = defaultdict(int)
        duplicate_coords = set()

        # Traverse through the nodes to collect the coordinates
        for _, data in G.nodes(data=True):
            coord = data['position']  # Convert the position list to a tuple
            coord_counts[coord] += 1

        # Filter out coordinates that occur more than once
        for coord, count in coord_counts.items():
            if count > 1:
                duplicate_coords.add(coord)

        return list(duplicate_coords)

    positions = {node: edgeset_position(node, base_net) for node in
                 tqdm(G.nodes(), desc="Computing 3D positions of edge-sets")}
    # Set these positions as node attributes
    nx.set_node_attributes(G, positions, "position")

    # 1. Add base-graph
    base_traces = generate_base_graph_traces(base_net)

    # 2. Add routespace nodes and walk
    node_indegrees = {node: len(property["visits"]) for node, property in G.nodes(data=True)}
    min_indegs = min(node_indegrees.values())
    max_indegs = max(node_indegrees.values())

    duplicate_coords_dict = {coord: 0 for coord in find_duplicate_coords(G)}
    node_data_by_level = defaultdict(lambda: {"x": [], "y": [], "z": [], "names": [], "indegrees": []})

    # the z-value is the size of the edge-set - plus jitter if there are multiple nodes in the same position
    for node, data in G.nodes(data=True):
        x, y, z = data['position']
        # indegree = len(data["visits"])
        node_data_by_level[z]["x"].append(x)
        node_data_by_level[z]["y"].append(y)
        if data['position'] in duplicate_coords_dict.keys():
            # adding z-jitter to the nodes in the same position - probably not efficiently solved whatever
            count = duplicate_coords_dict[data['position']]
            jitter = (count - count % 2) * 0.05 * (-1) ** count  # alternating jitter
            node_data_by_level[z]["z"].append(z + jitter)
            duplicate_coords_dict[data['position']] += 1
        else:
            node_data_by_level[z]["z"].append(z)
        node_data_by_level[z]["names"].append(node)
        node_data_by_level[z]["indegrees"].append(node_indegrees[node])
        # node_data_by_level[z]["indegrees"].append(indegree)

    # Create scatter plot for nodes
    node_traces_on_lvls = []
    for z, node_data in sorted(node_data_by_level.items()):
        # nodes are colored by indegree
        cmap = plt.cm.get_cmap('YlOrRd')
        colors = [cmap(rel_indegree(deg, min_indegs, max_indegs)) for deg in node_data["indegrees"]]
        hover_texts = [(f"{name}<br>Indegree: {deg}")
                       for name, deg in
                       zip(node_data["names"], node_data["indegrees"])]
        node_traces_on_lvls.append(
            go.Scatter3d(x=node_data["x"], y=node_data["y"], z=node_data["z"],
                         mode="markers",
                         marker=dict(size=6, color=colors),
                         text=hover_texts,
                         hoverinfo="text",
                         name=f"Edge-Sets of Size {str(z)}")
        )

    # # extract edge positions using list comprehensions
    # edge_positions = [(G.nodes[edge[0]]['position'], G.nodes[edge[1]]['position']) for edge in G.edges()]
    # edges = {"x": [], "y": [], "z": []}
    #
    # for start, end in edge_positions:
    #     edges["x"].extend([start[0], end[0], None])
    #     edges["y"].extend([start[1], end[1], None])
    #     edges["z"].extend([start[2], end[2], None])
    #
    # number_of_edges = len(edge_positions)
    #
    # cmap_edges = plt.cm.get_cmap('GnBu')
    # # TODO: edge["traversals"] as color weights
    # edge_color_list = [cmap_edges(n) for n in np.linspace(start=0, stop=1, num=number_of_edges, endpoint=True)]
    #
    # # Create line plot for edges
    # edge_trace = go.Scatter3d(x=edges["x"], y=edges["y"], z=edges["z"],
    #                           mode='lines',
    #                           line=dict(width=2,
    #                                     color=edge_color_list),
    #                           name="Currently-scheduled-routes system transitions")

    # fig = go.Figure(data=node_traces_on_lvls + [edge_trace, base_edge_trace, base_net_node_trace],
    #                 skip_invalid=True)

    fig = go.Figure(data=node_traces_on_lvls + base_traces,
                    skip_invalid=True)
    fig.show()
