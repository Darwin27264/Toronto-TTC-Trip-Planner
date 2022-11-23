import sqlite3
import os
import json

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


def starting_route_stops(info):
    return_value = False
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': info.starting_stop.stop_id})
    starting_point = s.fetchone()
    for i in binary_to_dict(starting_point[4]):
        r.execute("SELECT * FROM routes WHERE route_id=:route_id",{'route_id': i})
        route = r.fetchone()
        if str(info.ending_stop.stop_id) in binary_to_dict(route[4]): return_value = True
    return return_value


os.system(clearTermial)
print("test")
info = get_input()
print_info(info)
print(starting_route_stops(info))