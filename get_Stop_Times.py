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
# sample_output = [(14529, 14498, 'direct', 61457, 1),
#                  (14546, 14552, 'direct', 61458, 1), (9276, 8000, 'close_to_end', 61363, 3),
#                  (4049, 574, 'close_to_close', 61367, 3), (9230, 467, 'close_to_close', 61431, 3)]
sample_output = [(9276, 8000, 'close_to_end', 61363, 3),
                 (4049, 574, 'close_to_close', 61367, 3),
                 (9230, 467, 'close_to_close', 61431, 3)]


def get_route_id(route_id):
    t.execute("SELECT * FROM trips WHERE route_id=:route_id", {'route_id': route_id})
    all_matching_routes = t.fetchall()

    return all_matching_routes


def get_stop_times(one_possible_route):
    one_possible_route_wt_time = []

    # For the every step in one possible route, from point a to point b
    for step in one_possible_route:

        print(step)

        start_stop_id = step[0]
        end_stop_id = step[1]
        cur_route_id = step[3]

        # Finding route
        t.execute("SELECT * FROM trips WHERE route_id=:route_id", {'route_id': cur_route_id})
        all_matching_routes = t.fetchall()

        all_matching_routes_cor_order = []

        for j in all_matching_routes:
            tmp_list = ast.literal_eval(j[3])

            if check_contains(tmp_list, start_stop_id, end_stop_id):
                all_matching_routes_cor_order.append(j)

        times = []

        # Debugging code
        print("running...looking for route_id: " + str(cur_route_id) + "\n")

        for p in all_matching_routes_cor_order:
            print(p)

            index_str_stop_id = (ast.literal_eval(p[3])).index(start_stop_id)
            index_end_stop_id = (ast.literal_eval(p[3])).index(end_stop_id)

            start_time = (ast.literal_eval(p[2]))[index_str_stop_id]
            end_time = (ast.literal_eval(p[2]))[index_end_stop_id]

            time_out = (start_time, end_time)

            times.append(time_out)

        one_possible_route_wt_time.append((step, times))

    return one_possible_route_wt_time


def check_contains(sample_route_order, start_stop_id, end_stop_id):

    starting_stop_found = False

    for s in sample_route_order:
        if s == start_stop_id and end_stop_id in sample_route_order:
            starting_stop_found = True
        if starting_stop_found and s == end_stop_id:
            return True
    return False


# def clean_time():

"""
What the code currently will do is output all the found time sets (every time for start_stop_id and end_stop_id)
and append it into a list, which gets outputted for each stop. However, the bugs still needs to be fixed as some stops are
still not finding anything. Could be a bug within get_TTC_Trip as mentioned (with subway). 

The current test case that has been enabled simply does not have a time within the order given (a manual check within the 
data was done and no match ones with the correct order were spotted, only the opposite ordered were found).

There are no instances where stop_id 4049 comes before stop_id 574. Not sure if this is a bug or just simply how it is.

Considering that this is only one way of getting from Point A to Point B, there should very likely be working ones out
of the thousand solutions we find.

What the final output should be for get_stop_times is an output with each step and all the possible time sets put into a
list an outputted along with, all in a tuple format. See below for example...

This is a single step/stop... ((4049, 574, 'close_to_close', 61367, 3), [('4:51:08', '4:40:10'), ('4:21:08', 
'4:10:10'), ('27:31:08', '27:20:10'), ('27:01:08', '26:50:10'), ('28:01:08', '27:50:10'), ('26:31:08', '26:20:10'), 
('29:01:08', '28:50:09'), ('28:31:08', '28:20:09'), ('26:31:08', '26:20:10'), ('4:21:08', '4:10:10'), ('27:31:08', 
'27:20:10'), ('29:31:08', '29:20:09'), ('26:01:08', '25:50:10'), ('6:01:08', '5:50:10'), ('27:01:08', '26:50:10'), 
('28:01:08', '27:50:10'), ('5:21:08', '5:10:10'), ('4:51:08', '4:40:10'), ('6:01:08', '5:50:10'), ('5:01:08', 
'4:50:10'), ('28:01:08', '27:50:10'), ('27:31:08', '27:20:10'), ('6:31:08', '6:20:10'), ('7:01:08', '6:50:10'), 
('26:01:08', '25:50:10'), ('28:31:08', '28:20:09'), ('5:31:08', '5:20:10'), ('4:31:08', '4:20:10'), ('27:01:08', 
'26:50:10'), ('29:01:08', '28:50:09'), ('26:31:08', '26:20:10'), ('29:31:08', '29:20:09'), ('29:01:08', '28:50:09'), 
('28:31:08', '28:20:09'), ('6:01:08', '5:50:10'), ('26:01:08', '25:50:10'), ('7:01:08', '6:50:10'), ('5:01:08', 
'4:50:10'), ('28:01:08', '27:50:10'), ('27:31:08', '27:20:10'), ('4:31:08', '4:20:10'), ('27:01:08', '26:50:10'), 
('6:31:08', '6:20:10'), ('26:31:08', '26:20:10'), ('7:31:08', '7:20:10'), ('5:31:08', '5:20:10'), ('29:31:08', 
'29:20:09')]) 

"ignore the wrong order with the time, that has been fixed, the format is what we want"

The commented out clean_time function is there to then use this data (from get_stop_times), get rid of all the 
conflicting time sets. From step 1 and step 2, there are times that may be conflicting. For example, if step 1's 
ending time in the time set is 9:00 and the beginning time in step 2 might have a time set that starts at 8:45, 
this is not feasible as step 2 can't happen before step 1, therefore can't be before step 1 in terms of time either. 

The final output we need to get is a list of all the possible ways to complete a trip in terms of time (as we now 
already have all combinations of ways to get from A to B) by feeding the function a single trip instance (we can then 
use a for loop to loop through all the trips possible)
"""

# for i in get_stop_times(sample_output):
#     print("\n")
#     print(i)
#     print("\n")

print(get_route_id(61367))

# print(get_stop_times(sample_output))
