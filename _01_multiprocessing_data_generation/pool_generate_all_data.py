import random
from multiprocessing import Pool

import networkx as nx
import numpy as np

from req_generator import req_generator_uniform
from simulator import ZeroDetourBus, Network, FixedRouteBus
from utils import run_or_get_pickle


def simulate_different_request_rates(G, shortestpathmode, topology, xrange, num_reqs):
    G.shortest_path_mode = shortestpathmode
    nG = Network(G, network_type=topology, shortest_path_mode=shortestpathmode)
    l_avg = nx.average_shortest_path_length(G)

    req_args = ((G, nG, x, topology, shortestpathmode, l_avg, num_reqs) for x in
                xrange)  # generator expression to bundle vars

    with Pool() as pool:
        print("pool opened for worker splash party")
        # call the same function with different data in parallel
        pool.starmap(simulate_single_request_rate_wrapped, req_args)


def simulate_single_request_rate_wrapped(G, nG, x, topology, spm, l_avg, num_reqs):
    unique_id = f'{topology}_{spm}_{str(x)}'
    wrapped_function = run_or_get_pickle(unique_id, "01_simulations")(simulate_single_request_rate)
    return wrapped_function(G, nG, x, topology, l_avg, num_reqs)


def simulate_single_request_rate(G, nG, x, topology, l_avg, num_reqs):
    """
    Simulates only as single request rate x. See the docstring of
    `simulate_different_request_rates` for details on the arguments.
    """
    req_rate = x / (2 * l_avg)
    sim = ZeroDetourBus(nG,
                        req_generator_uniform(G, num_reqs, req_rate, topology, anchoring=False),
                        topology,
                        random.sample(list(G), k=1)[0]
                        )
    ## we checked the "fixed route bus" (aka conventional public transport) as a sanity check
    # sim = FixedRouteBus(nG,
    #                     req_generator_uniform(G, num_reqs, req_rate),
    #                     network_type,
    #                     random.sample(list(G), k=1)[0]
    #                     )
    print(f"simulating x={x}")
    sim.simulate_all_requests()
    return sim.req_data, sim.insertion_data
