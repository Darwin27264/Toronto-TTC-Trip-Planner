import sqlite3
import os
import json
import math
import itertools
from itertools import permutations

# Import User Input Function
from get_User_Input import *

# Importing database
data_trip = sqlite3.connect('trips.db')
t = data_trip.cursor()
data_route = sqlite3.connect('routes.db')
r = data_route.cursor()
data_stop = sqlite3.connect('stops.db')
s = data_stop.cursor()
data_subway = sqlite3.connect('subway.db')
m = data_subway.cursor()


def binary_to_dict(the_binary):
    """
    binary_to_dict converts binary numbers into a python dictionary and then returns
    the dictionary
    """
    jsn = ''.join(chr(int(x, 2)) for x in the_binary.split())
    d = json.loads(jsn)
    return d


def stop_distance(stop1, stop2):
    """
    stop_distance returns the distance between two
    stops in units of kilometers
    """
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': stop1})
    stop1 = s.fetchone()
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': stop2})
    stop2 = s.fetchone()
    return math.sqrt(pow(stop1[2] - stop2[2], 2) + pow(stop1[3] - stop2[3], 2)) * 110.947


def start_to_close(start, near_end_stops):
    """
    Summary:
        check if a stop within 200 meters of the ending stop 
        has a direct route from the starting stop

    Args:
        start: starting stop_id
        near_end_stops: all stop_ids of stops within 200 meters of the
                          ending stop

    Returns:
        if a route is found under the conditions above, then
        the function will return a list of tuples of the starting stop,
        new ending stop, and then the string "start_to_close",
        the route name, and the route type. Otherwise the 
        function will return an empty list
    """
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': start})
    starting_point = s.fetchone()
    valid_routes = []
    for i in binary_to_dict(starting_point[4]):
        r.execute("SELECT * FROM routes WHERE route_id=:route_id", {'route_id': i})
        route = r.fetchone()
        for j in near_end_stops:
            if str(j) in binary_to_dict(route[4]):
                valid_routes.append((start, j, "start_to_close", route[0], route[2]))
    return valid_routes


def close_to_end(end, near_start_stops):
    """
    Summary:
        check if a stop within 200 meters of the starting stop
        goes to the ending stop

    Args:
        near_start_stops: all stop_ids of stops within 200 meters of the
                          starting stop
        end: ending stop_id

    Returns:
        if a route is found under the conditions above, then
        the function will return a a list of tuples of the new starting stop,
        ending stop, the string "close_to_end",the route name, and the route type.
        Otherwise the function will return an empty list
    """
    valid_routes = []
    for i in near_start_stops:
        s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': i})
        starting_point = s.fetchone()
        for j in binary_to_dict(starting_point[4]):
            r.execute("SELECT * FROM routes WHERE route_id=:route_id", {'route_id': j})
            route = r.fetchone()
            if str(end) in binary_to_dict(route[4]):
                valid_routes.append((i, end, "close_to_end", route[0], route[2]))
    return valid_routes


def close_to_close(near_start_stops, near_end_stops):
    """
    Summary:
        check if a stop within 200 meters of the starting stop
        goes to a stop within 200 meters of the ending stop

    Args:
        near_start_stops: all stop_ids of stops within 200 meters of the
                          starting stop
        near_end_stops: all stop_ids of stops within 200 meters of the
                          ending stop

    Returns:
        if a route is found under the conditions above, then
        the function will return a a list of tuples of the new starting stop,
        ending stop, the string "close_to_close",the 
        route name, and the route type. Otherwise the function 
        will return an empty list
    """
    valid_routes = []
    for i in near_start_stops:
        s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': i})
        starting_point = s.fetchone()
        for j in binary_to_dict(starting_point[4]):
            r.execute("SELECT * FROM routes WHERE route_id=:route_id", {'route_id': j})
            route = r.fetchone()
            for k in near_end_stops:
                if str(k) in binary_to_dict(route[4]):
                    valid_routes.append((i, k, "close_to_close", route[0], route[2]))
    return valid_routes


def find_close_direct_route(start, end):
    """
    Summary:
        check if a stop within 200 meters of the starting stop
        goes to the ending stop or if a stop within 200 meters
        of the ending stop has a direct route from the starting
        stop

    Args:
        start: starting stop_id
        end: ending stop_id

    Returns:
        if a route is found under any of those conditions, then
        the function will return a list of tuples of the starting stop,
        ending stop,then information about which stop has
        changed, then the route name, and then the route type. 
        Otherwise the function will return an empty list
    """
    near_start_stops = nearby_stops(start)
    near_end_stops = nearby_stops(end)
    route1 = start_to_close(start, near_end_stops)
    route2 = close_to_end(end, near_start_stops)
    route3 = close_to_close(near_start_stops, near_end_stops)
    all_routes = []
    all_routes = route1 + route2 + route3
    return all_routes


