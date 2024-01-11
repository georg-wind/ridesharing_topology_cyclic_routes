from create_figures import create_figures
from utils import topologies, shortest_path_modes, xrange, numreqs

if __name__ == '__main__':
    print("Creating figures.")
    for topology in topologies:
        for spmode in shortest_path_modes:
            print(f"{topology}_{spmode}")
            create_figures(topology=topology, mode=spmode, x_range=xrange, n_reqs=numreqs)
