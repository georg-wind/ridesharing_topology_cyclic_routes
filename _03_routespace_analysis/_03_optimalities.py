from collections import Counter

import numpy as np
from tqdm import tqdm

from _03_routespace_analysis.graph_builder import build_cycle_routespaces
from utils import pickle_loader, get_stats_dict, run_or_get_pickle

def optimality_without_motifs(unique_id, base_net_graph_edges, base_net_graph_shortest_paths):
    # get the data
    pickle_path_route = f"./data/02_stats/{unique_id}_calc_single_stats.dill"
    route = pickle_loader(pickle_path_route)[0]
    print(f"{unique_id}: 1. Route loaded.")

    route_space_walk_graph = build_cycle_routespaces(route)
    print(f"{unique_id}: 2. Result-Space Walk loaded.")
    data_a = []
    data_b = []

    for edge_set, edge_data in tqdm(route_space_walk_graph.nodes(data=True), desc="Processing Edge-Sets in "
                                                                                  "Route-Space Walk"):
        unreal_edge_count = len(edge_set)
        visits = len(edge_data["visits"])
        real_edge_count = sum(1 if edge in base_net_graph_edges else base_net_graph_shortest_paths[edge[0]][edge[1]]
                              for edge in edge_set)
        nodes = [node for edge in edge_set for node in edge]

        if (not any(node_frequency > 2 for node_frequency in Counter(nodes).values()) and
                unreal_edge_count == real_edge_count):
            data_a.append((visits, unreal_edge_count))

        data_b.append((visits, real_edge_count, len(set(nodes))))

    # opt_a is the average no. nodes visited in a round-trip w/o double visits
    # even though this only captures the shortest of all roundtrips, it could be a good proxy for efficiency
    if len(data_a) == 0:
        #preventing get_stats_dict from crashing
        data_a = [(0, 0)]
    opt_a = get_stats_dict([d[1] for d in data_a], weights=[d[0] for d in data_a])
    # opt_b simply looks at all return-trips and captures there overall efficiency in both the no nodes of the trip
    #  (we would prefer the trip to visit many nodes before returning to the same) and the no edges (we prefer them to
    #  utilize as few edges as possible, i.e. nodes-1).
    opt_b = {"edges": get_stats_dict([d[1] for d in data_b], weights=[d[0] for d in data_b]),
             "nodes": get_stats_dict([d[2] for d in data_b], weights=[d[0] for d in data_b])}

    return opt_a, opt_b


def optimality_without_motifs_wrapped(x, topology, spm, base_net_graph_edges, base_net_graph_shortest_paths):
    unique_id = f"{topology}_{spm}_{str(x)}"
    wrapped_function = run_or_get_pickle(unique_id, "03_optimalities")(optimality_without_motifs)
    return wrapped_function(unique_id, base_net_graph_edges, base_net_graph_shortest_paths)



# optimality given motifs...

def xavg_compute_optimality_scores_a(motifs_by_original_length_dict):
    # filter motifs to only contain those with frequency 1 on all edges
    filtered_motifs = []
    edge_set_lengths = []
    for original_edge_set_length, motifs in motifs_by_original_length_dict.items():
        filtered_motifs.extend([motif for motif in motifs.values() if len(motif["graph"].edges()) ==
                                original_edge_set_length])
        edge_set_lengths.extend([original_edge_set_length] * (len(filtered_motifs) - len(edge_set_lengths)))

    motif_visits = np.array([len(motif["visits"]) for motif in filtered_motifs])
    relative_frequencies = motif_visits / motif_visits.sum()
    opt_a = sum(np.multiply(relative_frequencies, edge_set_lengths))
    return opt_a


def xavg_compute_optimality_scores_b(motifs_by_original_length_dict):
    optimality_b_factors = []
    for original_edge_set_length, motifs in motifs_by_original_length_dict.items():
        optimality_b_factors.extend(
            [(len(motif["graph"].nodes()), original_edge_set_length) for motif in motifs.values()])
    factor_nodes = get_stats_dict([nodes for nodes, _ in optimality_b_factors])
    factor_edges = get_stats_dict([edges for _, edges in optimality_b_factors])

    return [factor_nodes, factor_edges]