def find_direct_route(start, end, val):
    """
    Summary:
        check if there is a direct route from the starting
        stop to the ending stop

    Args:
        start: starting stop_id
        end: ending stop_id
        val: if true check the close stops as well

    Returns:
        if a direct route is found then return a list of tuples
        of the starting stop, ending stop, the string
        'direct', the route name, and the route type. 
        otherwise the function will return an empty list
    """
    valid_routes = []
    return_list = []
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': start})
    starting_point = s.fetchone()
    check_for_walk = stop_distance(start, end)
    if check_for_walk < 0.2:
        return [(start, end, 'walking', -1)]
    for i in binary_to_dict(starting_point[4]):
        r.execute("SELECT * FROM routes WHERE route_id=:route_id", {'route_id': i})
        route = r.fetchone()
        if str(end) in binary_to_dict(route[4]): valid_routes.append((start, end, 'direct', route[0], route[2]))
    if val:
        close_routes = find_close_direct_route(start, end)
        return_list.append(valid_routes + close_routes)
    else:
        return_list.append(valid_routes)
    return return_list


def make_stops_dict(stop):
    """
    make_stops_dict makes a dictionary of all of the stops that bus
    stations withing 200 meters of the original station go to
    """
    stops_list = nearby_stops(stop)
    all_stops = {}
    for k in stops_list:
        s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': k})
        stop = s.fetchone()
        for i in binary_to_dict(stop[4]):
            r.execute("SELECT * FROM routes WHERE route_id=:route_id", {'route_id': i})
            route = r.fetchone()
            for j in binary_to_dict(route[4]):
                all_stops[j] = 0
    return all_stops


def find_closest_stop(start, end, used_stops):
    """
    find_clostest_stop finds the closest stop to the end stop
    without returning any stops inside the "used_stops" list and the stop
    has more than 4 routes goes through it
    """
    dict_stops = make_stops_dict(start)
    if int(list(dict_stops)[0]) != start and int(list(dict_stops)[0]) not in used_stops:
        closest = int(list(dict_stops)[0])
    elif int(list(dict_stops)[1]) not in used_stops:
        closest = int(list(dict_stops)[1])
    else:
        closest = int(list(dict_stops)[2])
    for i in dict_stops:
        if stop_distance(end, int(i)) < stop_distance(end, closest) and int(i) != start and int(i) not in used_stops:
            s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': int(i)})
            stop_info = s.fetchone()
            if len(binary_to_dict(stop_info[4])) >= 4:
                closest = int(i)
    used_stops.append(closest)
    return (closest, used_stops)


def find_closest_subway(stop):
    """
    find_closest_subway will take the parameter "stop" and
    search the subways database for the subway stop closest
    to the current stop and return the stop_id
    """
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': stop})
    stop_info = s.fetchone()
    m.execute("SELECT * FROM subways")
    all_subway = m.fetchall()
    closest = all_subway[0]
    for i in all_subway:
        if stop_distance(stop_info[0], i[0]) < stop_distance(stop_info[0], closest[0]):
            closest = i
    return closest[0]


