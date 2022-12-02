import ast
import sqlite3
import itertools

# Importing database
data_trip = sqlite3.connect('trips.db')
t = data_trip.cursor()
data_route = sqlite3.connect('routes.db')
r = data_route.cursor()
data_stop = sqlite3.connect('stops.db')
s = data_stop.cursor()
data_subway = sqlite3.connect('subway.db')
m = data_subway.cursor()


def get_stop_times(one_possible_route):
    """
    get_stop_times takes in a possible route and finds all the trips
    associated with the route_id of each step and adds a list of tuples of
    all the times whose index matches with the starting and ending stop
    """
    one_possible_route_wt_time = []

    # For the every step in one possible route, from point a to point b
    for step in one_possible_route:

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
        # print("running...looking for route_id: " + str(cur_route_id) + "\n")

        for p in all_matching_routes_cor_order:
            index_str_stop_id = (ast.literal_eval(p[3])).index(start_stop_id)
            index_end_stop_id = (ast.literal_eval(p[3])).index(end_stop_id)

            start_time = (ast.literal_eval(p[2]))[index_str_stop_id]
            end_time = (ast.literal_eval(p[2]))[index_end_stop_id]

            time_out = (start_time, end_time)

            times.append(time_out)

        one_possible_route_wt_time.append((step, times))

    return one_possible_route_wt_time


def check_contains(sample_route_order, start_stop_id, end_stop_id):
    """
    check_contains checks the list of stops that a trip visits and
    checks if the starting stop and ending stop both appear in the list
    and in that order respectively. Returns True if these conditions are met
    and returns False otherwise
    """

    starting_stop_found = False

    for s in sample_route_order:
        if s == start_stop_id and end_stop_id in sample_route_order:
            starting_stop_found = True
        if starting_stop_found and s == end_stop_id:
            return True
    return False


def get_time(time):
    """
    get_time takes the time in string format and returns the values
    in the tuple format of (hours,minutes,seconds)
    """
    timesplit = time.split(":")
    hours = int(timesplit[0])
    minutes = int(timesplit[1])
    seconds = int(timesplit[2])
    return (hours, minutes, seconds)


def check_time_after(time1, time2):
    time_val1 = get_time(time1)
    time_val2 = get_time(time2)
    if time_val1[0] > time_val2[0]:
        return False
    elif time_val1[0] == time_val2[0] and time_val1[1] > time_val2[1]:
        return False
    elif time_val1[0] == time_val2[0] and time_val1[1] == time_val2[1] and time_val1[2] >= time_val2[2]:
        return False
    else:
        return True


def clean_time(trip):
    """
    clean_time takes the output from get_stop_times and returns a list
    of all permutations that have the correct chronological sequence 
    """
    output = get_stop_times(trip)
    iterlist = []
    correctlist = []
    returnlist = []
    for i in output:
        if i[1] == []:
            return False
        else:
            iterlist.append(i[1])
    permuations = list(itertools.product(*iterlist))
    for i in permuations:
        num_steps = len(i)
        is_correct = True
        for j in range(num_steps - 1):
            if check_time_after(i[j][1], i[j + 1][0]) == False:
                is_correct = False
                break
        if is_correct: correctlist.append(i)
    for i in correctlist:
        permuation = []
        for j in range(len(output)):
            permuation.append((output[j][0], i[j]))
        returnlist.append(permuation)
    return returnlist


def get_all_times(all_trips):
    trips_with_time = []

    for i in all_trips:
        for j in clean_time(i):
            trips_with_time.append(j)

    return trips_with_time
