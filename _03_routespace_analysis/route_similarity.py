import numpy as np
from scipy.stats import norm
from utils import get_stats_dict
from tqdm import tqdm

def lev_distance(s1, s2):
    if len(s1) < len(s2):
        s1, s2 = s2, s1

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    # returning the normalized distance
    return previous_row[-1] / min(len(s1), len(s2))


def equal_lengths_walk_similarity(walk1, walk2):
    """calculate the similarity between two walks over many routes"""
    total_distance = sum(lev_distance(w1, w2) for w1, w2 in zip(walk1, walk2))
    return total_distance / len(walk1)


def equal_lengths_walk_similarities(many_walks):
    return [equal_lengths_walk_similarity(i, j) for i in many_walks for j in many_walks if i != j]


def cyclic_walks(graph, node, min_walk_length, max_walk_length):
    all_possible_cyclic_walks = graph.get_all_simple_paths(v=node, to=node, cutoff=max_walk_length, mode="out")
    if len(all_possible_cyclic_walks) == 0:
        print(f"No cyclic walks up to length {max_walk_length} found for node {node.index}.")

    # Filter paths based on length and organize them in a dictionary
    path_dict = {}
    for path in all_possible_cyclic_walks:
        length = len(path) - 1  # subtract 1 because path length = number of vertices - 1
        if min_walk_length <= length <= max_walk_length:
            if length not in path_dict:
                path_dict[length] = []
            path_dict[length].append(path)

    return path_dict


def generate_walklengths_stats_dict(g, min_walk_length, max_walk_length):
    pbar = tqdm(g.vs)
    c_message = "Got all cyclic walks. Calculating similarities."
    for node in pbar:
        pbar.set_description(f"Processing node {node.index}")
        node["walklengths_dict"] = {}
        # generate all possible cyclic walks for this node   
        all_possible_cyclic_walks = cyclic_walks(g, node, min_walk_length, max_walk_length)
        pbar.set_postfix(custom_message=c_message, another_message="Static Info")
        for length in all_possible_cyclic_walks.keys():
            walk_similarities = equal_lengths_walk_similarities(all_possible_cyclic_walks[length])
            node["walklengths_dict"][length] = get_stats_dict(walk_similarities)


def calc_combined_stats(g):
    """calculate the combined distributional stats for all nodes i which have been visited repeatedly with the same
    cycle-length j. The dictionary is stored as a property of the graph."""
    g.graph["walklengths_dict"] = {}
    cycle_stats_dict = {"mean": 0, "std": 0, "min": 0, "max": 0, "median": 0, "count": 0, "nodes": []}
    for node in g.vs:
        node_cycle_stats_dict = node["walklengths_dict"]
        for cycle_length in node_cycle_stats_dict.keys():
            if not cycle_length in g.graph["walklengths_dict"].keys():
                g.graph["walklengths_dict"][cycle_length] = cycle_stats_dict.copy()
            g.graph["walklengths_dict"][cycle_length]["nodes"].append(node.index)
            g.graph["walklengths_dict"][cycle_length]["count"] += node_cycle_stats_dict[cycle_length]["count"]
            # step 1/2 mean-calculation
            g.graph["walklengths_dict"][cycle_length]["mean"] += node_cycle_stats_dict[cycle_length]["mean"] * \
                                                                 node_cycle_stats_dict[cycle_length]["count"]

            # storing some additional values which we can only use in calculation later
            g.graph["walklengths_dict"][cycle_length]["ind_means"] = node_cycle_stats_dict[cycle_length]["mean"]
            g.graph["walklengths_dict"][cycle_length]["ind_stds"] = node_cycle_stats_dict[cycle_length]["std"]
            g.graph["walklengths_dict"][cycle_length]["ind_counts"] = node_cycle_stats_dict[cycle_length]["count"]

    # step 2/2 mean-calculation
    for cycle_length in g.graph["walklengths_dict"].keys():
        g.graph["walklengths_dict"][cycle_length]["mean"] /= g.graph["walklengths_dict"][cycle_length]["count"]

        # SD calculation
        g.graph["walklengths_dict"][cycle_length]["std"] = ((sum(
            (count - 1) * (g.graph["walklengths_dict"][cycle_length]["ind_stds"][i] ** 2)
            +
            count * (g.graph["walklengths_dict"][cycle_length]["ind_means"][i] -
                     g.graph["walklengths_dict"][cycle_length]["mean"]) ** 2
            for i, count in enumerate(g.graph["walklengths_dict"][cycle_length]["ind_counts"])) / (
                                                                     sum(g.graph["walklengths_dict"][cycle_length][
                                                                             "ind_counts"]) -
                                                                     len(g.graph["walklengths_dict"][cycle_length][
                                                                             "nodes"])))
                                                            ** 0.5)


def cycle_similarity(g, min_walk_length=4, max_walk_length=15, routespace_walk=None):
    generate_walklengths_stats_dict(g, min_walk_length, max_walk_length)
    calc_combined_stats(g)

    pvals = dict()
    for node in g.vs:
        visits = node["visits"]
        vid = node.index
        pvals[vid] = dict()
        cyclelengths = [visits[i] - visits[i - 1] for i in range(1, len(visits))]
        repeated_cycle_lengths = set([length for length in cyclelengths if cyclelengths.count(length) > 1])
        # create a dictionary indicating which cycle lenghts were observed repeatedly and which cycles had this length
        node["repeated_cyclelengths"] = {i: [j for j, length in enumerate(cyclelengths) if length == i] for i in
                                         repeated_cycle_lengths}
        for j in repeated_cycle_lengths:
            base_distribution = g.graph["walklengths_dict"][j]
            base_mean = base_distribution["mean"]
            base_std = base_distribution["std"]

            cycles_j = node["repeated_cyclelengths"][j]
            visits_j = [(visits[walk], visits[walk + 1]) for walk in cycles_j]
            cycles_j_routespace_walks = [routespace_walk[start:end] for (start, end) in visits_j]
            # calculate the similarity of the walks of length j
            walk_similarities = equal_lengths_walk_similarities(cycles_j_routespace_walks)

            # determine the p-value of the observed walks
            pvals[vid][j] = [p_val(similarity, base_mean, base_std) for similarity in walk_similarities]

    return pvals


def p_val(x, mean, std):
    """
    Compute the value of the standard normal distribution at x standard deviations.
    
    Parameters:
    - x: Number of standard deviations from the mean (0 for standard normal).
    
    Returns:
    - Value of the standard normal distribution's PDF at x.
    """
    if x > mean:
        deviations = (x - mean) / std
    else:
        deviations = (mean - x) / std
    return 1 - norm.cdf(deviations)