def navigate_subway(start, end):
    """
    navigate_subway will find a path through the subway lines
    and return a list of all steps of each possible way the user
    can do each step
    """
    m.execute("SELECT * FROM subways WHERE stop_id=:stop_id", {'stop_id': start})
    start_plat = m.fetchone()
    m.execute("SELECT * FROM subways WHERE stop_name LIKE :stop_name",
              {'stop_name': (start_plat[1].split("-")[0] + "%")})
    all_start_platform = m.fetchall()
    m.execute("SELECT * FROM subways WHERE stop_id=:stop_id", {'stop_id': end})
    end_plat = m.fetchone()
    m.execute("SELECT * FROM subways WHERE stop_name LIKE :stop_name", {'stop_name': (end_plat[1].split("-")[0] + "%")})
    all_end_platform = m.fetchall()
    all_routes = []
    for i in all_start_platform:
        for j in all_end_platform:
            start_platform = i
            end_platform = j
            if start_platform[4] == end_platform[4]:
                route = (find_direct_route(start, end, True))
            elif start_platform[4] == 1 and end_platform[4] == 4:
                route = (find_direct_route(start, 14465, True),
                         find_direct_route(14530, end, True))
            elif start_platform[4] == 4 and end_platform[4] == 1:
                route = (find_direct_route(start, 14539, True),
                         find_direct_route(14406, end, True))
            elif start_platform[4] == 2 and end_platform[4] == 3:
                route = (find_direct_route(start, 14498, True),
                         find_direct_route(14546, end, True))
            elif start_platform[4] == 3 and end_platform[4] == 2:
                route = (find_direct_route(start, 14546, True),
                         find_direct_route(14498, end, True))
            elif start_platform[4] == 1 and end_platform[4] == 2:
                bloor_distance = stop_distance(start, 14414)
                george_distance = stop_distance(start, 14426)
                if bloor_distance < george_distance:
                    route = (find_direct_route(start, 14414, True),
                             find_direct_route(14485, end, True))
                else:
                    route = (find_direct_route(start, 14426, True),
                             find_direct_route(14483, end, True))
            elif start_platform[4] == 2 and end_platform[4] == 1:
                bloor_distance = stop_distance(end, 14414)
                george_distance = stop_distance(end, 14426)
                if bloor_distance < george_distance:
                    route = (find_direct_route(start, 14485, True),
                             find_direct_route(14414, end, True))
                else:
                    route = (find_direct_route(start, 14483, True),
                             find_direct_route(14426, end, True))
            elif start_platform[4] == 1 and end_platform[4] == 3:
                bloor_distance = stop_distance(start, 14414)
                george_distance = stop_distance(start, 14426)
                if bloor_distance < george_distance:
                    route = (find_direct_route(start, 14414, True),
                             find_direct_route(14485, 14498, True),
                             find_direct_route(14546, end, True))
                else:
                    route = (find_direct_route(start, 14426, True),
                             find_direct_route(14483, 14498, True),
                             find_direct_route(14546, end, True))
            elif start_platform[4] == 3 and end_platform[4] == 1:
                bloor_distance = stop_distance(end, 14414)
                george_distance = stop_distance(end, 14426)
                if bloor_distance < george_distance:
                    route = (find_direct_route(start, 14546, True),
                             find_direct_route(14498, 14485, True),
                             find_direct_route(14426, end, True))
                else:
                    route = (find_direct_route(start, 14546, True),
                             find_direct_route(14498, 14483, True),
                             find_direct_route(14426, end, True))
            elif start_platform[4] == 4 and end_platform[4] == 2:
                route = (find_direct_route(start, 14539, True),
                         find_direct_route(14406, 14414, True),
                         find_direct_route(14485, end, True))
            elif start_platform[4] == 2 and end_platform[4] == 4:
                route = (find_direct_route(start, 14485, True),
                         find_direct_route(14414, 14406, True),
                         find_direct_route(14539, end, True))
            elif start_platform[4] == 4 and end_platform[4] == 3:
                route = (find_direct_route(start, 14539, True),
                         find_direct_route(14406, 14414, True),
                         find_direct_route(14485, 14498, True),
                         find_direct_route(14546, end, True))
            elif start_platform[4] == 3 and end_platform[4] == 4:
                route = (find_direct_route(start, 14546, True),
                         find_direct_route(14498, 14485, True),
                         find_direct_route(14414, 14406, True),
                         find_direct_route(14539, end, True))
    for i in route:
        all_routes.append(i)

    valid_routes = []
    for i in all_routes:
        if [] not in i:
            valid_routes.append([i[0]])
    return valid_routes


def truncate_walk_steps(steps):
    cleaned_steps = []

    truncate_beginning_index = find_all_walks(steps)

    if len(truncate_beginning_index) != 0:
        for i in steps[:truncate_beginning_index[0]]:
            cleaned_steps.append(i)

        for every_tru in truncate_beginning_index:

            ending_index = 0
            index = every_tru

            for step in steps[every_tru:]:

                if type(step[0]) != tuple and step[0][3] != -1:
                    ending_index = index - 1
                    break
                else:
                    ending_index = index
                index += 1

            new_walk_instru = [(steps[every_tru][0][0], steps[ending_index][0][1], 'walking', -1)]

            cleaned_steps.append(new_walk_instru)

            if every_tru != truncate_beginning_index[-1]:
                for the_rest in steps[
                                ending_index + 1:truncate_beginning_index[
                                    truncate_beginning_index.index(every_tru) + 1]]:
                    cleaned_steps.append(the_rest)
    else:
        return steps

    return cleaned_steps


def find_all_walks(steps):
    index_counter = 0

    walk_start_index = []
    final_output = []

    for i in steps:
        if type(i[0]) == tuple and i[0][3] == -1:
            if index_counter + 1 < len(steps) - 1:
                next_step = steps[index_counter + 1]
                if type(next_step[0]) == tuple and next_step[0][3] == -1:
                    walk_start_index.append(index_counter)

        index_counter += 1

    for e in walk_start_index:
        if (e - 1) not in walk_start_index:
            final_output.append(e)

    return final_output


