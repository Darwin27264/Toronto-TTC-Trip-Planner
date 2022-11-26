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
    return math.sqrt(pow(stop1[2] - stop2[2], 2) + pow(stop1[3] - stop2[3], 2))*110.947


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
    check_for_walk = stop_distance(start,end)
    if check_for_walk < 0.2:
        return [(start,end,'walking',-1)]
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

def find_closest_stop(start,end,used_stops):
    dict_stops = make_stops_dict(start)
    if int(list(dict_stops)[0]) != start and int(list(dict_stops)[0]) not in used_stops:
        closest = int(list(dict_stops)[0])
    elif int(list(dict_stops)[1]) not in used_stops:
        closest = int(list(dict_stops)[1])
    else: 
        closest = int(list(dict_stops)[2])
    for i in dict_stops:
        if stop_distance(end,int(i)) < stop_distance(end,closest) and int(i) != start and int(i) not in used_stops:
            s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': int(i)})
            stop_info = s.fetchone()
            if len(binary_to_dict(stop_info[4])) >=3:
                closest = int(i)
    used_stops.append(closest)
    return (closest,used_stops)
               

def find_closest_subway(stop):
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': stop})
    stop_info = s.fetchone()
    m.execute("SELECT * FROM subways")
    all_subway = m.fetchall()
    closest = all_subway[0]
    for i in all_subway:
        if stop_distance(stop_info[0],i[0]) < stop_distance(stop_info[0],closest[0]):
            closest = i
    return closest[0]


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
                route=(find_direct_route(start, end, False))
            elif start_platform[4] == 1 and end_platform[4] == 4:
                route=(find_direct_route(start, 14465, False),
                                   find_direct_route(14530, end, False))
            elif start_platform[4] == 4 and end_platform[4] == 1:
                route=(find_direct_route(start, 14539, False),
                                   find_direct_route(14406, end, False))
            elif start_platform[4] == 2 and end_platform[4] == 3:
                route=(find_direct_route(start, 14498, False),
                                   find_direct_route(14546, end, False))
            elif start_platform[4] == 3 and end_platform[4] == 2:
                route=(find_direct_route(start, 14546, False),
                                   find_direct_route(14498, end, False))
            elif start_platform[4] == 1 and end_platform[4] == 2:
                bloor_distance = stop_distance(start, 14414)
                george_distance = stop_distance(start, 14426)
                if bloor_distance < george_distance:
                    route=(find_direct_route(start, 14414, False),
                                       find_direct_route(14485, end, False))
                else:
                    route=(find_direct_route(start, 14426, False),
                                       find_direct_route(14483, end, False))
            elif start_platform[4] == 2 and end_platform[4] == 1:
                bloor_distance = stop_distance(end, 14414)
                george_distance = stop_distance(end, 14426)
                if bloor_distance < george_distance:
                    route=(find_direct_route(start, 14485, False),
                                       find_direct_route(14414, end, False))
                else:
                    route=(find_direct_route(start, 14483, False),
                                       find_direct_route(14426, end, False))
            elif start_platform[4] == 1 and end_platform[4] == 3:
                bloor_distance = stop_distance(start, 14414)
                george_distance = stop_distance(start, 14426)
                if bloor_distance < george_distance:
                    route=(find_direct_route(start, 14414, False),
                                       find_direct_route(14485, 14498, False),
                                       find_direct_route(14546, end, False))
                else:
                    route=(find_direct_route(start, 14426, False),
                                       find_direct_route(14483, 14498, False),
                                       find_direct_route(14546, end, False))
            elif start_platform[4] == 3 and end_platform[4] == 1:
                bloor_distance = stop_distance(end, 14414)
                george_distance = stop_distance(end, 14426)
                if bloor_distance < george_distance:
                    route=(find_direct_route(start, 14546, False),
                                       find_direct_route(14498, 14485, False),
                                       find_direct_route(14426, end, False))
                else:
                    route =(find_direct_route(start, 14546, False),
                                       find_direct_route(14498, 14483, False),
                                       find_direct_route(14426, end, False))
            elif start_platform[4] == 4 and end_platform[4] == 2:
                route = (find_direct_route(start, 14539, False),
                                   find_direct_route(14406, 14414, False),
                                   find_direct_route(14485, end, False))
            elif start_platform[4] == 2 and end_platform[4] == 4:
                route = (find_direct_route(start, 14485, False),
                                   find_direct_route(14414, 14406, False),
                                   find_direct_route(14539, end, False))
            elif start_platform[4] == 4 and end_platform[4] == 3:
                route = (find_direct_route(start, 14539, False),
                                   find_direct_route(14406, 14414, False),
                                   find_direct_route(14485, 14498, False),
                                   find_direct_route(14546, end, False))
            elif start_platform[4] == 3 and end_platform[4] == 4:
                route = (find_direct_route(start, 14546, False),
                                   find_direct_route(14498, 14485, False),
                                   find_direct_route(14414, 14406, False),
                                   find_direct_route(14539, end, False))
    for i in route:
                all_routes.append(i)           
                    
    empty_list = []
    valid_routes = []
    for i in all_routes:
        if empty_list not in i:
            valid_routes.append(i[0])
    return valid_routes


os.system(clearTermial)

# User input test
info = get_input()
print_info(info)
direct_routes = find_direct_route(info.starting_stop.stop_id,info.ending_stop.stop_id,True)
if len(direct_routes)!=0:
    for i in direct_routes:
        print(i)
else:
    print("No Direct Routes Found ... Looking for subway path ...")
    start_subway = find_closest_subway(info.starting_stop.stop_id)
    end_subway = find_closest_subway(info.ending_stop.stop_id)
    print(end_subway)
    subway = navigate_subway(start_subway,end_subway)
    to_start_subway = find_direct_route(info.starting_stop.stop_id,start_subway,True)
    if to_start_subway == []:
        closest_to_start = find_closest_stop(info.starting_stop.stop_id,start_subway)
        to_start_subway = find_direct_route(info.starting_stop.stop_id,closest_to_start,False)+ find_direct_route(closest_to_start,start_subway,True)
    from_end_subway = find_direct_route(end_subway,info.ending_stop.stop_id,True)
    if from_end_subway == []:
        closest_to_end = find_closest_stop(end_subway,info.ending_stop.stop_id,[])
        print(closest_to_end)
        near = nearby_stops(end_subway)
        test = close_to_end(closest_to_end[0],near)
        test2 = find_direct_route(closest_to_end[0],info.ending_stop.stop_id,True)
        print(test)
        print(test2)
        from_end_subway = test + test2
    print(to_start_subway)
    print("--------------------------------")
    print(subway)
    print("--------------------------------")
    print(from_end_subway)
    
    
print("--------------------------------")
