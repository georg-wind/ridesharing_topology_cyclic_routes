import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np

from utils import pickle_loader, topo_color, n_marker, get_all_x, graph_constructor, graphics_dir
from utils.tscpt import tscpt_by_topo


def get_crossing(xarr, stats_arr, tscpt):
    for i in range(len(stats_arr)):
        if stats_arr[i] > tscpt:
            x_area = xarr[i - 1:i + 1]
            rel_diff = 1 - (stats_arr[i] - tscpt) / (stats_arr[i] - stats_arr[i - 1])
            x_cross = x_area[0] + (x_area[1] - x_area[0]) * rel_diff
            return x_cross


spmode = "all_volume_info"
topologies_of_interest = {
    "grid_9": {0: 20, 1: 100},
    "wheel_10": {0: 15, 1: 750},
    "grid_16": {0: 20, 1: 1000},
    "cycle_10": {0: 10, 1: 100},
    "line_10": {0: 10, 1: 50},
    "star_10": {0: 10, 1: 100}
}

for topology in topologies_of_interest.keys():

    cutoff_x = topologies_of_interest[topology]
    graph_type, N = topology.split('_')
    N = int(N)

    xsubrange = dict()
    fig, axs = plt.subplots(ncols=2, figsize=(10, 4.8))

    for i in range(2):
        critical_x = [1.0]
        ax = axs[i]

        # set gridlines
        step = 1 if i == 0 else cutoff_x[1] // 10
        major_ticks = list(range(0, int(cutoff_x[i] + 1), step))  # + [x for x in range(cutoff_x[i] + 1) if x % 5 == 0]
        ax.set_xlim(0, cutoff_x[i])
        ax.set_xticks(major_ticks, minor=False)
        ax.grid(True)

        tscpt_interest = tscpt_by_topo(topology)
        taxi = 2 * nx.average_shortest_path_length(graph_constructor(topology))
        ax.plot([0, cutoff_x[i]], [tscpt_interest for _ in [0, cutoff_x[i]]], "-", color="C3",
                label="conv. public transport")
        ax.text(cutoff_x[i], y=tscpt_interest - 0.02, s="$t_{s}^{cpt}$", fontsize=12, color="C3",
                ha='right', verticalalignment='top')
        ax.plot([0, cutoff_x[i]], [taxi for _ in [0, cutoff_x[i]]], "-", color="#f5d033",
                label="idle taxi")
        ax.text(cutoff_x[i] / 4, y=taxi - 0.02, s="$t_{s}^{taxi}$", fontsize=12, color="#f5d033",
                ha='left', verticalalignment='top')

        ax.spines[["top", "right"]].set_visible(False)

        stats = dict()
        colortop = topo_color(topology)
        nmarker = n_marker(N)

        xrange = get_all_x(topology, spmode, "calc_single_stats")
        tscpt = tscpt_by_topo(topology)

        print(f"Plotting {topology}, {tscpt}")
        xsubrange = [x for x in xrange if x <= cutoff_x[i] + 5]
        for x in xsubrange:
            pickle_path = f'./data/02_stats/{topology}_{spmode}_{str(x)}_calc_single_stats.dill'
            stats[str(x)] = pickle_loader(pickle_path)[2]
        stats_df = pd.DataFrame(stats)

        ax.plot(xsubrange, stats_df.loc["s_t_arr_mean"], ":", label="mean", color=colortop)
        ax.scatter(xsubrange, stats_df.loc["s_t_arr_50"], s=15, label="median", color=colortop)
        ax.fill_between(xsubrange, stats_df.loc["s_t_arr_25"], stats_df.loc["s_t_arr_75"],
                        alpha=0.2, label="25/75 percentiles", color=colortop)

        ax.plot(xsubrange, stats_df.loc["route_vol_arr"], ":", label="route-volume", color="purple")
        # ax.plot(xsubrange, stats_df.loc["rest_route_vol_arr"], ":", label="route-volume", color="pink")
        ax.set_xlabel('request rate $x$', fontsize=12)

        if i == 0:
            new_tick = get_crossing(xsubrange, stats_df.loc["s_t_arr_50"], tscpt)
            critical_x.append(new_tick)
            max_x = xsubrange[np.argmax(stats_df.loc["s_t_arr_50"][:50])]
            critical_x.append(max_x)
            critical_x = np.add(critical_x, -0.001) # if major and minor ticks are at the same location, the minor ticks are removed...
            labels = [f"$x_{i + 1}$" for i in range(3)]
            ax.set_xticks(critical_x, minor=True, color="red", labels=labels)
            ax.tick_params(axis="x", which="minor", direction="in", length=5, width=2, color="red", pad=-22, labelsize=12)

            ax.set_title(f"{graph_type}, N: {N}", loc="left")
            ax.set_ylabel('service-time $t_{s}$', fontsize=12)

    axs[1].legend(loc="lower right")

    fig.tight_layout()
    plt.savefig(
        fr"{graphics_dir}\04_st_over_x_multi_sim_{graph_type}_{N}.png",
        dpi=300)
    plt.show()
