import networkx as nx
from utils.mongo_db_connect import cache_to_mongodb

# @cache_to_mongodb()
def get_shortest_paths_and_volume(G, mode="staticmax"):
    """
    Function that retrieves the shortest paths and the volume of the shortest paths for all node-pairs in a graph.
    
    Parameters
    ----------
    G : networkx graph
        The graph for which we want to calculate the shortest paths and the volume of the shortest paths.
    mode : str, optional
        Modes "staticmax" and "staticmin" return the a priori (i.e. without knowlege of the scheduled route) 
        volume-maximizing and minimizing shortest paths, respectively.
        Mode "originalpaper" returns one shortest path per node-pair as implemented in the original paper, depending 
        ultimately on the implementation of the "Graph.adj"-attribute in networkx (which is more or less random). 
        It's volume-relevance is not considered.
        "all_volume_info" returns the entire dictionary of paths and corresponding volume-values, 
        so it can be used to dynamically adjust the path-choice depending on the scheduled route.
        
    Returns
    -------
    shortest_paths : dict
        Dictionary of dictionaries. The outer dictionary has the origin as keys and the inner dictionaries as values.
        The inner dictionaries have the destinations as keys and the shortest as values. If mode is any of 
        originalpaper, staticmax or statixmin, it contains one path chosen according to the mode.
        If mode is "all_volume_info", the dictionary contains another level of dictionaries, with the values "paths", 
        "volume-values" and "volumes".
            
    """
    # TODO: make use of network topology property - if its grid or star, these algorithms are not really necessary

    node_list = list(G)

    shortest_paths = dict()
    # initializing dictionary
    for u in node_list:
        shortest_paths[u] = dict()

    open_nodes = node_list.copy()
    # populating dictionary
    while len(open_nodes) > 0:
        u = open_nodes.pop()
        shortest_paths[u][u] = [[u, u]]
        # let's only check nodes which have not yet been checked
        open_paths_u = [open_node for open_node in open_nodes if open_node not in shortest_paths[u].keys()]  ## TODO: 
        # could be optimized by sorting this list from longest to shortest shortest path (but how much would this step 
        # cost?)

        while len(open_paths_u) > 0:
            v = open_paths_u.pop()
            # this is an extremely expensive step, so we store all the information we are getting from it (see steps below)
            shortest_paths[u][v] = list(nx.all_shortest_paths(G, source=u, target=v))

            # if my shortest path from u to v crosses a node w, then the collection of all shortest paths from u to v is 
            # guaranteed to entail all shortest paths from u to w and from w to v, too.
            sub_paths_u = {}
            sub_paths_v = {}
            for p in shortest_paths[u][v]:
                if len(p) > 2:
                    for n in range(1, len(p) - 1):
                        w = p[n]

                        ## CHECKING THE PATHS FROM U TO W
                        # only relevant if the node is not yet completed from a previous iteration
                        if w in open_paths_u:
                            # if the node is not yet in the keys of the sub_list, we can safely add it right away - won't 
                            # be a duplicate,-
                            if w not in sub_paths_u.keys():
                                sub_paths_u[w] = [p[:n + 1]]

                            # if it is, we must check that this specific path is not yet added
                            elif any(p[:n + 1] != path for path in sub_paths_u[w]):
                                sub_paths_u[w].append(p[:n + 1])
                            else:
                                break
                        else:
                            break

                        ## CHECKING THE PATHS FROM W TO V
                        # if the node is not yet completed from a previous iteration
                        if w not in shortest_paths[v].keys():
                            # if the node is not yet in the keys of the sub_list, we can safely add it right away - won't
                            # be a duplicate
                            if w not in sub_paths_v.keys():
                                sub_paths_v[w] = [p[n:][::-1]]
                            # if it is, we must check that this specific path is not yet added
                            elif any(p[n:][::-1] != path for path in sub_paths_v[w]):
                                sub_paths_v[w].append(p[n:][::-1])
                            else:
                                break
                        else:
                            break
                else:
                    break

            # adding these paths to the overall dictionary
            for w in sub_paths_u.keys():
                shortest_paths[u][w] = sub_paths_u[w]
                open_paths_u.remove(w)

            for w in sub_paths_v.keys():
                shortest_paths[v][w] = sub_paths_v[w]
                shortest_paths[w][v] = [p[::-1] for p in sub_paths_v[w]]

        #  adding the reverse paths to the dictionary, too
        for key in shortest_paths[u].keys():
            shortest_paths_v_u = [p[::-1] for p in shortest_paths[u][key]]
            shortest_paths[key][u] = shortest_paths_v_u

    # identification of volume-optimal shortest paths (case 1)
    volume_optimal_paths = dict()
    for u in node_list:
        volume_optimal_paths[u] = dict()
        for j in node_list:
            volume_optimal_paths[u][j] = dict()

    for i in range(0, len(node_list)):
        u = node_list[i]
        while i < len(node_list):
            v = node_list[i]
            # this gives the entire set of nodes on the paths from u to v (relevant for case 2)
            volume_optimal_paths[v][u]["volume_set"] = volume_optimal_paths[u][v]["volume_set"] = set([node for path in
                                                                                                       shortest_paths[
                                                                                                           u][v] for
                                                                                                       node in path])
            # and this gives the size of the set (relevant for case 1)
            volume_optimal_paths[u][v]["volume"] = volume_optimal_paths[v][u]["volume"] = len(
                volume_optimal_paths[v][u][
                    "volume_set"]) - 2  # -2 because we don't want to freq_counts u and v
            volume_optimal_paths[u][v]["paths"] = shortest_paths[u][v]
            volume_optimal_paths[v][u]["paths"] = shortest_paths[v][u]
            i += 1
    # now we can calculate the volume-value of each path
    for i in range(0, len(node_list)):
        u = node_list[i]
        for j in range(0, len(node_list)):
            v = node_list[j]
            if j != i:
                volume_optimal_paths[u][v]["path_vol_values"] = []
                for n in range(0, len(volume_optimal_paths[u][v]["paths"])):
                    path = volume_optimal_paths[u][v]["paths"][n]
                    path_vol_value = 0
                    for node in path[1:-1]:
                        path_vol_value += volume_optimal_paths[node][v]["volume"]
                    volume_optimal_paths[u][v]["path_vol_values"].append(path_vol_value)
            else:
                volume_optimal_paths[u][v]["path_vol_values"] = [0]
                volume_optimal_paths[u][v]["volume"] = 0
                volume_optimal_paths[u][v]["volume_set"] = set([u])
                volume_optimal_paths[u][v]["paths"] = [[u, v]]

    if mode in ["staticmax", "staticmin"]:  # (max and min)
        vol_optimal_paths = dict()
        for u in node_list:
            vol_optimal_paths[u] = dict()
            for j in node_list:
                if u != j:
                    paths_volume_values = volume_optimal_paths[u][j]["path_vol_values"]
                    if len(paths_volume_values) > 0:
                        # note: this is still not a unique choice!
                        if mode == "staticmax":
                            largest_value_ind = paths_volume_values.index(max(paths_volume_values))
                            vol_optimal_paths[u][j] = volume_optimal_paths[u][j]["paths"][largest_value_ind]
                        elif mode == "staticmin":
                            smallest_value_ind = paths_volume_values.index(min(paths_volume_values))
                            vol_optimal_paths[u][j] = volume_optimal_paths[u][j]["paths"][smallest_value_ind]
                    else:
                        vol_optimal_paths[u][j] = volume_optimal_paths[u][j]["paths"][0]
                else:
                    vol_optimal_paths[u][j] = [u, j]
        print(f"Using mode {mode}")
        return vol_optimal_paths, volume_optimal_paths
    elif mode == "all_volume_info":
        print(f"Using mode {mode}")
        return volume_optimal_paths, volume_optimal_paths
    elif mode == "originalpaper":
        return dict(nx.all_pairs_shortest_path(G)), volume_optimal_paths