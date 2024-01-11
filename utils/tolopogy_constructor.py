import networkx as nx
import numpy as np


def graph_constructor(topology):
    if topology == "Göttingen":
        graph_path = './data/homogenized_networks/goe/'
        return nx.read_gpickle(f"{graph_path}/G_homog.gpkl")
    elif topology == "Harz":
        graph_path = './data/homogenized_networks/harz/'
        return nx.read_gpickle(f"{graph_path}/G_homog.gpkl")
    elif topology == "Berlin":
        graph_path = './data/homogenized_networks/berlin/'
        return nx.read_gpickle(f"{graph_path}/G_homog.gpkl")

    # Parse the topology type and size
    parts = topology.split('_')
    graph_type = parts[0]
    size = int(parts[1])

    # Generate the appropriate graph based on the type
    if graph_type == "line":
        graph = nx.grid_graph((size,))
        # pos = nx.spring_layout(graph)
        pos = {n: (n, 0) for n in range(size)}
    elif graph_type == "cycle":
        graph = nx.cycle_graph(size)
        pos = nx.circular_layout(graph)
    elif graph_type == "wheel":
        graph = nx.wheel_graph(size)
        center_node = 0  # Or any other node to be in the center
        edge_nodes = set(graph) - {center_node}
        pos = nx.circular_layout(graph.subgraph(edge_nodes))
        pos[center_node] = np.array([0, 0])  # Manually specify node position
    elif graph_type == "star":
        graph = nx.star_graph(size - 1)  # Subtract one for the center node
        pos = nx.spring_layout(graph)
        # pos = nx.planar_layout(graph)
    elif graph_type == "grid":
        side_length = int(np.sqrt(size))  # Assuming a square grid
        graph = nx.grid_2d_graph(side_length, side_length)
        pos = dict((n, n) for n in graph.nodes())  # Positions are the same as node labels
    elif graph_type == "trigrid":
        side_length = int(np.sqrt(size / 3))  # Assuming an equilateral triangle grid
        graph = nx.triangular_lattice_graph(side_length, side_length)
        pos = dict((n, n) for n in graph.nodes())  # Positions are the same as node labels
    else:
        raise ValueError("Unknown graph topology")

    # Add nodes to the graph with their positions as attributes
    for node, position in pos.items():
        graph.add_node(node, pos=position)

    return graph


# # Many berlins
# graph_path = './data/homogenized_networks/berlin/'
#
# with open(f"{graph_path}/diff_coarse_graining/all_berlin.pkl", 'rb') as f:
#     all_Gs = pickle.load(f)
#
# for coarse_graining_meters, target_edge_length in [
#                                                    (200, 400),
#                                                    (200, 600),
#                                                    (200, 800)
#                                                   ]:
#     print(f"Doing Berlin {coarse_graining_meters} {target_edge_length }")
#     # read the graph
#     _,G = all_Gs[coarse_graining_meters][target_edge_length]
#     pickle_path = f'./data/simulations/street_berlin_homogenized_coarse_graining_meters_{coarse_graining_meters}_target_edge_length_{target_edge_length}_{spm}_{xrange[1]}_{numreqs}.pkl'
#     simulate_different_request_rates(G, pickle_path, network_type='novolcomp')
