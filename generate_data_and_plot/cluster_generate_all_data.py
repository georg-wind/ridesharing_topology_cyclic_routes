"""
A refactored version of `generate_allo_data.py`, suitable for using in
a HPC cluster with a queuing system. See the accompanying `submit_jobs_slurm.py`
for performing the computation in a slurm queuing system equipped HPC cluster.
"""
import os
import pathlib
import networkx as nx
from generate_all_data import simulate_single_request_rate
import sys
import pickle
from collections import defaultdict

from toysimulations import Network

def simulate_and_write_to_disk_single_request_rate(G, pickle_basepath, request_rate,
        network_type='novolcomp'):
    pickle_path = os.path.join(pickle_basepath, f"{request_rate}.pkl")
    if os.path.exists(pickle_path):
        print("pickle exists, doing nothing")
        return None

    nG = Network(G, network_type=network_type)
    l_avg = nx.average_shortest_path_length(G)
    req_data, ins_data = simulate_single_request_rate(G, nG, request_rate, 
            network_type, l_avg)

    result = defaultdict(lambda :dict())
    result[request_rate]['req_data'] = req_data
    result[request_rate]['insertion_data'] = ins_data

    picklable_res = {key: dict(val) for key, val in result.items()}
    with open(pickle_path, 'wb') as f:
        pickle.dump(picklable_res, f)


path_prefix = pathlib.Path('../data')
if not path_prefix.is_dir():
    path_prefix.mkdir()

def setup_graph(graph_name):
    pickle_basepath = path_prefix.joinpath(graph_name)
    if not pickle_basepath.is_dir():
        pickle_basepath.mkdir()
    if graph_name == 'ring_10':
        G = nx.cycle_graph(10)
        network_type = 'ring'
    elif graph_name == 'ring_100':
        G = nx.cycle_graph(100)
        network_type = 'ring'
    elif graph_name == 'line_100':
        G = nx.grid_graph((100,))
        network_type = 'line'
    elif graph_name == 'star_100':
        G = nx.star_graph(n=100)
        network_type = 'star'
    elif graph_name == 'grid_10':
        G = nx.grid_2d_graph(10, 10)
        network_type = 'grid'
    elif graph_name == 'trigrid_13':
        G = nx.lattice.triangular_lattice_graph(13, 13)
        network_type = 'trigrid'
    elif graph_name == 'street_goe_homogenized':
        graph_path = '../data/homogenized_networks/goe/'
        G = nx.read_gpickle(f"{graph_path}/G_homog.gpkl")
        network_type = 'novolcomp'
    elif graph_name == 'street_harz_homogenized':
        graph_path = '../data/homogenized_networks/harz/'
        G = nx.read_gpickle(f"{graph_path}/G_homog.gpkl")
        network_type = 'novolcomp'
    elif graph_name == 'street_berlin_homogenized':
        graph_path = '../data/homogenized_networks/berlin/'
        G = nx.read_gpickle(f"{graph_path}/G_homog.gpkl")
        network_type = 'novolcomp'
    elif graph_name.startswith("street_berlin_homogenized_coarse_graining_meters_"):
        fname_parts = graph_name.split('_')
        coarse_graining_meters = int(fname_parts[6])
        target_edge_length = int(fname_parts[10])

        graph_path = '../data/homogenized_networks/berlin/'

        with open(f"{graph_path}/diff_coarse_graining/all_berlin.pkl", 'rb') as f:
            all_Gs = pickle.load(f)

        _,G = all_Gs[coarse_graining_meters][target_edge_length]
        network_type = 'novolcomp'

    return G, pickle_basepath, network_type

if __name__ == '__main__':
    graph_name = sys.argv[1]
    req_rate = float(sys.argv[2])

    print(f"Simulating {graph_name} network for request rate {req_rate}")
    G, pickle_basepath, network_type = setup_graph(graph_name)
    simulate_and_write_to_disk_single_request_rate(G, pickle_basepath, req_rate,
        network_type)
