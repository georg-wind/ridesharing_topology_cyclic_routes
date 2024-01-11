import numpy as np
import random

from simulator import Request


def req_generator_uniform(graph, num_reqs, req_rate, topology, anchoring=False):
    """
    Generates requests with rate=req_rate whose origin and
    destination are drawn uniformly randomly. The requests
    are generated in time as a Poisson process.
    """
    t = 0
    req_idx = 0
    nodes = list(graph)
    graph_type, N = topology.split('_')
    N = int(N)

    if not anchoring:
        while req_idx < num_reqs:
            orig, dest = random.sample(nodes, k=2)
            delta_t = np.random.exponential(1 / req_rate)

            if req_idx == 0:  # we put the first request at t=0 - makes reading and controlling the data much easier when 
                # travel times are always integer times until the end of the simulation
                delta_t = 0
            t += delta_t
            req_idx += 1
            yield Request(req_idx, t, orig, dest)

    # route-anchoring is only defined for wheel graphs and for grid
    elif graph_type == "wheel":
        route_order = list(range(N))
        while req_idx < num_reqs:
            if req_idx < 100:
                orig = route_order[req_idx % N]
                dest = route_order[(req_idx + 1) % N]
                delta_t = np.random.exponential(1 / req_rate)
            else:
                orig, dest = random.sample(nodes, k=2)
                delta_t = np.random.exponential(1 / req_rate)

            if req_idx == 0:  # we put the first request at t=0 - makes reading and controlling the data much easier when
                # travel times are always integer times until the end of the simulation
                delta_t = 0

            t += delta_t
            req_idx += 1
            yield Request(req_idx, t, orig, dest)
    elif graph_type == "grid" and ((N % 2) == 0):
        while req_idx < num_reqs:
            if req_idx < 100:
                # requests still on the stoplist
                # then we need to add requests that will lead to the algorithm scheduling
                # a perfect route - this would not necessarily require requesting all nodes
                # but it is easier and safer to implement it this way

                # calculating the shortest path visiting all nodes is NP-hard, so we use our knowledge about the topology to
                # hard-code the shortest path
                # NB: this only works for grids with an even number of nodes per side yet.
                grid_dims = int(np.sqrt(N))
                # moving along the first row of the grid
                if (req_idx + 2) <= grid_dims:  # 2, 3, 4
                    orig = (1, req_idx + 1)
                    dest = (1, req_idx + 2)
                # moving down the last column of the grid
                if grid_dims < (req_idx + 2) < (2 * grid_dims):  # 5, 6, 7
                    orig = (req_idx + 2 - grid_dims, grid_dims)
                    dest = (req_idx + 3 - grid_dims, grid_dims)
                # moving backwards along the last row of the grid
                if (2 * grid_dims) <= (req_idx + 2) < (3 * grid_dims - 2):  # 8, 9, 10
                    orig = (grid_dims, 3 * grid_dims - req_idx - 2)
                    dest = (grid_dims, 3 * grid_dims - req_idx - 3)

                # snake back up the grid
                if (3 * grid_dims - 1) <= (req_idx + 2) < N:  # 11, 12, 13, 14, 15, 16
                    snake_position_in_loop = (req_idx + 2 - (3 * grid_dims - 1)) % (2 * (grid_dims - 1))
                    # let's first determine in which loop we are
                    repetition = int((req_idx + 2 - (3 * grid_dims - 1)) / (2 * (grid_dims - 1)))

                    # moving up
                    if snake_position_in_loop == 0:  # at the beginning of the loop, move one up
                        orig = (grid_dims - 2 * repetition, 1)
                        dest = (grid_dims - 2 * repetition - 1, 1)
                    # moving right
                    if 0 < snake_position_in_loop < (grid_dims - 1):
                        orig = (grid_dims - 2 * repetition - 1, snake_position_in_loop)
                        dest = (grid_dims - 2 * repetition - 1, snake_position_in_loop + 1)
                    # moving up
                    if snake_position_in_loop == (grid_dims - 1):
                        orig = (grid_dims - 2 * repetition - 1, grid_dims - 1)
                        dest = (grid_dims - 2 * repetition - 2, grid_dims - 1)
                    # moving left
                    if snake_position_in_loop > (grid_dims - 1):
                        orig = (grid_dims - 2 * repetition - 2, grid_dims - (snake_position_in_loop - grid_dims) - 1)
                        dest = (grid_dims - 2 * repetition - 2, grid_dims - (snake_position_in_loop - grid_dims) - 2)

                if req_idx == N - 2:  # 17
                    orig = (2, 1)
                    dest = (1, 1)

                # FIX: noticed only now, that nx starts counting at zero - nvm
                orig = (orig[0] - 1, orig[1] - 1)
                dest = (dest[0] - 1, dest[1] - 1)

                delta_t = np.random.exponential(1 / req_rate)



            else:
                orig, dest = random.sample(nodes, k=2)
                delta_t = np.random.exponential(1 / req_rate)

            if req_idx == 0:  # we put the first request at t=0 - makes reading and controlling the data much easier when 
                # travel times are always integer times until the end of the simulation
                delta_t = 0

            t += delta_t
            req_idx += 1
            yield Request(req_idx, t, orig, dest)
