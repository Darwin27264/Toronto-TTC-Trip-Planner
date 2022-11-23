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


def start_to_close(start, end):
    """
    Summary:
        check if a stop within 200 meters of the ending stop 
        has a direct route from the starting stop

    Args:
        start: starting stop_id
        end: ending stop_id

    Returns:
        if a route is found under the conditions above, then
        the function will return a tuple of the starting stop,
        new ending stop, and then the string "start_to_close",
        and the route name
    """
    near_end_stops = nearby_stops(end)
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': start})
    starting_point = s.fetchone()
    for i in binary_to_dict(starting_point[4]):
        r.execute("SELECT * FROM routes WHERE route_id=:route_id",{'route_id': i})
        route = r.fetchone()
        list_close = []
        for j in near_end_stops:
            if str(j) in binary_to_dict(route[4]): 
                list_close.append(j)
        if len(list_close)!=0:
            closest = list_close[0]
            for k in list_close:
                if stop_distance(start,k) < closest:
                    closest = k
            return (start,closest,"start_to_close",route[1])
        else: return False

def close_to_end(start, end):
    """
    Summary:
        check if a stop within 200 meters of the starting stop
        goes to the ending stop

    Args:
        start: starting stop_id
        end: ending stop_id

    Returns:
        if a route is found under the conditions above, then
        the function will return a tuple of the new starting stop,
        ending stop, the string "close_to_end", and the route name
    """
    near_start_stops = nearby_stops(start)
    list_close = []
    for i in near_start_stops:
        s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': i})
        starting_point = s.fetchone()
        for j in binary_to_dict(starting_point[4]):
            r.execute("SELECT * FROM routes WHERE route_id=:route_id",{'route_id': j})
            route = r.fetchone()
            if str(end) in binary_to_dict(route[4]):
                list_close.append(i)
    if len(list_close)!=0:
        closest = list_close[0]
        for k in list_close:
                if stop_distance(start,k) < closest:
                    closest = k
        return (closest,end,"close_to_end",route[1])
    else: return False


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
        the function will return a tuple of the starting stop,
        ending stop,then information about which stop has
        changed, and then the route name
    """
    route = start_to_close(start, end)
    if route != False: return route
    else: return close_to_end(start, end)
        


def find_direct_route(start,end):
    """
    Summary:
        check if there is a direct route from the starting
        stop to the ending stop

    Args:
        start: starting stop_id
        end: ending stop_id

    Returns:
        if a direct route is found then return a tuple
        of the starting stop, ending stop, the string
        'direct', and the route name
    """
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': start})
    starting_point = s.fetchone()
    for i in binary_to_dict(starting_point[4]):
        r.execute("SELECT * FROM routes WHERE route_id=:route_id",{'route_id': i})
        route = r.fetchone()
        if str(end) in binary_to_dict(route[4]): return (start,end,'direct',route[1])
    return False


os.system(clearTermial)
info = get_input()
# info = Input((14235, ((12, 0),(12, 0))), (3169, ((20, 0),(20, 0))), 19, True, 20,[])
print_info(info)
direct = find_direct_route(info.starting_stop.stop_id,info.ending_stop.stop_id)
if direct!=False:
    print(direct)
else:
    print(find_close_direct_route(info.starting_stop.stop_id,info.ending_stop.stop_id))