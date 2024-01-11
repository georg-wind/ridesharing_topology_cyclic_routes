from pool_generate_all_data import simulate_different_request_rates
from utils import graph_constructor
from utils import topologies, shortest_path_modes, xrange, numreqs

if __name__ == '__main__':

    for topology in topologies:
        for spm in shortest_path_modes:
            if spm != "all_volume_info" and any(topology_with_unique_shortest_paths in topology
                                                for topology_with_unique_shortest_paths in ('cycle', 'line', 'star')):
                continue

            print(f"Simulating {topology} with {spm} shortest-path-mode.")
            G = graph_constructor(topology)
            simulate_different_request_rates(G, topology=topology, shortestpathmode=spm,
                                             xrange=xrange, num_reqs=numreqs)
            print(f"Simulation for {topology} with {spm} shortest-path-mode completed.")
