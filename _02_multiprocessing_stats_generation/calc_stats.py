import bisect

import numpy as np

from rolling_mean_servicetime import rolling_mean_servicetime
from stoplists_and_route_lengths import stoplists_and_node_visit_frequencies_optimized
from utils import run_or_get_pickle, pickle_loader, tscpt_by_topo


def calc_single_stats(x, topology, mode, chunk_size):
    PICKLE_FILE = f'./data/01_simulations/{topology}_{mode}_{str(x)}_simulate_single_request_rate.dill'
    try:
        result = pickle_loader(PICKLE_FILE)
    except Exception as e:
        print(f"Got exception trying to load {PICKLE_FILE}.")
        raise e

    req_data = result[0]
    insertion_data = result[1]
    print(f"Simulation data for x = {x}. loaded. Calculating statistics.")

    # Compute statistics for insertion_data
    stoplist_lens = [item[1] for item in insertion_data]
    stoplist_volumes = [item[2] for item in insertion_data]
    rest_stoplist_volumes = [item[3] for item in insertion_data]

    x_stats = {
        "n_arr": np.mean(stoplist_lens),
        "route_vol_arr": np.mean(stoplist_volumes),
        "rest_route_vol_arr": np.mean(rest_stoplist_volumes)
    }
    # tscpt_by_topology = tscpt_by_topo(topology)
    # Compute statistics for req_data
    service_times = [item['dropoff_epoch'] - item['req_epoch'] for item in req_data.values()]
    x_stats["s_t_arr_25"], x_stats["s_t_arr_50"], x_stats["s_t_arr_75"] = np.percentile(service_times, (25, 50, 75))
    x_stats["s_t_arr_mean"] = np.mean(service_times)
    x_stats["s_t_arr_std"] = np.std(service_times)

    # stmean = x_stats["s_t_arr_mean"]
    # print(f"\n{topology}, x={x}, mean st = {stmean}: tscpt =  {tscpt_by_topology}\n\n")

    # node-visit-dict AND stoplist-lengths-over-reqs
    node_visits_dict, stoplist_lengths_over_reqs, unique_scheduled_stops_over_reqs = stoplists_and_node_visit_frequencies_optimized(
        req_data)

    x_stats["mean_unique_stoplist_length"] = np.mean(unique_scheduled_stops_over_reqs)

    # compute [mean, SD] of delta t between visits for each node at request rate x
    node_visits_delta = {node: np.subtract(visits[1:], visits[:-1]) for node, visits in node_visits_dict.items()}
    node_visit_frequency = {k: [np.power(np.mean(v[1:]), -1), np.power(np.std(v[1:]), -1)] for k, v in
                            node_visits_delta.items()}

    # calculating the mean and SD for all nodes of the mean of frequency of visits of each node at request rate x
    node_visit_frequency_means = [i[0] for i in node_visit_frequency.values()]
    node_visit_frequency_sds = [i[1] for i in node_visit_frequency.values()]

    (x_stats["node_visit_frequency_arr_25"], x_stats["node_visit_frequency_arr_50"],
     x_stats["node_visit_frequency_arr_75"]) = np.percentile(node_visit_frequency_means, (25, 50, 75))
    x_stats["node_visit_frequency_arr_mean"] = np.mean(node_visit_frequency_means)
    x_stats["node_visit_frequency_arr_std"] = np.std(node_visit_frequency_means)

    x_stats["node_visit_frequency_arr_mean_of_individual_stds"] = np.mean(node_visit_frequency_sds)
    x_stats["node_visit_frequency_arr_std_of_individual_stds"] = np.std(node_visit_frequency_sds)

    # create the route driven and the visit times.
    visit_list = [(node, visit) for node, visits in node_visits_dict.items() for visit in visits]
    visit_list.sort(key=lambda n: n[1])
    route, visits = zip(*visit_list)

    # resulting route_lengths - evaluated at each stop as opposed to at each request
    # (this drastically shortens the array since we usually have much more requests than stops)
    current_route_lengths = []
    req_epochs = [item["req_epoch"] for item in req_data.values()]

    for visit in visits:
        index = bisect.bisect_right(req_epochs, visit)
        if index > 0:
            current_route_lengths.append(stoplist_lengths_over_reqs[index - 1])
        else:
            current_route_lengths.append(0)

    print(f"Calculating 3D-statistics for x = {x}.")
    rollingmeanservicetime = rolling_mean_servicetime(req_data, chunk_size)

    return route, current_route_lengths, x_stats, rollingmeanservicetime


def calc_single_stats_wrapped(x, topology, spm, chunk_size):
    unique_id = f'{topology}_{spm}_{str(x)}'
    wrapped_function = run_or_get_pickle(unique_id, "02_stats")(calc_single_stats)
    return wrapped_function(x, topology, spm, chunk_size)
