import matplotlib.pyplot as plt

from utils import pickle_loader, get_all_x, graphics_dir, tscpt_by_topo

spmode = "all_volume_info"
topology = "grid_16"
servicetimes = dict()
chunk_size = 10 ^ 3
graph_type, N = topology.split('_')

xrange = get_all_x(topology, spmode, "calc_single_stats")
for index in (100, 60, 30, 18, 12, 8, 6, 4, 2, 1, 0):
    x = xrange[index]
    pickle_path = f'./data/02_stats/{topology}_{spmode}_{str(x)}_calc_single_stats.dill'
    servicetimes[str(x)] = pickle_loader(pickle_path)[3]

nreqs = len(servicetimes["0.1"])
tscpt = tscpt_by_topo(topology)

fig, ax = plt.subplots()
ax.grid(True)
ax.spines[["top", "right"]].set_visible(False)

for x in servicetimes.keys():
    ax.plot(list(range(0, nreqs * 10 ** 2, 10 ** 2)), servicetimes[x], label=f"x: {float(x):.2f}")

ax.set_xlabel("requests ordered by generation", size=12)
ax.set_ylabel(f"rolling-mean service-time over {10 ** 3} requests", size=12)
ax.set_title(f"{graph_type}-{N}", size=12)
ax.legend(loc="lower right")
fig.tight_layout()
plt.savefig(
    fr"{graphics_dir}\08st_vs_x_vs_req.png",
    dpi=300)
plt.show()