def flatten_tuple(tuple_to_flat):
    list_of_tuple = []

    list_tuple = flatten_tuple_recur(tuple_to_flat, list_of_tuple)
    list_tuple.reverse()

    return list_tuple


def flatten_tuple_recur(tuple_to_flat, list_of_tuple):
    if type(tuple_to_flat[1]) == tuple:
        list_of_tuple.append(tuple_to_flat[1])
        flatten_tuple_recur(tuple_to_flat[0], list_of_tuple)
    else:
        list_of_tuple.append(tuple_to_flat)

    return list_of_tuple


def flatten_tuple_in_sub(tuple_to_flat):
    list_of_tuple = []

    list_tuple = flatten_tuple_in_sub_recur(tuple_to_flat, list_of_tuple)
    list_tuple.reverse()

    list_out = []

    for i in list_tuple:
        if type(i) == list:
            for j in i:
                list_out.append(j)
        else:
            list_out.append(i)

    return list_out


def flatten_tuple_in_sub_recur(tuple_to_flat, list_of_tuple):
    if type(tuple_to_flat[0]) != list:
        if type(tuple_to_flat[1]) == tuple:
            list_of_tuple.append(tuple_to_flat[1])
            flatten_tuple_in_sub_recur(tuple_to_flat[0], list_of_tuple)
        else:
            list_of_tuple.append(tuple_to_flat)
    else:
        var = tuple_to_flat[0]
        list_of_tuple.append(tuple_to_flat[1])
        list_of_tuple.append(var)

    return list_of_tuple


def all_routes_finder(to_start_sub, sub, from_end_sub):
    # Final output
    all_pos_routes = []

    # Combining all walking steps first
    to_sub = truncate_walk_steps(to_start_sub)
    from_sub = truncate_walk_steps(from_end_sub)

    # Finds all permutations to get to the subway
    print("\nFinding permutation going to the subway...")

    i = 0
    to_sub_all = to_sub[i][0]
    unique_combinations = []
    to_sub_final = []

    while i < len(to_sub) - 1:
        if type((to_sub[i + 1][0])) == tuple:

            exp_temp = [(to_sub[i + 1][0])]

            for r in itertools.product(to_sub_all, exp_temp):
                unique_combinations.append(r)

            to_sub_all = unique_combinations
            unique_combinations = []

        else:

            for r in itertools.product(to_sub_all, to_sub[i + 1][0]):
                unique_combinations.append(r)

            to_sub_all = unique_combinations
            unique_combinations = []

        i += 1

    if type(to_sub_all) != tuple:
        for each_sub in to_sub_all:
            to_sub_final.append(flatten_tuple(each_sub))
    else:
        to_sub_final.append(to_sub_all)

    print("Total ways to go to the subway station from starting location: " + str(len(to_sub_final)))

    # Finds all permutations in the subway
    print("\nFinding permutation going to and within the subway...")

    i = 0
    unique_combinations = []
    in_sub_final = []

    # Old format subway permutation code
    # while j < len(sub):
    #     for r in itertools.product(to_sub_final, sub[j]):
    #         unique_combinations.append(r)
    #
    #     to_sub_final = unique_combinations
    #     unique_combinations = []
    #
    #     # print("total count: " + str(len(to_sub_all)))
    #     # print("\n")
    #
    #     j += 1

    while i < len(sub):

        if type((sub[i][0])) == tuple:

            exp_temp = [(sub[i][0])]

            for r in itertools.product(to_sub_final, exp_temp):
                unique_combinations.append(r)

            to_sub_final = unique_combinations
            unique_combinations = []

        else:
            for r in itertools.product(to_sub_final, sub[i][0]):
                unique_combinations.append(r)

            to_sub_final = unique_combinations
            unique_combinations = []

        i += 1

    for every_sub in to_sub_final:
        in_sub_final.append(flatten_tuple_in_sub(every_sub))

    print("Total permutation going to and within the subway: " + str(len(in_sub_final)))

    # Finds all permutations to the final destination from the subway
    print("\nFinding permutation going to the destination from the subway...")

    i = 0
    unique_combinations = []

    while i < len(from_sub):

        if type((from_sub[i][0])) == tuple:

            exp_temp = [(from_sub[i][0])]

            for r in itertools.product(in_sub_final, exp_temp):
                unique_combinations.append(r)

            in_sub_final = unique_combinations
            unique_combinations = []

        else:
            for r in itertools.product(in_sub_final, from_sub[i][0]):
                unique_combinations.append(r)

            in_sub_final = unique_combinations
            unique_combinations = []

        i += 1

    for each_sub in in_sub_final:
        all_pos_routes.append(flatten_tuple_in_sub(each_sub))

    print("Total ways to go from initial location to destination: " + str(len(all_pos_routes)))

    return all_pos_routes


