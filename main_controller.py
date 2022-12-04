from get_Stop_Times import *
from get_TCC_Trip import *


def time_to_string(time):
    """
    Changes time in tuple format back to string
    :param
    time: tuple
    :return:
    time: string
    """
    hours = str(time[0])
    minutes = str(time[1])
    seconds = str(time[2])

    if len(hours) == 1:
        hours = "0" + hours
    if len(minutes) == 1:
        minutes = "0" + minutes
    if len(seconds) == 1:
        seconds = "0" + seconds

    return hours + ":" + minutes


def time_to_int(time_str):
    """
    Feed in 'xx:yy:zz' to get xxyy

    :param time_str:
    :return: int - time in xxyy format
    """

    time_parts_str = time_str.split(":")
    hr_min = (time_parts_str[0] + time_parts_str[1])

    return int(hr_min)


def start_program():
    # Get user input
    user_input = get_input()

    # Declare and initiate variables with user input
    # Output format: ((start, (starting_time, starting_time)), (destination, (ending_time, ending_time)),
    #               int(age), hasPresto, budget, [additional_stops (not implemented)], pref_transit)

    pref_transit = user_input.pref_transit
    user_age = user_input.age
    hasPresto = user_input.hasPresto
    user_budget = user_input.budget

    start_dest_info = user_input.starting_stop
    end_dest_info = user_input.ending_stop

    desired_departure_time = time_to_int(time_to_string(user_input.starting_stop.arrive_time))
    desired_arrival_time = time_to_int(time_to_string(user_input.ending_stop.arrive_time))

    all_trips = get_trips(user_input)
    print(all_trips)
    trips_with_time = get_all_times(all_trips)
    for i in trips_with_time:
        print(i)
    
    return (trips_with_time, pref_transit, user_age, hasPresto, user_budget, desired_departure_time, desired_arrival_time)


# Test
# start_program()
