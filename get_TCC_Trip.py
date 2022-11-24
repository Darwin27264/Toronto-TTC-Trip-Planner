import sqlite3
import os
import json
import math 

# Import User Input Function
from get_User_Input import *

# importing output objects
from input import Input

# Importing database
data_trip = sqlite3.connect('trips.db')
t = data_trip.cursor()
data_route = sqlite3.connect('routes.db')
r = data_route.cursor()
data_stop = sqlite3.connect('stops.db')
s = data_stop.cursor()

def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    binary = ' '.join(format(ord(letter), 'b') for letter in str)
    return binary


def binary_to_dict(the_binary):
    jsn = ''.join(chr(int(x, 2)) for x in the_binary.split())
    d = json.loads(jsn)  
    return d

def stop_distance(stop1,stop2):
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': stop1})
    stop1 = s.fetchone()
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': stop2})
    stop2 = s.fetchone()
    return math.sqrt(pow(stop1[2]-stop2[2],2)+pow(stop1[3]-stop2[3],2))


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
        r.execute("SELECT * FROM routes WHERE route_id=:route_id",{'route_id': i})
        route = r.fetchone()
        for j in near_end_stops:
            if str(j) in binary_to_dict(route[4]): 
                valid_routes.append((start,j,"start_to_close",route[1],route[2]))
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
            r.execute("SELECT * FROM routes WHERE route_id=:route_id",{'route_id': j})
            route = r.fetchone()
            if str(end) in binary_to_dict(route[4]):
                valid_routes.append((i,end,"close_to_end",route[1],route[2]))
    return valid_routes

def close_to_close(near_start_stops,near_end_stops):
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
            r.execute("SELECT * FROM routes WHERE route_id=:route_id",{'route_id': j})
            route = r.fetchone()
            for k in near_end_stops:
                if str(k) in binary_to_dict(route[4]):
                    valid_routes.append((i,k,"close_to_close",route[1],route[2]))
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
    route3 = close_to_close(near_start_stops,near_end_stops)
    all_routes = []
    all_routes = route1 + route2 + route3
    return all_routes
        


def find_direct_route(start,end,val):
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
        r.execute("SELECT * FROM routes WHERE route_id=:route_id",{'route_id': i})
        route = r.fetchone()
        if str(end) in binary_to_dict(route[4]): valid_routes.append((start,end,'direct',route[1],route[2]))
    if val:
        close_routes = find_close_direct_route(start,end)
        return valid_routes + close_routes
    else: return valid_routes

def make_stops_dict(stop):
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': stop})
    stop = s.fetchone()
    all_stops = {}
    for i in binary_to_dict(stop[4]):
        r.execute("SELECT * FROM routes WHERE route_id=:route_id",{'route_id': i})
        route = r.fetchone()
        for j in binary_to_dict(route[4]):
            all_stops[j] = 0
    print(all_stops)
    return all_stops

os.system(clearTermial)
# User input test
info = get_input()
print_info(info)
direct_routes = find_direct_route(info.starting_stop.stop_id,info.ending_stop.stop_id,True)
if len(direct_routes)!=0:
    print(direct_routes)
else:
    stops_dict = make_stops_dict(info.ending_stop.stop_id)
    for i in stops_dict:
        alt_route = find_direct_route(info.starting_stop.stop_id,int(i),False)
        if len(alt_route)!=0:
            print(alt_route)
        else:
            print(i)
print("--------------------------------")

# Direct Route Test
# info = Input((4308, ((12, 0),(12, 0))), (760, ((20, 0),(20, 0))), 19, True, 20,[])
# print_info(info)
# direct_routes = find_direct_route(info.starting_stop.stop_id,info.ending_stop.stop_id)
# print(direct_routes)
# print("--------------------------------")

# Start to Close Test
# info = Input((3169, ((12, 0),(12, 0))), (14235, ((20, 0),(20, 0))), 19, True, 20,[])
# print_info(info)
# direct_routes = find_direct_route(info.starting_stop.stop_id,info.ending_stop.stop_id)
# print(direct_routes)
# print("--------------------------------")

# Close to End Test
# info = Input((14235, ((12, 0),(12, 0))), (3169, ((20, 0),(20, 0))), 19, True, 20,[])
# print_info(info)
# direct_routes = find_direct_route(info.starting_stop.stop_id,info.ending_stop.stop_id)
# print(direct_routes)
# print("--------------------------------")

# Close to Close Test
# info = Input((9227, ((12, 0),(12, 0))), (3390, ((20, 0),(20, 0))), 19, True, 20,[])
# print_info(info)
# direct_routes = find_direct_route(info.starting_stop.stop_id,info.ending_stop.stop_id)
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