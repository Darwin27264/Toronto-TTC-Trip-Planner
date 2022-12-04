import ast
import sqlite3
import itertools
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


def time_to_string(time):
    hours = str(time[0])
    minutes = str(time[1])
    seconds = str(time[2])
    if len(hours) == 1:
        hours = "0" + hours
    if len(minutes) == 1:
        minutes = "0" + minutes
    if len(seconds) == 1:
        seconds = "0" + seconds
    return hours + ":" + minutes + ":" + seconds


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
    elif time_val1[0] == time_val2[0] and time_val1[1] == time_val2[1] and time_val1[2] > time_val2[2]:
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
    permutationlist = []
    returnlist = []
    for i in output:
        if i[1] == [] and i[0][-1] != -1:
            return False
        elif i[1] != []:
            iterlist.append(i[1])
    permuations = list(itertools.product(*iterlist))
    count = 0
    for j in permuations:
        count += 1
        os.system('cls')
        print("Number of permutations: " + str(len(permuations)))
        print("Current Permuation: " + str(count))
        one_trip = []
        counter = 0
        for i in range(len(output)):
            if output[i][0][-1] == -1:
                if len(one_trip) == 0:
                    one_trip.append((output[i][0], [('00:00:00', '00:05:00')]))
                else:
                    prev_time = list(get_time(output[i - 1][1][0][1]))
                    prev_time_string = time_to_string(tuple(prev_time))
                    if prev_time[1] + 5 >= 60:
                        prev_time[0] += 1
                        prev_time[1] = (prev_time[1] + 5) - 60
                    else:
                        prev_time[1] = 5 + prev_time[1]
                    time_string = time_to_string(tuple(prev_time))
                    one_trip.append((output[i][0], [(prev_time_string, time_string)]))
            elif output[i - 1][0][-1] == -1 and len(one_trip) == 1:
                time2 = j[counter][0]
                first_time = list(get_time(j[counter][0]))
                if first_time[1] - 5 < 0:
                    first_time[0] -= 1
                    first_time[1] = 60 - (5 - first_time[1])
                else:
                    first_time[1] = 5 + first_time[1]
                time1 = time_to_string(tuple(first_time))
                one_trip[0][1][0] = (time1, time2)
                one_trip.append((output[i][0], [(j[counter])]))
                counter += 1
            else:
                one_trip.append((output[i][0], [(j[counter])]))
                counter += 1
            permutationlist.append(one_trip)
    for i in permutationlist:
        if len(i) == 1:
            returnlist.append(i)
        else:
            for j in range(len(i) - 1):
                correct = True
                if check_time_after(i[j][1][0][1], i[j + 1][1][0][0]) == False:
                    correct = False
                    break
                if correct == True: returnlist.append(i)
    return returnlist


def get_all_times(all_trips):
    trips_with_time = []

    for i in all_trips:
        out_clean_time = clean_time(i)

        if type(out_clean_time) != bool:
            for j in out_clean_time:
                trips_with_time.append(j)

    return trips_with_time
