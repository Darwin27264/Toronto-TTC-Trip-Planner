import sqlite3
import os

# Importing database
data_trip = sqlite3.connect('trips.db')
t = data_trip.cursor()
data_route = sqlite3.connect('routes.db')
r = data_route.cursor()
data_stop = sqlite3.connect('stops.db')
s = data_stop.cursor()
data_subway = sqlite3.connect('subway.db')
m = data_subway.cursor()

sample_output = [(3169, 14242, 'start_to_close', 61329, 3), (14529, 14498, 'direct', 61457, 1),
                 (14546, 14552, 'direct', 61458, 1), (9276, 8000, 'close_to_end', 61363, 3),
                 (4049, 574, 'close_to_close', 61367, 3), (9230, 467, 'close_to_close', 61431, 3)]


def get_stop_times(one_possible_route):
    # For the every step in one possible route, from point a to point b
    for step in one_possible_route:
        cur_route_id = step[3]
        print(cur_route_id)

        # Finding route direction
        t.execute("SELECT * FROM trips WHERE route_id=:route_id", {'route_id': cur_route_id})
        to_test = t.fetchone()[3]
        route_direction = check_direction(to_test, step[0], step[1])

        all_matching_routes = t.execute("SELECT * FROM trips WHERE route_id=:route_id",
                                        {'route_id': cur_route_id})

        all_matching_routes_cur_order = []

        tmp = all_matching_routes.fetchall()

        print(len(tmp))
        print(tmp[0])

        for j in tmp:
            print(j[5])
            print(route_direction)
            if j[5] == route_direction:
                all_matching_routes_cur_order.append(j)
            elif route_direction == -1:
                print("No matching stops in this trip found")

        print(all_matching_routes_cur_order)

        break


def check_direction(sample_route_order, start_stop_id, end_stop_id):
    print(sample_route_order)
    print(start_stop_id)
    print(end_stop_id)

    for i in sample_route_order:
        if i == start_stop_id:
            return 0
        elif i == end_stop_id:
            return 1
        else:
            return -1


get_stop_times(sample_output)
