from get_Stop_Times import *
from get_TCC_Trip import *


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

    all_trips = get_trips(user_input)
    print(all_trips)
    trips_with_time = get_all_times(all_trips)
    for i in trips_with_time:
        print(i)
    
    return (trips_with_time, pref_transit, user_age, hasPresto, user_budget)


# Test
# start_program()
