import warnings
from functools import reduce
from itertools import tee
from math import ceil
from typing import List

import networkx as nx
import numpy as np

from utils import get_shortest_paths_and_volume
from tqdm import tqdm


def pairwise(iterable):
    """
    A pairwise iterator. Source:
    https://docs.python.org/3.8/library/itertools.html#itertools-recipes
    s -> (s0,s1), (s1,s2), (s2, s3), ...
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


class Stop(object):
    """
    A stop object, to be used in our simulations. Encodes a single stop.
    """

    def __init__(self, position, time, stop_type, req_id):
        self.position = position
        self.time = time
        self.stop_type = stop_type
        self.req_id = req_id

    def __repr__(self):
        return f"Stop(position={self.position}, time={self.time}, " \
               f"stop_type={self.stop_type}, req_id={self.req_id})"


class Request(object):
    """
    A request object, to be used in our simulations. Encodes a single request.
    """

    def __init__(self, req_id, req_epoch, origin, destination):
        self.req_id = req_id
        self.req_epoch = req_epoch
        self.origin = origin
        self.destination = destination

    def __repr__(self):
        return f"Request(req_id={self.req_id}, req_epoch={self.req_epoch}, " \
               f"origin={self.origin}, destination={self.destination})"


class Network(object):
    """
    A wrapper around nx.Graph. The idea is to  would override key methods
    to make simulations faster.
    """

    def __init__(self, G, network_type, shortest_path_mode='originalpaper'):
        """
        Args:
        -----
            G: Either a networkx.Graph or a Network object.
            network_type: A string. Used for smart route volume
                computations. If set to 'novolcomp', no route volume
                computation is performed.
        """
        self.network_type = network_type
        self.shortest_path_mode = shortest_path_mode
        self.all_path_info = None
        if isinstance(G, Network):
            # If a Network is passed, just copy relevant stuff.
            self._network = G._network
            self._all_shortest_paths = G._all_shortest_paths
            self.all_path_info = G.all_path_info
            self._all_shortest_path_lengths = G._all_shortest_path_lengths
            self.shortest_path_mode = G.shortest_path_mode
        else:
            self._network = nx.Graph(G)
            self._network.shortest_path_mode = shortest_path_mode
            # Cache all shortest paths
            if any(topology_with_unique_shortest_paths in self.network_type
                   for topology_with_unique_shortest_paths in ('cycle', 'line', 'star')):
                warnings.warn(
                    f"Warning: \"network_type\" is set to \"{network_type}\". Any shortest path will be the volume-optimal shortest path.")
                self._all_shortest_paths, _ = get_shortest_paths_and_volume(self._network, mode="originalpaper")
            elif self.network_type == "novolcomp" and shortest_path_mode == "all_volume_info":
                warnings.warn(
                    "Warning: \"shortest_path_mode\" is set to \"all_volume_info\" (dynamic mode), but \"network_type\" "
                    "is \"novolcomp\". Using \"static max\" shortest_path_mode instead.")
                self._all_shortest_paths, _ = get_shortest_paths_and_volume(self._network, mode="staticmax")
            else:
                self._all_shortest_paths, self.all_path_info = get_shortest_paths_and_volume(self._network,
                                                                                             mode=shortest_path_mode)
            self._all_shortest_path_lengths = dict(nx.all_pairs_shortest_path_length(self._network))

    def shortest_path_length(self, u, v, **kwargs):
        return self._all_shortest_path_lengths[u][v]

    def shortest_path(self, u, v, **kwargs):
        if self.shortest_path_mode == 'all_volume_info' and not any(
                topology_with_unique_shortest_paths in self.network_type
                for topology_with_unique_shortest_paths in
                ('cycle', 'line', 'star')):
            ## i.e. if we want to dynamically choose the volume-maximizing
            # shortest path depending on the already scheduled route AND it makes sense given the topology
            scheduled_route_vol = reduce(set.union, (self._all_shortest_paths[u.position][v.position][
                                                         "volume_set"] for u, v in
                                                     pairwise(kwargs["stoplist"])), set())
            volume_optimal_shortest_path_uv = []
            volume_value = -1
            for i in range(0, len(self._all_shortest_paths[u][v]["paths"])):
                if len(self._all_shortest_paths[u][v]["volume_set"] - scheduled_route_vol) > volume_value:
                    volume_optimal_shortest_path_uv = self._all_shortest_paths[u][v]["paths"][i]
                    volume_value = len(self._all_shortest_paths[u][v]["volume_set"] - scheduled_route_vol)
            return volume_optimal_shortest_path_uv
        else:
            return self._all_shortest_paths[u][v]

    def nodes_enroute(self, s, t):
        """
        Returns all the nodes that are on the route when one goes from
        s to t. Basically this is the set of all nodes in all
        shortest paths between s and t.
        """
        if any(topology_with_unique_shortest_paths in self.network_type
               for topology_with_unique_shortest_paths in ('cycle', 'line', 'star')):
            return set(self.shortest_path(s, t))
        elif self.network_type == 'novolcomp':
            # forcibly disable volume computation
            return set()
        else:
            return self.all_path_info[s][t]["volume_set"]

    def all_reachable_nodes_on_stoplist(self, stoplist) -> set:
        # this is a sped-up operation to get all nodes on the route between all pairs of stops in the stoplist
        checked_routes_directed = set()
        node_set = set()
        for u, v in pairwise(stoplist):
            u_pos, v_pos = u.position, v.position
            # since shortest-paths are symmetric, we only need to check each route once and direction doesnt matter
            u_pos, v_pos = sorted((u_pos, v_pos))
            if (u_pos, v_pos) not in checked_routes_directed:
                # add all nodes on the route from u to v that aren't already in the node_set
                nodes_on_route = self.nodes_enroute(u_pos, v_pos)
                node_set |= nodes_on_route

                # add the route to the set of checked routes
                checked_routes_directed.add(tuple((u_pos, v_pos)))
                # but also add all subroutes to the set of checked routes
                checked_routes_directed |= set(tuple(sorted((u_pos, w_pos))) for w_pos in nodes_on_route)
        return node_set


class ZeroDetourBus(object):
    """
    A simulator that simulates a single bus with no-detour policy.
    Any network can be chosen.
    """

    def __init__(self, network, req_gen, network_type, initpos=None):
        self.network_type = network_type
        self.network: Network = Network(network,
                                        network_type=self.network_type, shortest_path_mode=network.shortest_path_mode)
        self.req_gen = req_gen
        self.initpos = initpos

        self.position = self.initpos
        self.time = 0
        self.remaining_time = 0
        self.next_stop = None

        self.stoplist: List[Stop] = []

        # req_data contains for each request:
        # req_epoch, origin, destination, pickup_epoch, dropoff-epoch
        self.req_data = dict()

        # insertion_data contains for each insertion
        # time, stoplist_length, stoplist_volume, rest_stoplist_volume,
        # pickup_idx, dropoff_idx, insertion_type

        # insertion_type is:
        #  1 if both PU and DO en route
        #  2 if only PU en route
        #  3 if neither PU nor DO en route
        self.insertion_data_columns = ('time', 'stoplist_length', 'stoplist_volume',
                                       'rest_stoplist_volume',
                                       'pickup_index', 'dropoff_index', 'insertion_type')
        self.insertion_data = []

    def process_new_request(self, req: Request):
        """
        Process a new request. Before doing that, fast-forward internal clock
        to request epoch and serve all requests pending until that time.
        """
        # process all requests till now and advance clock
        # if all stops had already been processed (potentially in last round), but the bus is still moving to its next
        # stop, i.e. in the middle of an edge
        if req.req_epoch < self.time:
            # We are still "in the middle of an edge". There can't be any need to process stops.
            assert (self.time - req.req_epoch) <= 1
            self.remaining_time = req.req_epoch - self.time
        else:
            # else, fast-forward all remaining stops
            self.fast_forward(req.req_epoch)

        # then add a dummy-stop (type == -1) at current position
        self._insert_stop_into_stoplist(0, self.position, arrtime=self.time, stop_type=-1, req_id=None)

        # now insert req into stoplist
        self.add_request(req)

        # remove dummy stop again
        dummy_stop = self.stoplist.pop(0)
        assert dummy_stop.stop_type == -1

    def fast_forward(self, t):
        """
        Service all stops till a time t.
        Set self.position to the correct value.
        """
        self.remaining_time = 0

        for idx, s in enumerate(self.stoplist):
            self.next_stop = s
            if s.time <= t:
                self.process_stop(s)
            else:
                self.stoplist = self.stoplist[idx:]
                self.next_stop = self.stoplist[0]
                break
        else:
            self.stoplist = []
            self.next_stop = None

        # if stoplist is not empty after processing all stops until t do the following
        if self.next_stop:  # we are *not* idling
            self.position, self.remaining_time = self.interpolate(
                current_time=t, started_from=self.position,
                going_to=self.next_stop.position,
                started_at=self.time)

        # this can set self.time to a value larger than t (see above)
        self.time = t + self.remaining_time

    def add_request(self, req: Request):
        """
        Inserts req to self.stoplist
        Logs details of the request and the insertion.
        """
        assert self.stoplist[0].stop_type == -1

        def position_stop_in_stoplist(requested_stop_position, stoplist):
            """
            returns the position of the stop in a stoplist - potentially also just a section of it
            """
            for idx_stoplist, (u, v) in enumerate(pairwise(stoplist)):
                stop_is_on_route, dist_to = self._is_between(requested_stop_position, u.position, v.position)
                if stop_is_on_route:
                    break
            else:
                # this should never happen
                raise ValueError(f"Stop {requested_stop_position} is not on the route between any two stops in "
                                 f"the stoplist. But this should not be possible.")

            return idx_stoplist + 1, u.time + dist_to

        # we need these numbers only for our statistics
        nodes_in_stoplist_volume = self.network.all_reachable_nodes_on_stoplist(self.stoplist)
        len_stoplist_volume = len(nodes_in_stoplist_volume)

        pickup_enroute = req.origin in nodes_in_stoplist_volume
        # insert PU
        if pickup_enroute:
            pickup_idx, pickup_epoch = position_stop_in_stoplist(req.origin, self.stoplist)
        else:
            pickup_idx = len(self.stoplist)
            pickup_epoch = self.stoplist[-1].time + self.network.shortest_path_length(self.stoplist[-1].position,
                                                                                      req.origin)
        self._insert_stop_into_stoplist(pickup_idx, req.origin, arrtime=pickup_epoch, stop_type=1, req_id=req.req_id)

        # again statistics
        nodes_in_rest_stoplist_volume = self.network.all_reachable_nodes_on_stoplist(self.stoplist[pickup_idx:])
        len_rest_stoplist_volume = len(nodes_in_rest_stoplist_volume)

        dropoff_enroute = req.destination in nodes_in_rest_stoplist_volume
        if dropoff_enroute:
            dropoff_idx, dropoff_epoch = position_stop_in_stoplist(req.destination, self.stoplist[pickup_idx:])
        else:
            dropoff_idx = len(self.stoplist)
            dropoff_epoch = self.stoplist[-1].time + self.network.shortest_path_length(self.stoplist[-1].position,
                                                                                       req.destination)

        # insert DO
        self._insert_stop_into_stoplist(dropoff_idx + pickup_idx, req.destination, arrtime=dropoff_epoch,
                                        stop_type=0, req_id=req.req_id)

        # and once more statistics
        request_handling_type = 1 if pickup_enroute and dropoff_enroute else 2 if pickup_enroute else 3

        # and let's save all these numbers
        # but first correct for the dummy stop
        pickup_idx -= 1
        dropoff_idx -= 1
        self.insertion_data.append((self.time, len(self.stoplist) - 2, len_stoplist_volume, len_rest_stoplist_volume,
                                    pickup_idx, dropoff_idx, request_handling_type))

        # store self.req_data
        self.req_data[req.req_id] = dict(origin=req.origin,
                                         destination=req.destination,
                                         req_epoch=req.req_epoch,  # NOT self.time
                                         # since jump. see function fast_forward
                                         pickup_epoch=pickup_epoch,
                                         dropoff_epoch=dropoff_epoch)

    def simulate_all_requests(self):
        """
        simulates the system till req_gen is empty
        """
        for req in tqdm(self.req_gen, desc="Simulating requests"):
            self.process_new_request(req)
        print(f"simulation complete. current time {self.time}")

    def process_stop(self, s: Stop):
        self.time = s.time
        self.remaining_time = 0
        self.position = s.position

        if s.stop_type == 1:
            assert self.req_data[s.req_id]['pickup_epoch'] == self.time
        else:
            assert s.stop_type == 0
            assert self.req_data[s.req_id]['dropoff_epoch'] == self.time

    def interpolate(self, current_time, started_from, going_to, started_at):
        """
        Returns:
        --------
            position, remaining_time: position is the next node on the way, remaining_time
                is the remaining time necessary to reach position.
        """
        assert current_time >= started_at

        if current_time == started_at:
            pos = started_from
            remaining_time = 0
            return pos, remaining_time

        shortest_path = self.network.shortest_path(started_from, going_to, stoplist=self.stoplist)
        shortest_path_length = len(shortest_path) - 1

        if current_time >= started_at + shortest_path_length:
            pos = going_to
            remaining_time = 0
        else:
            delta_t = current_time - started_at
            num_nodes_traversed = ceil(delta_t)  # next node
            remaining_time = num_nodes_traversed - delta_t
            pos = shortest_path[num_nodes_traversed]

        return pos, remaining_time

    def _is_between(self, a, u, v):
        """
        checks if a is on a shortest path between u and v
        """
        dist_to = self.network.shortest_path_length(u, a)
        dist_from = self.network.shortest_path_length(a, v)
        is_inbetween = dist_to + dist_from == self.network.shortest_path_length(u, v)
        return is_inbetween, dist_to

    def _insert_stop_into_stoplist(self, idx, position, arrtime, stop_type, req_id):
        stop = Stop(position=position,
                    time=arrtime,
                    stop_type=stop_type,
                    req_id=req_id)
        self.stoplist.insert(idx, stop)


class FixedRouteBus(object):
    """
    A simulator that simulates a normal public transport bus with pre-determined route.
    Any network can be chosen.
    """

    def __init__(self, network, req_gen, network_type, initpos=None):
        self.graph_type, self.N = network_type.split('_')
        self.N = int(self.N)
        self.network_type = network_type
        self.network: Network = Network(network,
                                        network_type="novolcomp", shortest_path_mode=network.shortest_path_mode)
        self.req_gen = req_gen
        # so far only defined for grid networks
        self.req_data = dict()
        self.insertion_data = []
        self.route_length = self.N
        if self.graph_type == "grid" and self.N % 2 == 1:
            self.route_length = self.N + 1
        if self.graph_type == "line":
            self.route_length = self.N * 2 - 2
        if self.graph_type == "star":
            self.route_length = 2*(self.N-1)


        # the node positions on the cycle-route are simple integers
        # we can pretend the nodes are shuffled randomly - hence, we can also simply put them in one line
        # since our nodes are named as node at position (x,y), we set their position equal to x*y

    def process_new_request(self, req: Request):
        """
        Process a new request."""
        if self.graph_type == "grid":
            bus_position_at_request = req.req_epoch % self.route_length
            pickup = req.origin[0]*np.sqrt(self.N) + req.origin[1]
            dropoff = req.destination[0]*np.sqrt(self.N) + req.destination[1]

            if pickup >= bus_position_at_request:
                pickup_epoch = req.req_epoch + pickup - bus_position_at_request
            else:
                pickup_epoch = req.req_epoch + pickup - bus_position_at_request + self.route_length

            if dropoff >= pickup:
                dropoff_epoch = pickup_epoch + dropoff - pickup
            else:
                dropoff_epoch = pickup_epoch + dropoff - pickup + self.route_length

            self.req_data[req.req_id] = dict(origin=req.origin,
                                             destination=req.destination,
                                             req_epoch=req.req_epoch,
                                             pickup_epoch=pickup_epoch,
                                             dropoff_epoch=dropoff_epoch
                                             )

            # let's insert dummy insertion data point to not break plotting right away
            self.insertion_data.append(
                (-1, -1, -1, -1, -1,
                 -1, -1, -1, -1))

        elif self.graph_type == "line":
            # our bus starts driving at time t=0 at node 0
            # and goes in continues cycles without every stopping
            origin_position_forward = req.origin
            origin_position_backward = self.N - 1 - req.origin
            destination_position_forward = req.destination
            destination_position_backward = self.N - 1 - req.destination

            bus_position_at_request = req.req_epoch % self.route_length
            forward = bus_position_at_request < (self.N-1)
            if forward:
                if bus_position_at_request <= origin_position_forward:
                    pickup_epoch = req.req_epoch + origin_position_forward - bus_position_at_request
                else:
                    pickup_epoch = req.req_epoch + origin_position_backward + self.N - 1 - bus_position_at_request
                    forward = False
            else:
                if bus_position_at_request - (self.N-1) <= origin_position_backward:
                    pickup_epoch = req.req_epoch + origin_position_backward - (bus_position_at_request - (self.N-1))
                else:
                    pickup_epoch = req.req_epoch + origin_position_forward + self.route_length - bus_position_at_request
                    forward = True

            if forward:
                if origin_position_forward <= destination_position_forward:
                    dropoff_epoch = pickup_epoch + destination_position_forward - origin_position_forward
                else:
                    dropoff_epoch = pickup_epoch + destination_position_backward + self.N - 1 - origin_position_forward
            else:
                if origin_position_backward <= destination_position_backward:
                    dropoff_epoch = pickup_epoch + destination_position_backward - origin_position_backward
                else:
                    dropoff_epoch = pickup_epoch + destination_position_forward + self.N - 1 - origin_position_backward

            self.req_data[req.req_id] = dict(origin=req.origin,
                                             destination=req.destination,
                                             req_epoch=req.req_epoch,
                                             pickup_epoch=pickup_epoch,
                                             dropoff_epoch=dropoff_epoch
                                             )

            # let's insert dummy insertion data point to not break plotting right away
            self.insertion_data.append(
                (-1, -1, -1, -1, -1,
                 -1, -1, -1, -1))

        elif self.graph_type == "star":
            # our bus starts driving at time t=0 at node 0
            # and goes in continues cycles without every stopping

            bus_position_at_request = req.req_epoch % self.route_length
            pickup_position = 2*req.origin - 1
            dropoff_position = 2*req.destination - 1
            if req.origin == 0:
                pickup_position = bus_position_at_request + 2 - (bus_position_at_request % 2)
                pickup_epoch = req.req_epoch + pickup_position - bus_position_at_request
            elif pickup_position >= bus_position_at_request :
                pickup_epoch = req.req_epoch + pickup_position - bus_position_at_request
            else:
                pickup_epoch = req.req_epoch + pickup_position - bus_position_at_request + self.route_length

            if req.destination == 0:
                dropoff_epoch = pickup_epoch + 1
            elif dropoff_position > pickup_position:
                dropoff_epoch = pickup_epoch + dropoff_position - pickup_position
            else:
                dropoff_epoch = pickup_epoch + dropoff_position - pickup_position + self.route_length

            self.req_data[req.req_id] = dict(origin=req.origin,
                                             destination=req.destination,
                                             req_epoch=req.req_epoch,
                                             pickup_epoch=pickup_epoch,
                                             dropoff_epoch=dropoff_epoch
                                             )

            # let's insert dummy insertion data point to not break plotting right away
            self.insertion_data.append(
                (-1, -1, -1, -1, -1,
                 -1, -1, -1, -1))

        elif self.graph_type == "cycle":
            # our bus starts driving at time t=0 at node 0
            # and goes in continues cycles without every stopping

            bus_position_at_request = req.req_epoch % self.route_length
            if req.origin >= bus_position_at_request:
                pickup_epoch = req.req_epoch + req.origin - bus_position_at_request
            else:
                pickup_epoch = req.req_epoch + req.origin - bus_position_at_request + self.route_length

            if req.destination >= req.origin:
                dropoff_epoch = pickup_epoch + req.destination - req.origin
            else:
                dropoff_epoch = pickup_epoch + req.destination - req.origin + self.route_length

            self.req_data[req.req_id] = dict(origin=req.origin,
                                             destination=req.destination,
                                             req_epoch=req.req_epoch,
                                             pickup_epoch=pickup_epoch,
                                             dropoff_epoch=dropoff_epoch
                                             )

            # let's insert dummy insertion data point to not break plotting right away
            self.insertion_data.append(
                (-1, -1, -1, -1, -1,
                 -1, -1, -1, -1))

    def simulate_all_requests(self):
        for req in self.req_gen:
            self.process_new_request(req)
        print(f"simulation complete.")
