import hashlib
import random
from collections import defaultdict, Counter

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from tqdm import tqdm

from graph_builder import build_cycle_routespaces
from utils import run_or_get_pickle, pickle_loader


def identify_and_illustrate_motifs(x, topology, spm, base_net_graph, n=20):
    """
    Identifies and illustrates the top n motifs in the given graph.
    :param route_space_walk_graph: the route-space-walk graph
    :param base_net_graph: the base network graph
    :param n: top n most frequent motifs to be illustrated
    :return:
    """
    base_net_graph_edges = set(tuple(sorted(edge)) for edge in base_net_graph.edges())
    motifs = identify_motifs_wrapped(x, topology, spm, base_net_graph_edges)
    # sort motifs by decreasing number of visits
    visualize_top_n_motifs(motifs, n, base_net_graph)


def identify_motifs(unique_id, base_net_graph_edges, sample_size=10 ** 5):
    pickle_path_route = f"./data/02_stats/{unique_id}_calc_single_stats.dill"
    route = pickle_loader(pickle_path_route)[0]
    print(f"{unique_id}: 1. Route loaded.")

    route_space_walk_graph = build_cycle_routespaces(route)

    motifs = defaultdict(dict)
    all_nodes_with_data = list(route_space_walk_graph.nodes(data=True))

    # Determine nodes to process based on sample size
    if len(all_nodes_with_data) > sample_size:
        # Randomly sample nodes with data if the graph is larger than the sample size
        nodes_to_process = random.sample(all_nodes_with_data, sample_size)
    else:
        # Use all nodes with data if the graph is smaller than or equal to the sample size
        nodes_to_process = all_nodes_with_data

    for edge_set, edge_data in tqdm(nodes_to_process, desc="Processing Edge-Sets"):
        subgraph = construct_graph_from_edge_set(edge_set, base_net_graph_edges)
        if len(edge_set) in motifs.keys():
            for motif_hash, motif_data in motifs[len(edge_set)].items():
                if nx.is_isomorphic(subgraph, motif_data["graph"], node_match=match_all, edge_match=edge_matcher):
                    motifs[len(edge_set)][motif_hash]["sets"].append(edge_set)
                    motifs[len(edge_set)][motif_hash]["visits"].extend(edge_data["visits"])
                    break
            else:
                motifs[len(edge_set)][graph_hash(subgraph)] = {
                    "graph": subgraph,
                    "sets": [edge_set],
                    "visits": edge_data["visits"]
                }
        else:
            motifs[len(edge_set)][graph_hash(subgraph)] = {
                "graph": subgraph,
                "sets": [edge_set],
                "visits": edge_data["visits"]
            }
    return motifs

def identify_motifs_wrapped(x, topology, spm, base_net_graph_edges):
    unique_id = f"{topology}_{spm}_{str(x)}"
    wrapped_function = run_or_get_pickle(unique_id, "03_motifs")(identify_motifs)
    return wrapped_function(unique_id, base_net_graph_edges)


def visualize_top_n_motifs(motifs_by_original_length_dict, n, base_net_graph):
    # sort motifs by decreasing number of visits
    sorted_motifs = []
    for edge_set_length, motifs in motifs_by_original_length_dict.items():
        sorted_motifs.extend([motif for _, motif in motifs.items()])

    sorted_motifs = sorted(sorted_motifs, key=lambda x: len(x['visits']), reverse=True)

    pos = nx.get_node_attributes(base_net_graph, 'pos')
    total_visits = sum(len(motif["visits"]) for motif in sorted_motifs)

    # Get all edge frequencies to determine the range of the colormap
    all_edge_frequencies = [data['edge_frequency'] for motif in sorted_motifs for u, v, data in
                            motif['graph'].edges(data=True)]
    min_freq = min(all_edge_frequencies)
    max_freq = max(all_edge_frequencies)
    norm = mcolors.Normalize(vmin=min_freq, vmax=max_freq)
    cmap = plt.cm.viridis  # or any other colormap

    for i in tqdm(range(min(n, len(sorted_motifs))), desc="Visualizing motifs"):
        motif = sorted_motifs[i]
        plt.figure(figsize=(5, 5))

        # Get edge colors based on the continuous colormap
        edge_colors = [cmap(norm(motif["graph"][u][v]['edge_frequency'])) for u, v in motif["graph"].edges()]

        # Draw nodes
        nx.draw_networkx_nodes(motif["graph"], pos=pos, node_color='blue')
        # Draw curved edges without arrow heads
        nx.draw_networkx_edges(motif["graph"], pos=pos, edge_color=edge_colors, connectionstyle="arc3,rad=0.1",
                               arrows=True, arrowstyle='-')

        # Create an empty plot with a legend entry for the statistics
        plt.plot([], [], ' ', label=f"Number of Edge-Sets: {len(motif['sets'])}")
        plt.plot([], [], ' ', label=f"Total Visits: {len(motif['visits'])}")
        plt.plot([], [], ' ', label=f"Share of Visits: {round(len(motif['visits']) / total_visits * 100, 2)} %")

        # Add a colorbar as the legend for edge frequencies
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])  # only needed for matplotlib < 3.1
        plt.colorbar(sm, label='Edge Frequency')

        plt.legend(loc='upper left')

        plt.savefig(f"./data/motifs/{i}.png")
        # display(Image(f"./data/motifs/{i}.png"))
        plt.close()


## Visualize binned motifs

