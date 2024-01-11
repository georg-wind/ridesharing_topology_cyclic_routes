import matplotlib
import numpy as np
import pandas as pd

from _04_stats_visualisation import create_figure1, create_figure3, create_figure5, create_figure6
from utils import pickle_loader, get_all_x

matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['figure.figsize'] = [8, 6.4]


def create_figures(topology, mode, x_range, n_reqs):
    print("Stats pickle loaded.")
    stats = dict()
    for x in x_range:
        pickle_path = f'./data/02_stats/{topology}_{mode}_{str(x)}_calc_single_stats.dill'
        stats[str(x)] = pickle_loader(pickle_path)[2]

    stats_df = pd.DataFrame(stats)

    create_figure1(x_range, topology, mode, n_reqs, stats_df)
    # create_figure2(x_arr, topology, mode, n_reqs, stats_df)
    create_figure3(x_range, topology, mode, n_reqs, stats_df)
    # create_figure4(topology, mode, x_range, n_reqs, output_dir='./data/plots', data_dir='./data/stats')
    # create_figure5(service_time, topology, mode, x_range, n_reqs)

    data = dict()
    for x in x_range:
        pickle_path = f'./data/03_optimalities/{topology}_{mode}_{str(x)}_optimality_without_motifs.dill'
        optimality_a, optimality_b = pickle_loader(pickle_path)
        data[x] = {"opt_a": optimality_a["mean"],
                   "opt_b_nodes_mean": optimality_b["nodes"]["mean"],
                   "opt_b_nodes_std": optimality_b["nodes"]["std"],
                   "opt_b_edges_mean": optimality_b["edges"]["mean"],
                   "opt_b_edges_std": optimality_b["edges"]["std"]}

    # Create DataFrame
    opt_df = pd.DataFrame(data)
    opt_df.index = ["opt_a",
                    "opt_b_nodes_mean",
                    "opt_b_nodes_std",
                    "opt_b_edges_mean",
                    "opt_b_edges_std"]

    # @run_or_getpickle(...)
    create_figure6(x_range, topology, mode, n_reqs, stats_df, opt_df)

