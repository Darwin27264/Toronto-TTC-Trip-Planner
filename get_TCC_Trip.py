import sqlite3
import os
import json
import math

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


def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    binary = ' '.join(format(ord(letter), 'b') for letter in str)
    return binary


def binary_to_dict(the_binary):
    jsn = ''.join(chr(int(x, 2)) for x in the_binary.split())
    d = json.loads(jsn)
    return d


def stop_distance(stop1, stop2):
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': stop1})
    stop1 = s.fetchone()
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': stop2})
    stop2 = s.fetchone()
    return math.sqrt(pow(stop1[2] - stop2[2], 2) + pow(stop1[3] - stop2[3], 2))


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
                valid_routes.append((start, j, "start_to_close", route[1], route[2]))
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
                valid_routes.append((i, end, "close_to_end", route[1], route[2]))
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
                    valid_routes.append((i, k, "close_to_close", route[1], route[2]))
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
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': start})
    starting_point = s.fetchone()
    for i in binary_to_dict(starting_point[4]):
        r.execute("SELECT * FROM routes WHERE route_id=:route_id", {'route_id': i})
        route = r.fetchone()
        if str(end) in binary_to_dict(route[4]): valid_routes.append((start, end, 'direct', route[1], route[2]))
    if val:
        close_routes = find_close_direct_route(start, end)
        return valid_routes + close_routes
    else:
        return valid_routes


def make_stops_dict(stop):
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': stop})
    stop = s.fetchone()
    all_stops = {}
    for i in binary_to_dict(stop[4]):
        r.execute("SELECT * FROM routes WHERE route_id=:route_id", {'route_id': i})
        route = r.fetchone()
        for j in binary_to_dict(route[4]):
            all_stops[j] = 0
    print(all_stops)
    return all_stops


def navigate_subway(start, end):
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
                all_routes.append(find_direct_route(start, end, False))
            elif start_platform[4] == 1 and end_platform[4] == 4:
                all_routes.append((find_direct_route(start, 14465, False),
                                   find_direct_route(14530, end, False)))
            elif start_platform[4] == 4 and end_platform[4] == 1:
                all_routes.append((find_direct_route(start, 14539, False),
                                   find_direct_route(14406, end, False)))
            elif start_platform[4] == 2 and end_platform[4] == 3:
                all_routes.append((find_direct_route(start, 14498, False),
                                   find_direct_route(14546, end, False)))
            elif start_platform[4] == 3 and end_platform[4] == 2:
                all_routes.append((find_direct_route(start, 14546, False),
                                   find_direct_route(14498, end, False)))
            elif start_platform[4] == 1 and end_platform[4] == 2:
                bloor_distance = stop_distance(start, 14414)
                george_distance = stop_distance(start, 14426)
                if bloor_distance < george_distance:
                    all_routes.append((find_direct_route(start, 14414, False),
                                       find_direct_route(14485, end, False)))
                else:
                    all_routes.append((find_direct_route(start, 14426, False),
                                       find_direct_route(14483, end, False)))
            elif start_platform[4] == 2 and end_platform[4] == 1:
                bloor_distance = stop_distance(end, 14414)
                george_distance = stop_distance(end, 14426)
                if bloor_distance < george_distance:
                    all_routes.append((find_direct_route(start, 14485, False),
                                       find_direct_route(14414, end, False)))
                else:
                    all_routes.append((find_direct_route(start, 14483, False),
                                       find_direct_route(14426, end, False)))
            elif start_platform[4] == 1 and end_platform[4] == 3:
                bloor_distance = stop_distance(start, 14414)
                george_distance = stop_distance(start, 14426)
                if bloor_distance < george_distance:
                    all_routes.append((find_direct_route(start, 14414, False),
                                       find_direct_route(14485, 14498, False),
                                       find_direct_route(14546, end, False)))
                else:
                    all_routes.append((find_direct_route(start, 14426, False),
                                       find_direct_route(14483, 14498, False),
                                       find_direct_route(14546, end, False)))
            elif start_platform[4] == 3 and end_platform[4] == 1:
                bloor_distance = stop_distance(end, 14414)
                george_distance = stop_distance(end, 14426)
                if bloor_distance < george_distance:
                    all_routes.append((find_direct_route(start, 14546, False),
                                       find_direct_route(14498, 14485, False),
                                       find_direct_route(14426, end, False)))
                else:
                    all_routes.append((find_direct_route(start, 14546, False),
                                       find_direct_route(14498, 14483, False),
                                       find_direct_route(14426, end, False)))
            elif start_platform[4] == 4 and end_platform[4] == 2:
                all_routes.append((find_direct_route(start, 14539, False),
                                   find_direct_route(14406, 14414, False),
                                   find_direct_route(14485, end, False)))
            elif start_platform[4] == 2 and end_platform[4] == 4:
                all_routes.append((find_direct_route(start, 14485, False),
                                   find_direct_route(14414, 14406, False),
                                   find_direct_route(14539, end, False)))
            elif start_platform[4] == 4 and end_platform[4] == 3:
                all_routes.append((find_direct_route(start, 14539, False),
                                   find_direct_route(14406, 14414, False),
                                   find_direct_route(14485, 14498, False),
                                   find_direct_route(14546, end, False)))
            elif start_platform[4] == 3 and end_platform[4] == 4:
                all_routes.append((find_direct_route(start, 14546, False),
                                   find_direct_route(14498, 14485, False),
                                   find_direct_route(14414, 14406, False),
                                   find_direct_route(14539, end, False)))
    for i in all_routes:
        print(i)