def sort_and_bin_motifs(motifs, motif_visits_rel, motif_optimality):
    motif_nodes = [len(motif["graph"].nodes()) for motif in motifs]
    combined_list = list(zip(motif_nodes, motif_visits_rel, motif_optimality, motifs))
    sorted_combined_list = sorted(combined_list, key=lambda x: (x[0], x[2]))

    bin_edges = np.linspace(min(motif_nodes) - 0.1, max(motif_nodes) + 0.1, min(6, len(set(motif_nodes)) + 1))
    binned_motifs = {bin_i: [] for bin_i in range(len(bin_edges) - 1)}

    for motif in sorted_combined_list:
        bin_index = np.digitize(motif[0], bin_edges) - 1
        binned_motifs[bin_index].append(motif)

    return binned_motifs


# @cache_to_mongodb()
def motif_dist_data(motifs):
    """
    :param motifs:
    :return: x, y, z, x.gridlines, y.gridlines
    """
    motif_visits = np.array([len(motif["visits"]) for motif in motifs])
    motif_visits_rel = motif_visits / motif_visits.sum()
    motif_optimality = compute_optimality_scores(motifs)
    binned_motifs = sort_and_bin_motifs(motifs, motif_visits_rel, motif_optimality)

    bin_boundaries_x = []
    motif_optimality_sorted = []
    x_coords = []
    cdf = np.array([])
    bin_boundaries_y = [0]

    for bin_i, motifs_in_bin in binned_motifs.items():
        motif_visits_rel_sorted = [motif[1] for motif in motifs_in_bin]
        cdf = np.append(cdf, np.cumsum(motif_visits_rel_sorted) + bin_boundaries_y[-1])
        bin_boundaries_y.append(cdf[-1])

        nodes_in_bin = set([motif[0] for motif in motifs_in_bin])
        bin_x_coords = np.linspace(min(nodes_in_bin) - 0.5, max(nodes_in_bin) + 0.5, len(motifs_in_bin) + 2)[1:-1]
        x_coords.extend(bin_x_coords)
        bin_boundaries_x.extend([min(nodes_in_bin), max(nodes_in_bin)])
        motif_optimality_sorted.extend([motif[2] for motif in motifs_in_bin])

    return x_coords, cdf, motif_optimality_sorted, bin_boundaries_x, bin_boundaries_y


def plot_motif_distribution(x_coords, cdf, motif_optimality_sorted, bin_bounds_x, bin_bounds_y, topology, x, n_reqs):
    fig, ax = plt.subplots()
    plt.scatter(x_coords, cdf, c=motif_optimality_sorted, cmap='RdYlGn', marker='.', edgecolor='none')

    ax.set_xlim([bin_bounds_x[0] - 0.6, bin_bounds_x[-1] + 0.6])
    bin_edges = np.add(bin_bounds_x[1:-1:2], 0.5)
    ax.set_xticks(bin_edges, minor=False)
    ax.set_xticklabels([""] * len(bin_edges), minor=False)

    minor_ticklabel_positions = np.subtract(bin_bounds_x[1::2], (bin_bounds_x[1] - bin_bounds_x[0]) / 2)
    ax.set_xticks(minor_ticklabel_positions, minor=True)
    if bin_bounds_x[0] != bin_bounds_x[1]:
        bin_labels = [f"{bin_bounds_x[i * 2]} to {bin_bounds_x[i * 2 + 1]} nodes" for i in
                      range(len(bin_bounds_x) // 2)]
        x_label = "Number of Nodes in Motif (Binned)"
    else:
        bin_labels = [f"{bin_bounds_x[i * 2]} nodes" for i in range(len(bin_bounds_x) // 2)]
        x_label = "Number of Nodes in Motif"
    # ax.set_xticklabels(bin_labels, rotation=-25, ha="left", minor=True)
    ax.set_xticklabels(bin_labels, minor=True)
    plt.xlabel(x_label)

    ax.set_yticks([x * 0.1 for x in range(11)], minor=False)
    ax.set_yticks(bin_bounds_y, minor=True)

    plt.colorbar(label='Motif Optimality: Number of Nodes / Number of Edges')
    plt.ylabel('Cumulative Distribution Function (CDF)')
    plt.suptitle("CDF of Motif Frequencies and Motif Optimality.")
    plt.title(f"{topology}. Request-rate {x}. {n_reqs} requests.")
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, axis='y')
    plt.grid(True, which='major', linestyle='--', linewidth=0.5, axis='x')
    plt.tight_layout()
    return plt


#### MOTIF VISUALIZATION ####
def construct_graph_from_edge_set(edge_set, base_net_graph_edges):
    # building a simple graph with edge edge_frequencies (for counting traversals) instead of a multi-graph
    graph = nx.Graph()
    edge_set = (tuple(sorted(e_set)) for e_set in edge_set)
    for (u, v), frequency in Counter(edge_set).items():
        graph.add_edge(u, v, edge_frequency=frequency, base_net=((u, v) in base_net_graph_edges))

    return graph


def edge_matcher(e1, e2):
    return (e1['edge_frequency'] == e2['edge_frequency']) and (e1['base_net'] == e2['base_net'])


def match_all(n1, n2):
    return True


def graph_hash(graph):
    # This is a placeholder for whatever hashing or signature function you decide is best
    # It should return a hashable object that is the same for isomorphic graphs
    # Example: hash the sorted adjacency list
    stringified_edges = ''.join(sorted(map(str, graph.edges())))
    return hashlib.sha256(stringified_edges.encode('utf-8')).hexdigest()


## compare this (older) function with optimality-functions in _03_optimalities.py
def compute_optimality_scores(motifs):
    return np.array([
        len(motif["graph"].nodes()) / sum(data['edge_frequency'] for _, _, data in motif["graph"].edges(data=True))
        for motif in motifs
    ])
