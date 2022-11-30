import ast
import sqlite3

# Importing database
data_trip = sqlite3.connect('trips.db')
t = data_trip.cursor()
data_route = sqlite3.connect('routes.db')
r = data_route.cursor()
data_stop = sqlite3.connect('stops.db')
s = data_stop.cursor()
data_subway = sqlite3.connect('subway.db')
m = data_subway.cursor()

# sample_output = [(3169, 14242, 'start_to_close', 61329, 3), (14529, 14498, 'direct', 61457, 1),
#                  (14546, 14552, 'direct', 61458, 1), (9276, 8000, 'close_to_end', 61363, 3),
#                  (4049, 574, 'close_to_close', 61367, 3), (9230, 467, 'close_to_close', 61431, 3)]
sample_output = [(14529, 14498, 'direct', 61457, 1),
                 (14546, 14552, 'direct', 61458, 1), (9276, 8000, 'close_to_end', 61363, 3),
                 (4049, 574, 'close_to_close', 61367, 3), (9230, 467, 'close_to_close', 61431, 3)]


def get_stop_times(one_possible_route):
    one_possible_route_wt_time = []

    # For the every step in one possible route, from point a to point b
    for step in one_possible_route:
        route_direction = []

        start_stop_id = step[0]
        end_stop_id = step[1]

        cur_route_id = step[3]

        # Finding route direction
        t.execute("SELECT * FROM trips WHERE route_id=:route_id", {'route_id': cur_route_id})
        all_matching_routes = t.fetchall()

        for i in all_matching_routes:
            tmp_list = ast.literal_eval(i[3])
            if start_stop_id in tmp_list and end_stop_id in tmp_list:
                route_direction = check_direction(tmp_list, start_stop_id, end_stop_id)

        all_matching_routes_cor_order = []

        for j in all_matching_routes:
            tmp_list = ast.literal_eval(j[3])
            if j[5] == route_direction and start_stop_id in tmp_list and end_stop_id in tmp_list:
                all_matching_routes_cor_order.append(j)

        times = []

        for p in all_matching_routes_cor_order:
            index_str_stop_id = (ast.literal_eval(p[3])).index(start_stop_id)
            index_end_stop_id = (ast.literal_eval(p[3])).index(end_stop_id)

            start_time = (ast.literal_eval(p[2]))[index_str_stop_id]
            end_time = (ast.literal_eval(p[2]))[index_end_stop_id]

            time_out = (start_time, end_time)

            times.append(time_out)

        one_possible_route_wt_time.append((step, times))

        break

    return one_possible_route_wt_time


def check_direction(sample_route_order, start_stop_id, end_stop_id):

    for s in sample_route_order:
        if s == start_stop_id:
            return 0
        elif s == end_stop_id:
            return 1

    return -1


for i in get_stop_times(sample_output):
    print(i)
    print("\n")
