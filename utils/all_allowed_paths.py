import networkx as nx

def find_number_of_allowed_routes(G, g_nodes_shortest_paths: dict):
    
    # helper_function to reduce a box of possible remaining draws depending on a current draw and the network shortest paths
    # EDIT: We also need to expand sub_route by the nodes on shortest paths which we delete
    def filter_remaining_box(node_box, current_route, shortest_paths, route_list):
        # Step 1: removing all lots which start en-route of the currently added route:
        # node_box = [lot for lot in node_box if not lot[0] in shortest_paths[current_route]]
        # Step 2: removing the start of all lots which start at the current node(s) - their destination may still be drawn
        
        # the function generates different branches how the route is configured if the old box still had draws in it which start on current path
        route_insertions = {}
        route_insertions["base_case"] = {}
        route_insertions["base_case"]["reduced_box"] = []
        route_insertions["base_case"]["route_list"] = route_list
        
        # find all nodes we need to branch on
        #there are n cases:
       
        for node_comb in node_box:
            # 1. both start and end node are not in the current route nor nodes_on_route
            if node_comb[0] not in list(current_route)+shortest_paths[current_route]:
                for key in route_insertions.keys():
                    route_insertions[key]["reduced_box"].append(node_comb)
            # if it is - and there is only one node left in the lot, we can cut it
            elif len(node_comb) == 1 and node_comb[0] in current_route:
                pass
            elif len(node_comb) == 1 and node_comb[0] in shortest_paths[current_route]:
                for key in route_insertions.keys():
                    route_insertions[key]["route_list"] = route_insertions[key]["route_list"][:-1] + [node_comb[0]] + route_insertions[key]["route_list"][-1:]
            # 2. start node is in the current route, end node is not in the current route nor nodes_on_route - we need to
            # cut start node
            elif node_comb[0] in current_route and node_comb[1] not in list(current_route)+shortest_paths[current_route]:
                for key in route_insertions.keys():
                    route_insertions[key]["reduced_box"].append([node_comb[1]])
            # 3. start node is = origin, end node is in nodes_on_route - we need to insert end_node and remove the combi
            elif node_comb[0] == current_route[0] and node_comb[1] in shortest_paths[current_route]:
                if node_comb[1] in route_insertions.keys():
                    for key in route_insertions.keys():
                        if key not in ["base_case", node_comb[1]]:
                            route_insertions[key]["reduced_box"].append([node_comb[1]])
                else:
                    route_insertions[node_comb[1]] = {}
                    route_insertions[node_comb[1]]["reduced_box"] = route_insertions["base_case"]["reduced_box"]
                    route_insertions[node_comb[1]]["route_list"] = route_insertions["base_case"]["route_list"][:-1] + [node_comb[1]] + route_insertions["base_case"]["route_list"][-1:]
                    for key in route_insertions.keys():
                        if key not in ["base_case", node_comb[1]]:
                            route_insertions[key]["reduced_box"].append([node_comb[1]])
            # 4 start node is in nodes_on_route, end node is the second current_route node - we need to insert start_node and remove the combi
            elif node_comb[0] in shortest_paths[current_route] and node_comb[1] == current_route[1]:
                if node_comb[0] in route_insertions.keys():
                    for key in route_insertions.keys():
                        if key not in ["base_case", node_comb[0]]:
                            route_insertions[key]["reduced_box"].append(node_comb)
                else:
                    route_insertions[node_comb[0]] = {}
                    route_insertions[node_comb[0]]["reduced_box"] = route_insertions["base_case"]["reduced_box"]
                    route_insertions[node_comb[0]]["route_list"] = route_insertions["base_case"]["route_list"][:-1] + [node_comb[0]] + route_insertions["base_case"]["route_list"][-1:]
                    for key in route_insertions.keys():
                        if key not in ["base_case", node_comb[0]]:
                            route_insertions[key]["reduced_box"].append(node_comb)

            # 5. start node is in nodes_on_route, end node is not in the current route nor nodes_on_route - we need 
            # to insert and keep second node
            elif node_comb[0] in shortest_paths[current_route] and node_comb[1] not in list(current_route)+shortest_paths[current_route]:
                if node_comb[0] in route_insertions.keys():
                    route_insertions[node_comb[0]]["route_list"] = route_insertions[node_comb[0]]["route_list"][:-1] + [node_comb[0]] + route_insertions[node_comb[0]]["route_list"][-1:]
                    route_insertions[node_comb[0]]["reduced_box"].append([node_comb[1]])
                    for key in route_insertions.keys():
                        if key not in ["base_case", node_comb[0]]:
                            route_insertions[key]["reduced_box"].append(node_comb)
                else:
                    route_insertions[node_comb[0]] = {}
                    route_insertions[node_comb[0]]["route_list"] = route_insertions["base_case"]["route_list"][:-1] + [node_comb[0]] + route_insertions["base_case"]["route_list"][-1:]
                    route_insertions[node_comb[0]]["reduced_box"] = route_insertions["base_case"]["reduced_box"]
                    route_insertions[node_comb[0]]["reduced_box"].append([node_comb[1]])
                    for key in route_insertions.keys():
                        if key not in ["base_case", node_comb[0]]:
                            route_insertions[key]["reduced_box"].append(node_comb)
            # 6. start node is in nodes_on_route, end node is in nodes_on_route - we need to insert both - TBD
            
            # Step 3: let's remove all duplicate items
            for key in route_insertions.keys():
                unique_box = []
                for lot in route_insertions[key]["reduced_box"]:
                    if lot not in unique_box:
                        unique_box.append(lot)
                route_insertions[key]["reduced_box"] = unique_box
        
        if len(route_insertions.keys()) == 1:
            options = [(route_insertions["base_case"]["reduced_box"], route_insertions["base_case"]["route_list"])]
        else:
            options = []
            for key in route_insertions.keys():
                if key != "base_case":
                    options.append((route_insertions[key]["reduced_box"], route_insertions[key]["route_list"]))
        return options
    
    # recursive function to find all allowed routes
    def all_possible_sub_paths(all_routes, route_list, node_combs, shortest_paths):

        # let's take the current route and go through all remaining lots individually, to expand all_routes
        for i in range(len(node_combs)):
            # Set up sub_list of node_combs which will be main list for this iteration
            sub_node_combs = list(node_combs)
            sub_route = list(route_list)

            # Select one lot and remove it from box
            node_comb = sub_node_combs.pop(i)

            # if the lot still has 2 nodes, it is appended entirely to the route until here
            if len(node_comb) == 2:
                origin = node_comb[0]
                destination = node_comb[1]
                sub_route.append(origin)
            # if not, we need to set the last node to be the origin - it doesnt get readded to the route
            else:
                origin = sub_route[-1]
                destination = node_comb[0]
            
            sub_route.append(destination)

            # now we got the current route
            current_route = (origin, destination)

            # let's reduce the box and go down all the possible options it has generated
            for option in filter_remaining_box(sub_node_combs, current_route, shortest_paths, sub_route):
                new_box = option[0]
                option_sub_route = option[1]

                # if the new_box has no items left, we return the current path
                if len(new_box) == 0:
                    all_routes.append(option_sub_route)
                    return all_routes
                # else, we recursively call ourselves with the current status so for each item in the remaining box, sub-paths are considered
                elif len(new_box) == 1:
                    option_sub_route = option_sub_route+list(new_box[0])
                    all_routes.append(option_sub_route)
                    return all_routes
                else:
                    # print("There are still combinations left")
                    # print(f"Current route: {sub_route}")
                    # print(f"Current box: {new_box}")
                    all_routes = all_possible_sub_paths(all_routes=all_routes, route_list=option_sub_route, node_combs=new_box, shortest_paths=shortest_paths)
        
        # once we have gone through all possible next draws from the current route, we return the now fully populated all_routes collection to the caller
        return all_routes
    
    # TBD
    def input_prep_network_properties(G):
        # TBD: function to automatically determine all nodes on the shortest path(s) between all nodes i, j
        nodes=list(G)
        node_combs = [(x, y) for x in nodes for y in nodes if x !=y]
        nodes_shortest_paths = {node_comb: [] for node_comb in node_combs}
        ## determination of nodes on shortest paths between two nodes x, y is missing!
        ## tbd
        ## tbd
        return nodes_shortest_paths, nodes, node_combs

    # initializing values from input
    _, nodes, initial_node_combs = input_prep_network_properties(G)

    # get all allowed routing combinations
    all_paths = all_possible_sub_paths(all_routes=[], route_list=[], node_combs=initial_node_combs, shortest_paths=g_nodes_shortest_paths)
    print(all_paths)
    path_lengths = [len(path) for path in all_paths]
    print(path_lengths)
    optimal_path_length = min(path_lengths)
    indices_shortest_paths = [i for i, elem in enumerate(path_lengths) if path_lengths == optimal_path_length]
    print(f"Shortest routes are:")
    for i in indices_shortest_paths:
        print(all_paths[i])
    print(f"{sum([length == optimal_path_length for length in path_lengths])} routes are optimal. Optimal route length: {optimal_path_length}.")

    def sanity_check(path_lengths, min_length, max_length):
        # print([len(path) for path in all_paths])
        too_long_paths = sum([length > max_length for length in path_lengths])
        too_short_paths = sum([length < min_length for length in path_lengths])
        if too_long_paths > 0:
            print(f"{too_long_paths} routes are too long.")
        elif too_short_paths > 0:
            print(f"{too_short_paths} routes are too short.")
        else:
            print("All routes are of correct length.")

        # if len(set(path_collection)) != len(path_collection):
        #     print("Path Collection contains duplicates.")
        # else:
        #     print("All paths are unique")
    sanity_check(path_lengths, 2*len(nodes)-1, (len(nodes)-1)**2)

    # get number of 
    n_allowed = len(all_paths)
    print(f"network has {n_allowed} allowed routes.")
    return n_allowed



letter_5 = nx.Graph()
letter_5.add_edge(1, 2)
letter_5.add_edge(1, 5)
letter_5.add_edge(2, 3)
letter_5.add_edge(2, 5)
letter_5.add_edge(3, 4)
letter_5.add_edge(3, 5)
letter_5.add_edge(4, 1)
letter_5.add_edge(4, 5)

letter_5_nodes = list(letter_5)
letter_5_node_combs = [(x, y) for x in letter_5_nodes for y in letter_5_nodes if x !=y]
shortest_paths_letter_5 = {node_comb: [] for node_comb in letter_5_node_combs}
shortest_paths_letter_5[(1, 3)] = [2, 4, 5]
shortest_paths_letter_5[(3, 1)] = [2, 4, 5]
shortest_paths_letter_5[(2, 4)] = [1, 3, 5]
shortest_paths_letter_5[(4, 2)] = [1, 3, 5]

find_number_of_allowed_routes(letter_5, shortest_paths_letter_5)
#%%
