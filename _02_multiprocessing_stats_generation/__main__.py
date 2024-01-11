from multiprocessing import Pool



from _02_multiprocessing_stats_generation.calc_stats import calc_single_stats_wrapped
## importing variables
from utils import topologies, shortest_path_modes, numreqs, get_all_x

if __name__ == '__main__':
    rolling_window_size = numreqs // (10 ** 2)

    for topology in topologies:
        for mode in shortest_path_modes:
            xrange = get_all_x(topology, mode, "simulate_single_request_rate")
            print(f"Calculating statistics over all x on {topology} from simulation with {mode}.")
            stat_args = ((str(x), topology, mode, rolling_window_size) for x in xrange)
            with Pool() as pool:
                print("pool opened for worker splash party")
                pool.starmap(calc_single_stats_wrapped, stat_args)