os.system(clearTermial)


def get_trips(info):
    # final output
    all_routes = []
    # User input test
    # info = get_input()
    # test case
    # info = Input((4308, ((12, 0),(12, 0))), (760, ((20, 0),(20, 0))), 19, True, 20,[],5)
    # info = Input((14238, ((12, 0),(12, 0))), (760, ((20, 0),(20, 0))), 19, True, 20,[],5)
    # info = Input((3169, ((12, 0),(12, 0))), (465, ((20, 0),(20, 0))), 19, True, 20,[],5)
    # info = Input((465, ((12, 0), (12, 0))), (3169, ((20, 0), (20, 0))), 19, True, 20, [], 5)
    print_info(info)

    direct_routes = [find_direct_route(info.starting_stop.stop_id, info.ending_stop.stop_id, True)]
    if direct_routes[0] != [[]]:

        for i in direct_routes:

            if type(i[0]) == list:
                for j in i[0]:
                    all_routes.append([j])
            else:
                all_routes.append([i[0]])

        return all_routes

        print("--------------------------------")
    else:
        print("No Direct Routes Found ...\n\nLooking for subway path ...\n")
        start_subway = find_closest_subway(info.starting_stop.stop_id)
        end_subway = find_closest_subway(info.ending_stop.stop_id)
        subway = navigate_subway(start_subway, end_subway)
        to_start_subway = []
        to_start_subway.append(find_direct_route(info.starting_stop.stop_id, start_subway, True))
        if to_start_subway[0] == [[]]:
            print("No direct route from start to subway stop...\n\nLooking for alternatives...\n")
            route_from_start = []
            to_start_subway = []
            closest_to_start = find_closest_stop(info.starting_stop.stop_id, start_subway, [])
            prev_closest = closest_to_start[0]
            closest_to_subway = find_direct_route(info.starting_stop.stop_id, closest_to_start[0], True)
            route_from_start.append([closest_to_subway[0]])
            found_route = False
            while found_route == False:
                direct = find_direct_route(closest_to_start[0], start_subway, True)
                if direct[0] != []:
                    found_route = True
                    route_from_start.append(direct)
                else:
                    closest_to_start = find_closest_stop(closest_to_start[0], start_subway, closest_to_start[1])
                    route_from_start.append(find_direct_route(prev_closest, closest_to_start[0], True))
                    prev_closest = closest_to_start[0]
            to_start_subway = route_from_start

        from_end_subway = []
        from_end_subway.append(find_direct_route(end_subway, info.ending_stop.stop_id, True))
        if from_end_subway[0] == [[]]:
            print("No direct route from subway to ending stop...\n\nLooking for alternatives...\n")
            route_to_end = []
            from_end_subway = []
            closest_to_end = find_closest_stop(end_subway, info.ending_stop.stop_id, [])
            prev_closest = closest_to_end[0]
            near = nearby_stops(end_subway)
            subway_to_closest = close_to_end(closest_to_end[0], near)
            route_to_end.append([subway_to_closest[0]])
            found_route = False
            while found_route == False:
                direct = find_direct_route(closest_to_end[0], info.ending_stop.stop_id, True)
                if direct[0] != []:
                    found_route = True
                    route_to_end.append(direct)
                else:
                    closest_to_end = find_closest_stop(closest_to_end[0], info.ending_stop.stop_id, closest_to_end[1])
                    route_to_end.append(find_direct_route(prev_closest, closest_to_end[0], True))
                    prev_closest = closest_to_end[0]
            from_end_subway = route_to_end
        route = []

        print("--------------------------------")
        for i in to_start_subway:
            print(i)
            if type(i[0]) == list:
                print(len(i[0]))
            else:
                print(1)
        print("--------------------------------")
        for i in subway:
            print(i)
            if type(i[0]) == list:
                print(len(i[0]))
            else:
                print(1)
        print("--------------------------------")
        for i in from_end_subway:
            print(i)
            if type(i[0]) == list:
                print(len(i[0]))
            else:
                print(1)
        print("--------------------------------\n")

        if type(to_start_subway[0]) == tuple:
            all_routes = all_routes_finder([to_start_subway], subway, from_end_subway)
        else:
            all_routes = all_routes_finder(to_start_subway, subway, from_end_subway)

        return all_routes
