from collections import defaultdict

import matplotlib.pyplot as plt
import pandas as pd

from utils import pickle_loader, topo_color, n_marker, topologies, get_all_x, tscpt_by_topo, graphics_dir

spmode = "all_volume_info"

fig, ax = plt.subplots(ncols=2, figsize=(10, 4.8))
xsubrange = dict()
xtickdict = defaultdict(lambda: {"ticks": [], "colors": []})
cutoff_x = {0: 15, 1: 100}  # 30
topo_of_interest = "wheel"
N_left = [5]
N_right = [16]  # 100
# 5, 10, 16, 100
# set gridlines
major_ticks = list(range(0, cutoff_x[0] + 1))
ax[0].set_xticks(major_ticks, minor=False)

for i, subax in enumerate(ax):
    subax.grid(True)
    subax.plot([0, cutoff_x[i]], [1 for _ in [0, cutoff_x[i]]], "-", color="C3", label="conventional public transport")
    subax.text(cutoff_x[i], y=0.98, s="$t_{s}^{cpt}$", fontsize=11, color="C3",
               ha='right', verticalalignment='top')

    subax.spines[["top", "right"]].set_visible(False)

for topology in topologies:
    graph_type, N = topology.split('_')
    N = int(N)
    stats = dict()

    colortop = topo_color(topology)
    nmarker = n_marker(N)

    xrange = get_all_x(topology, spmode, "calc_single_stats")
    tscpt = tscpt_by_topo(topology)

    if N in N_left:
        i = 0
    elif N in N_right:
        i = 1
    else:
        i = 2

    if i != 2:
        print(f"plot: {topology}, {tscpt}")
        axsub = ax[i]
        xsubrange[i] = [x for x in xrange if x <= cutoff_x[i]]
        for x in xsubrange[i]:
            pickle_path = f'./data/02_stats/{topology}_{spmode}_{str(x)}_calc_single_stats.dill'
            stats[str(x)] = pickle_loader(pickle_path)[2]
        stats_df = pd.DataFrame(stats)
        axsub.scatter(xsubrange[i], stats_df.loc["s_t_arr_50"] / tscpt, s=15, label=f"{graph_type}", marker=nmarker,
                      color=colortop)
        axsub.plot(xsubrange[i], stats_df.loc["s_t_arr_mean"] / tscpt, ":", color=colortop)

for subax in ax:
    subax.legend(loc="lower right")

ax[0].set_ylabel('normalized service-time $t_{s}\ /\ t_{s}^{cpt}$', fontsize=12)
ax[0].set_title(f"N: {N_left[0]}")

ax[0].set_xlabel('request rate $x$', fontsize=12)
ax[1].set_xlabel('request rate $x$', fontsize=12)
ax[1].set_title(f"N: {N_right[0]}")

fig.tight_layout()
plt.savefig(
    fr"{graphics_dir}\04b_st_over_x_multi_sim.png",
    dpi=300)
plt.show()
