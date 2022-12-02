from get_Stop_Times import *
from get_TCC_Trip import *


def start_program():
    # Get user input
    user_input = get_input()

    # Declare and initiate variables with user input
    # Output format: ((start, (starting_time, starting_time)), (destination, (ending_time, ending_time)),
    #               int(age), hasPresto, budget, [additional_stops (not implemented)], pref_transit)

    pref_transit = user_input[-1]
    user_age = user_input[2]
    hasPresto = user_input[3]
    user_budget = user_input[4]

    start_dest_info = user_input[0]
    end_dest_info = user_input[1]

    all_trips = get_trips(user_input)

    trips_with_time = get_all_times(all_trips)

    return (trips_with_time, pref_transit, user_age, hasPresto, user_budget)