os.system(clearTermial)

# # Testing Same Line
# print("--------------------------------")
# navigate_subway(14404,15699)
# print("--------------------------------")
# navigate_subway(14473,14505)
# print("--------------------------------")
# navigate_subway(14544,14551)
# print("--------------------------------")
# navigate_subway(14532,14538)

# # Testing Lines 1 to 4 and 4 to 1
# print("--------------------------------")
# navigate_subway(14404,14533)
# print("--------------------------------")
# navigate_subway(14533,14404)

# # Testing Lines 2 to 3 and 3 to 2
# print("--------------------------------")
# navigate_subway(14468,14549)
# print("--------------------------------")
# navigate_subway(14549,14468)

# # Testing Lines 1 to 2
# print("--------------------------------")
# navigate_subway(14404,14468)
# print("--------------------------------")
# navigate_subway(15699,14468)
# print("--------------------------------")
# navigate_subway(14404,14498)
# print("--------------------------------")
# navigate_subway(15699,14498)
# print("--------------------------------")
# navigate_subway(14421,14468)
# print("--------------------------------")
# navigate_subway(14419,14468)
# print("--------------------------------")
# navigate_subway(14421,14498)
# print("--------------------------------")
# navigate_subway(14419,14498)

# # Testing Lines 2 to 1
# print("--------------------------------")
# navigate_subway(14468,14404)
# print("--------------------------------")
# navigate_subway(14468,15699)
# print("--------------------------------")
# navigate_subway(14498,14404)
# print("--------------------------------")
# navigate_subway(14498,15699)
# print("--------------------------------")
# navigate_subway(14468,14421)
# print("--------------------------------")
# navigate_subway(14468,14419)
# print("--------------------------------")
# navigate_subway(14498,14421)
# print("--------------------------------")
# navigate_subway(14498,14419)

# # Testing Lines 3 to 1
# print("--------------------------------")
# navigate_subway(14550,14404)
# print("--------------------------------")
# navigate_subway(14550,15699)
# print("--------------------------------")
# navigate_subway(14550,14452)
# print("--------------------------------")
# navigate_subway(14550,14450)

# # Testing Lines 1 to 3
# print("--------------------------------")
# navigate_subway(14404,14550)
# print("--------------------------------")
# navigate_subway(15699,14550)
# print("--------------------------------")
# navigate_subway(14452,14550)
# print("--------------------------------")
# navigate_subway(14450,14550)

# # Testing Lines 2 to 4 and 4 to 2
# print("--------------------------------")
# navigate_subway(14468,14536)
# print("--------------------------------")
# navigate_subway(14499,14536)
# print("--------------------------------")
# navigate_subway(14536,14468)
# print("--------------------------------")
# navigate_subway(14536,14499)

# Testing Lines 3 to 4 and 4 to 3
# print("--------------------------------")
# navigate_subway(14531,14545)
# print("--------------------------------")
# navigate_subway(14545,14531)


