import matplotlib.pyplot as plt
import pandas as pd

from utils import pickle_loader, topo_color, n_marker, get_all_x, graphics_dir

# ordering if normalized by N
topologies = ["star_10", "wheel_5", "wheel_10", "grid_16", "cycle_10", "line_10", "grid_100"]

spmode = "all_volume_info"

####### FIGURE 1 #######
fig, ax = plt.subplots(figsize=(6.4, 3.8))
# plt.subplots_adjust(hspace=0.1)
ax.set_xlabel('request rate $x$', fontsize=10)
ax.set_ylabel('normalized stop-list length $n / N$', fontsize=10)

# Create custom legend entries
unique_N_values = set()  # To track and add unique N values only

for topology in topologies:
    print(f"{topology}")
    stats = dict()
    xrange = get_all_x(topology, spmode, "calc_single_stats")
    xrange = [x for x in xrange if x <= 10]
    for x in xrange:
        pickle_path = f'./data/02_stats/{topology}_{spmode}_{str(x)}_calc_single_stats.dill'
        stats[str(x)] = pickle_loader(pickle_path)[2]

    stats_df = pd.DataFrame(stats)

    graph_type, N = topology.split('_')
    topocolor = topo_color(topology)
    ax.grid(True)

    # # 2. Stop-list length
    ax.plot(xrange, stats_df.loc["n_arr"] / int(N), ":", label=f"{graph_type}, N = {N}", color=topocolor)
    if topology in ["line_10", "cycle_10"]:
        ax.text(xrange[-1] + 0.2, stats_df.loc["n_arr"][-1] / int(N) - 0.1, f"{graph_type}",
                fontsize=10, color=topocolor, ha='left', verticalalignment='bottom')
    else:
        ax.text(xrange[-1] + 0.2, stats_df.loc["n_arr"][-1] / int(N), f"{graph_type}",
                fontsize=10, color=topocolor, ha='left', verticalalignment='bottom')

    nmarker = n_marker(N)
    ax.scatter(xrange, stats_df.loc["n_arr"] / int(N), s=15, color=topocolor, marker=nmarker)
    unique_N_values.add(int(N))

legend_entries = []
# Add custom legend to the plot
for N in sorted(list(unique_N_values)):
    marker = n_marker(N)
    entry = plt.Line2D([0], [0], color='w', marker=marker, markerfacecolor='black', label=f'N = {N}', markersize=8)
    legend_entries.append(entry)

ax.legend(handles=legend_entries, loc='upper left')

# Hide the default legend
# ax.legend().set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xticks(list(range(0, 11)))
fig.tight_layout()
plt.savefig(
    fr"{graphics_dir}\03_replicated_ManMol_results.png",
    dpi=300)
plt.show()
