import random
from multiprocessing import Pool

import networkx as nx

from _01_motifs import identify_motifs_wrapped
from _02_casestudy import case_study_motif_frequencies_wrapped
from _03_optimalities import optimality_without_motifs_wrapped
from utils import graph_constructor

# 0. set parameters
from utils import topologies, shortest_path_modes, get_all_x, casestudy_params


if __name__ == '__main__':
    for topology in topologies:
        base_net_graph = graph_constructor(topology)
        base_net_graph_shortest_paths = dict(nx.all_pairs_shortest_path_length(base_net_graph))
        base_net_graph_edges = set(tuple(sorted(edge)) for edge in base_net_graph.edges())
        for mode in shortest_path_modes:
            print(f"Topology: {topology}, Mode: {mode}")

            # Shuffle the list so we don't have small x values at the same time - they need some memory
            xrange = get_all_x(topology, mode, "calc_single_stats")
            random.shuffle(xrange)

            opt_args = ((x, topology, mode, base_net_graph_edges, base_net_graph_shortest_paths) for x in xrange)

            with Pool() as pool:
                print("Pool opened for worker splash party.")
                pool.starmap(optimality_without_motifs_wrapped, opt_args)
            print("Pool closed.")

            # case-study stats
            if topology in casestudy_params["topologies"].keys():
                casestudyxrange = [x for x in casestudy_params["topologies"][topology] if x in xrange] # make sure we do have stats for entire range
                if casestudy_params["topologies"][topology] != casestudyxrange:
                    print(f"Didn't find all x for casestudy_xrange in available x (from stats). Missing x: {casestudy_params['topologies'][topology]-casestudyxrange}")
                motif_args = ((x, topology, mode, base_net_graph_edges) for x in casestudyxrange)
                with Pool() as pool:
                    print("Pool 2 opened for worker splash party.")
                    pool.starmap(identify_motifs_wrapped, motif_args)
                print("Pool 2 closed.")

                # dist-plot params
                max_len_sorted_motifs = casestudy_params["max_len_sorted_motifs"]
                xlist = casestudyxrange
                motiffrequencydict = case_study_motif_frequencies_wrapped(topology, xlist, mode, max_len_sorted_motifs)


        #   ## BACKLOG
        #     pickle_path_walk = f'./data/graphs/{topology}_{mode}_x_{str(float(x))}_nreq_{n_reqs}_graph_walk.pkl'
        #     routespace_walk = pickle_loader(pickle_path_walk)
        #     print("Walk loaded.")
        #
        #     # visualize_3d_spacewalk(G, wheel_5_base_net)
        #     # visualize_3d_spacewalk_new(G, wheel_5_base_net)
        #
        #     # Insertion probability after n requests - wie viele nodes (also noch nie beobachtete Routen) kommen nach ...
        #     # requests noch dazu?
        #     plot_new_nodes_share(routespace_walk)
        #
        #     # 3. generate insights
        #     graph_stats = dict()
        #     print(f"Graph descriptives: \n Nodes: {G.number_of_nodes()} \n Edges: {G.number_of_edges()}")
        #
        #     in_degrees_dict = G.in_degree()
        #     indegrees = [deg for _, deg in in_degrees_dict]
        #
        #     # Nodes that have been visited more than once
        #     repeatedly_visited_nodes = [node for node, deg in in_degrees_dict if deg > 1]
        #
        #     # Calculate the cycle lengths
        #     cycle_lengths = [visit - G.nodes[node]["visits"][j - 1]
        #                      for i, node in enumerate(repeatedly_visited_nodes)
        #                      for j, visit in enumerate(G.nodes[node]["visits"][1:])]
        #
        #     # 5. save graph
        #     graph_stats["cycle_lengths"] = get_stats_dict(cycle_lengths)
        #     print("Cycle lengths stats: ", graph_stats["cycle_lengths"])
        #     del cycle_lengths
        #
        #     graph_stats["indegrees"] = get_stats_dict(indegrees, freq_counts=True)
        #     print("Indegree stats: ", graph_stats["indegrees"])
        #     del indegrees
        #
        #     minwalklength = graph_stats["cycle_lengths"]["percentiles"]["5"]
        #     maxwalklength = graph_stats["cycle_lengths"]["percentiles"]["25"]