# User input test
# info = get_input()
# print_info(info)
# direct_routes = find_direct_route(info.starting_stop.stop_id,info.ending_stop.stop_id,True)
# if len(direct_routes)!=0:
#     print(direct_routes)
# else:
#     stops_dict = make_stops_dict(info.ending_stop.stop_id)
#     for i in stops_dict:
#         alt_route = find_direct_route(info.starting_stop.stop_id,int(i),False)
#         if len(alt_route)!=0:
#             print(alt_route)
#         else:
#             print(i)
# print("--------------------------------")

# Direct Route Test
# info = Input((4308, ((12, 0),(12, 0))), (760, ((20, 0),(20, 0))), 19, True, 20,[])
# print_info(info)
# direct_routes = find_direct_route(info.starting_stop.stop_id,info.ending_stop.stop_id,True)
# print(direct_routes)
# print("--------------------------------")

# Start to Close Test
# info = Input((3169, ((12, 0),(12, 0))), (14235, ((20, 0),(20, 0))), 19, True, 20,[])
# print_info(info)
# direct_routes = find_direct_route(info.starting_stop.stop_id,info.ending_stop.stop_id,True)
# print(direct_routes)
# print("--------------------------------")

# Close to End Test
# info = Input((14235, ((12, 0),(12, 0))), (3169, ((20, 0),(20, 0))), 19, True, 20,[])
# print_info(info)
# direct_routes = find_direct_route(info.starting_stop.stop_id,info.ending_stop.stop_id,True)
# print(direct_routes)
# print("--------------------------------")

# Close to Close Test
# info = Input((9227, ((12, 0),(12, 0))), (3390, ((20, 0),(20, 0))), 19, True, 20,[])
# print_info(info)
# direct_routes = find_direct_route(info.starting_stop.stop_id,info.ending_stop.stop_id,True)
# print(direct_routes)
# print("--------------------------------")

# Alternative Route
# info = Input((4308, ((12, 0),(12, 0))), (465, ((20, 0),(20, 0))), 19, True, 20,[])
# print_info(info)
# direct_routes = find_direct_route(info.starting_stop.stop_id,info.ending_stop.stop_id,True)
# if len(direct_routes)!=0:
#     print(direct_routes)
# else:
#     stops_dict = make_stops_dict(info.ending_stop.stop_id)
#     for i in stops_dict:
#         alt_route = find_direct_route(info.starting_stop.stop_id,int(i),False)
#         if len(alt_route)!=0:
#             print(alt_route)
#         else:
#             print(i)
# print("--------------------------------")


# s.execute("SELECT * FROM stops")
# stops = s.fetchall()
# # num_routes = {}
# # for i in stops:
# #     num_routes[len(binary_to_dict(i[4]))] = 0
# # for i in stops:
# #     num_routes[len(binary_to_dict(i[4]))] = num_routes.get(len(binary_to_dict(i[4])))+1
# # print(num_routes)
# list6 = []
# list7 = []
# list8 = []
# list9 = []
# list10 = []
# list11 = []
# for i in stops:
#     if len(binary_to_dict(i[4]))==6:
#         list6.append((i[1],i[2],i[3]))
#     elif len(binary_to_dict(i[4]))==7:
#         list7.append((i[1],i[2],i[3]))
#     elif len(binary_to_dict(i[4]))==8:
#         list8.append((i[1],i[2],i[3]))
#     elif len(binary_to_dict(i[4]))==9:
#         list9.append((i[1],i[2],i[3]))
#     elif len(binary_to_dict(i[4]))==10:
#         list10.append((i[1],i[2],i[3]))
#     elif len(binary_to_dict(i[4]))==11:
#         list11.append((i[1],i[2],i[3]))

# for i in list6:
#     print(i)

# r.execute("SELECT * FROM routes WHERE route_id=:route_id",{'route_id': 61456})
# route = r.fetchall()
# subway_stops = {}
# for i in route:
#     stops = binary_to_dict(i[4])
#     for j in stops:
#         subway_stops[j] = 0
# for i in subway_stops:
#     s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': int(i)})
#     stop = s.fetchall()
#     for j in stop:
#         print((j[1],j[2],j[3]))
