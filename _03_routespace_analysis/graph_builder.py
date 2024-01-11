from multiprocessing import Pool

import networkx as nx
import numpy as np
from tqdm import tqdm
from utils import pickle_loader


def build_routespace(route, current_route_lengths):
    '''
    Builds a graph from the logged routes of a simulation run.
    :param x: the x-rate for generating the graph
    :param topology: 
    :param mode: the mode used for generating the data
    :param xrange: 
    :param n_reqs:
    :return:
    '''

    # 2. initialize networkx graph object
    result_space_graph = nx.MultiDiGraph()

    # Using a dictionary to keep track of added vertices for quick lookup
    added_vertices = set()
    added_edges = set()
    resultspace_walk = []

    # 3. iterate over all routes and add edges to graph
    for idx, length in enumerate(tqdm(current_route_lengths, desc="Building graph from logged routes")):
        sub_route = route[idx:idx + length]

        # we are interpreting the transitions as undirected, so in order of not interpreting A->B and B->A as two
        # different edges, we sort the nodes of the transition for interpreting them as an edge
        sub_route = [tuple(sorted((sub_route[i], sub_route[i + 1]))) for i in range(len(sub_route) - 1)]

        # we are not interested in multiple planned transverses, so we convert the route to a set
        sub_route = set(sub_route)
        # need to convert back to tuple for hashing
        sub_route = tuple(sorted(sub_route))

        # Add the sub_route as a vertex to the result-space
        if sub_route not in added_vertices:
            result_space_graph.add_node(sub_route, visits=[idx])
            added_vertices.add(sub_route)
        else:
            result_space_graph.nodes[sub_route]['visits'].append(idx)

        # Add edges between consecutive sub_routes
        edge = (resultspace_walk[-1], sub_route)
        if edge not in added_edges:
            result_space_graph.add_edge(*edge, traversals=[])
            result_space_graph.edges[edge]['traversals'].append(idx - 1)
            added_edges.add(edge)

        resultspace_walk.append(sub_route)

    return result_space_graph, resultspace_walk


def build_cycle_routespaces(route):
    collapse_multiple_traversals = False
    if collapse_multiple_traversals:
        # we are not interested in multiple planned transverses, so we convert the route to a set
        result_space_graph = nx.Graph()
    else:
        result_space_graph = nx.DiGraph()

    # Using a dictionary to keep track of added vertices for quick lookup
    added_vertices = set()
    stop_indices = {}  # Dictionary to store the most recent index of each stop

    # 3. iterate over all routes and add edges to graph
    for idx in tqdm(range(len(route)), desc=f"Processing Route"):
        stop = route[idx]
        # If the stop is already seen before
        if stop in stop_indices:
            current_cycle = route[stop_indices[stop]:idx + 1]
            # turning route into edge set
            current_cycle = [tuple(sorted((current_cycle[i], current_cycle[i + 1])))
                             for i in range(len(current_cycle) - 1)]

            # need to convert back to tuple for hashing
            current_cycle = tuple(sorted(current_cycle))
            # Add the current_cycle as a vertex to the result-space
            if current_cycle not in added_vertices:
                result_space_graph.add_node(current_cycle, visits=[idx])
                added_vertices.add(current_cycle)
            else:
                result_space_graph.nodes[current_cycle]['visits'].append(idx)
            stop_indices[stop] = idx  # Update the index to the current one
        else:
            stop_indices[stop] = idx

    return result_space_graph


def build_x_routespace(func_args):
    x, route = func_args
    # 2. initialize networkx graph object
    collapse_multiple_traversals = False
    if collapse_multiple_traversals:
        # we are not interested in multiple planned transverses, so we convert the route to a set
        result_space_graph = nx.Graph()
    else:
        result_space_graph = nx.DiGraph()

    # Using a dictionary to keep track of added vertices for quick lookup
    added_vertices = set()

    stop_indices = {}  # Dictionary to store the most recent index of each stop

    # 3. iterate over all routes and add edges to graph
    for idx in range(len(route)):
        stop = route[idx]
        # If the stop is already seen before
        if stop in stop_indices:
            current_cycle = route[stop_indices[stop]:idx + 1]
            # turning route into edge set
            current_cycle = [tuple(sorted((current_cycle[i], current_cycle[i + 1])))
                             for i in range(len(current_cycle) - 1)]

            # need to convert back to tuple for hashing
            current_cycle = tuple(sorted(current_cycle))
            # Add the current_cycle as a vertex to the result-space
            if current_cycle not in added_vertices:
                result_space_graph.add_node(current_cycle, visits=[idx])
                added_vertices.add(current_cycle)
            else:
                result_space_graph.nodes[current_cycle]['visits'].append(idx)

            stop_indices[stop] = idx  # Update the index to the current one
        else:
            stop_indices[stop] = idx
    return str(x), result_space_graph
