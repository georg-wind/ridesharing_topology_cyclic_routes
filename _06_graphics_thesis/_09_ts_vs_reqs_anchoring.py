import matplotlib.pyplot as plt

from utils import pickle_loader, get_all_x, tscpt_by_topo, casestudy_params, graphics_dir

# Note: for this graphics, the simulation data and stats data has to be regenerated for the respective topology, using the req-generator with "anchoring=True"
spmode = "all_volume_info"
topology = "wheel_5"
servicetimes = dict()
graph_type, N = topology.split('_')

xrange = get_all_x(topology, spmode, "calc_single_stats")
xlist = casestudy_params["topologies"][topology]

for x in xlist[::-1]:
    pickle_path = f'./data/02_stats/{topology}_{spmode}_{str(x)}_calc_single_stats.dill'
    servicetimes[str(x)] = pickle_loader(pickle_path)[3]

tscpt = tscpt_by_topo(topology)

fig, ax = plt.subplots()
ax.grid(True)
ax.spines[["top", "right"]].set_visible(False)

for x in servicetimes.keys():
    ax.plot(list(range(0, 400)), servicetimes[x][:400], label=f"x: {float(x):.2f}")

ax.set_xlabel("requests ordered by generation time", size=12)
ax.set_ylabel(f"service-time over requests", size=12)
ax.set_title(f"{graph_type}-{N}", size=12)
ax.legend(loc="lower right")
fig.tight_layout()
plt.savefig(
    fr"{graphics_dir}\09st_vs_req_anchoring.png",
    dpi=300)
plt.show()
