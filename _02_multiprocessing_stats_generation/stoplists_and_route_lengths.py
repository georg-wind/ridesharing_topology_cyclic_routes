def stoplists_and_node_visit_frequencies(req_df):
    node_visits_dict = {}
    # to decrease computational complexity, we build an auxiliary visitlist that only contains visit-times
    # after the current request
    scheduled_visits_list = []
    routelistlength_over_reqs = []

    def process_stops(req):
        nonlocal scheduled_visits_list
        # Process origin
        origin, pickup_epoch = req['origin'], req['pickup_epoch']
        process_node(origin, pickup_epoch)

        # Process destination
        destination, dropoff_epoch = req['destination'], req['dropoff_epoch']
        process_node(destination, dropoff_epoch)

        # store current route-length
        req_epoch = req["req_epoch"]

        scheduled_visits_list = [visit for visit in scheduled_visits_list if visit > req_epoch]
        routelistlength_over_reqs.append(len(scheduled_visits_list))

    def process_node(node, epoch):
        if node not in node_visits_dict.keys():
            node_visits_dict[node] = [epoch]
            scheduled_visits_list.append(epoch)
        else:
            if node_visits_dict[node][-1] < epoch:
                node_visits_dict[node].append(epoch)
                scheduled_visits_list.append(epoch)

    req_df.apply(process_stops, axis=1)

    return node_visits_dict, routelistlength_over_reqs


# New version
def stoplists_and_node_visit_frequencies_optimized(req_data):
    node_visits_dict = {}
    scheduled_visits_list = []
    routelistlength_over_reqs = []
    unique_scheduled_stops_over_reqs = []

    def process_stops(req):
        nonlocal scheduled_visits_list
        # Process origin
        origin, pickup_epoch = req['origin'], req['pickup_epoch']
        process_node(origin, pickup_epoch)

        # Process destination
        destination, dropoff_epoch = req['destination'], req['dropoff_epoch']
        process_node(destination, dropoff_epoch)

        # store current route-length
        req_epoch = req["req_epoch"]

        scheduled_visits_list = [visit for visit in scheduled_visits_list if visit > req_epoch]
        routelistlength_over_reqs.append(len(scheduled_visits_list))
        unique_scheduled_stops_over_reqs.append(len(set(scheduled_visits_list)))

    def process_node(node, epoch):
        if node not in node_visits_dict:
            node_visits_dict[node] = [epoch]
            scheduled_visits_list.append(epoch)
        else:
            if node_visits_dict[node][-1] < epoch:
                node_visits_dict[node].append(epoch)
                scheduled_visits_list.append(epoch)

    for _, req in req_data.items():
        process_stops(req)

    return node_visits_dict, routelistlength_over_reqs, unique_scheduled_stops_over_reqs


