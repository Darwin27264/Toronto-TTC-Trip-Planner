from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import likelihood

from datetime import datetime
from time import strptime

import os
import platform

import random
import math

from main_controller import start_program

# Main Logic Encoding: T
T = Encoding()
# User Price Group Logic Encoding: E
E = Encoding()

# Proposition Dictionaries for Layer 2
# Time
valid_start_time = {}
valid_end_time = {}

rush_hour = {}
more_than_fifty_strtcar_bus = {}

# Preferred Transportation Method
prefer_subway = {}
prefer_bus = {}
prefer_streetcar = {}
prefer_walking = {}

mostly_subway = {}
mostly_bus = {}
mostly_streetcar = {}
mostly_walking = {}

no_pref = {}

# Solution
within_preference = {}
within_time_cons = {}
within_budget_cons = {}
solution = {}


# Class for Price Group propositions
@proposition(E)
class budget_prop:
    # instantiate with name to be given to the proposition
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"E.{self.data}"


# Class for Budget propositions
@proposition(T)
class time_prop:
    # instantiate with name to be given to the proposition
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"T.{self.data}"


# Class for Budget propositions
@proposition(T)
class solution_prop:
    # instantiate with name to be given to the proposition
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"T.{self.data}"


# Class for Budget propositions
@proposition(T)
class prefer_prop:
    # instantiate with name to be given to the proposition
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"T.{self.data}"


# Budget Propositions (1st layer)
kid = budget_prop('kid')
adult = budget_prop('adult')
youth = budget_prop('youth')
senior = budget_prop('senior')

presto = budget_prop('presto user')

normal_adult = budget_prop('normal user (adult)')
normal_other = budget_prop('normal user (others)')

presto_adult = budget_prop('presto user (adult)')
presto_other = budget_prop('presto user (others)')


def prop_setup(trips):
    indexer = 0
    for _ in trips:
        # Time
        valid_start_time[indexer] = time_prop('valid start time (transit)' + str(indexer))
        valid_end_time[indexer] = time_prop('valid end time (transit)' + str(indexer))

        rush_hour[indexer] = time_prop('rush hour (>60% of trip within rush hours detected)' + str(indexer))
        more_than_fifty_strtcar_bus[indexer] = time_prop('>50% busses or street cars within trip' + str(indexer))

        # Preferred Transportation Method
        prefer_subway[indexer] = prefer_prop('prefer going via subway' + str(indexer))
        prefer_bus[indexer] = prefer_prop('prefer going via bus' + str(indexer))
        prefer_streetcar[indexer] = prefer_prop('prefer going via street car' + str(indexer))
        prefer_walking[indexer] = prefer_prop('prefer going by walking' + str(indexer))

        mostly_subway[indexer] = prefer_prop('trip mostly on subway' + str(indexer))
        mostly_bus[indexer] = prefer_prop('trip mostly on bus' + str(indexer))
        mostly_streetcar[indexer] = prefer_prop('trip mostly on streetcar' + str(indexer))
        mostly_walking[indexer] = prefer_prop('trip mostly on walking' + str(indexer))

        no_pref[indexer] = prefer_prop('no preference on transit type' + str(indexer))

        # Solution
        within_preference[indexer] = solution_prop('matches user preferred tansit type' + str(indexer))
        within_time_cons[indexer] = solution_prop('within time constraint' + str(indexer))
        within_budget_cons[indexer] = solution_prop('within budget constraint' + str(indexer))
        solution[indexer] = solution_prop('valid solution' + str(indexer))
        indexer += 1

    # 17 props total

    # for making each trip into a proposition, use code below
    # solution = solution_prop('valid solution' + i)
    # indexer += 1


def time_to_int(time_str):
    """
    Feed in 'xx:yy:zz' to get xxyy

    :param time_str:
    :return: int - time in xxyy format
    """

    time_parts_str = time_str.split(":")
    hr_min = (time_parts_str[0] + time_parts_str[1])

    return int(hr_min)


def percent_of_each_transit_type(single_trip):
    """
    Feed in trip, get percentage of each transit type

    --- Transit Types Classifier ---
    0 - streetcar
    1 - subway
    3 - bus
    -1 - walking (200m)

    """
    percent_bus = 0
    percent_subway = 0
    percent_street_car = 0
    percent_walking = 0

    transit_types = []

    for every_step in single_trip:
        transit_types.append(every_step[0][-1])

    percent_bus = (transit_types.count(3) / len(transit_types)) * 100
    percent_subway = (transit_types.count(1) / len(transit_types)) * 100
    percent_street_car = (transit_types.count(0) / len(transit_types)) * 100
    percent_walking = (transit_types.count(-1) / len(transit_types)) * 100

    return (percent_street_car, percent_subway, percent_bus, percent_walking)


def rh_factor_calc(single_trip):
    """
    Calculates the amount, in percentage, of the routes with transit type
    street car or busses to see if it could be valid is rush hour is true.

    --- Transit Types Classifier ---
    0 - streetcar
    1 - subway
    3 - bus
    -1 - walking (200m)

    --- Rush Hour Periods ---
    7am - 10am OR 7:00 - 10:00
    4pm - 7pm OR 16:00 - 19:00

    :return:
    percent - int - percentage of street cars and busses within a trip
    """

    # Calculate the percentage of trip transit types that are slow during rush hour
    transit_types = []
    times = []

    # Morning rush hour period
    m_rush_hour_st = 700
    m_rush_hour_ed = 1000
    # Evening rush hour period
    e_rush_hour_st = 1600
    e_rush_hour_ed = 1900

    rush_hour_counter = 0

    # Only is taken into consideration if the total steps in
    # the trip has more than 3 steps
    if len(single_trip) <= 3:

        for every_step in single_trip:
            times.append(every_step[1])

        trip_start_time = time_to_int(times[0][0][0])
        trip_end_time = time_to_int(times[-1][0][1])

        return (trip_start_time, trip_end_time, 0, 0)
    else:
        for every_step in single_trip:
            transit_types.append(every_step[0][-1])
            times.append(every_step[1])

        sum_of_slow_transit_type = transit_types.count(0) + transit_types.count(3)
        total_slow_transit_type = (sum_of_slow_transit_type / len(transit_types)) * 100

        # Calculate the amount of trip that happens within rush hour
        for i in times:
            # i is in [(start_time, end_time)] format
            j = i[0]
            # j is in (start_time, end_time) format
            t_s = time_to_int(j[0])
            t_e = time_to_int(j[1])

            if m_rush_hour_st <= t_s <= m_rush_hour_ed or e_rush_hour_st <= t_s <= e_rush_hour_ed:
                rush_hour_counter += 1
            elif m_rush_hour_st <= t_e <= m_rush_hour_ed or e_rush_hour_st <= t_e <= e_rush_hour_ed:
                rush_hour_counter += 1

        total_rh_percentage = (rush_hour_counter / len(times)) * 100

        trip_start_time = time_to_int(times[0][0][0])
        trip_end_time = time_to_int(times[-1][0][1])

    return (trip_start_time, trip_end_time, int(total_slow_transit_type), int(total_rh_percentage))


def price_grp_theory(hasPresto, age):
    # Determining and adding the user to an age group
    if age <= 12:
        E.add_constraint(kid)
        E.add_constraint(~presto)

    elif 13 <= age <= 19:
        E.add_constraint(youth)
    elif 20 <= age < 65:
        E.add_constraint(adult)
    else:
        E.add_constraint(senior)

    # If the user is not a Presto holder
    if not hasPresto:
        # Not a Presto user means that they either falls into
        # the normal_adult or the normal_other price group
        E.add_constraint(~presto)
        E.add_constraint(~adult | normal_adult)
        E.add_constraint(adult | normal_other)
    else:
        E.add_constraint(presto)
        E.add_constraint(~adult | presto_adult)
        E.add_constraint(adult | presto_other)

    # The user may only fall into one age group at a time
    constraint.add_exactly_one(E, adult, youth, senior, kid)
    constraint.add_exactly_one(E, presto_adult, presto_other, normal_adult, normal_other)

    return E


def price_grp_define(logic_dict):
    """
    Finds the specific price group and price from
    the logic solution

    Args:
        logic_dict (dictionary): logic solution

    Returns:
        Price group and price per ride
    """
    price_group_all = [kid, presto_adult, presto_other, normal_adult, normal_other]
    pricing = [0.0, 3.20, 2.25, 3.25, 2.30]

    logic_results = {}

    for i in price_group_all:
        logic_results[i] = logic_dict[i]

    if logic_results[kid]:
        final = {kid}
    else:
        final = {i for i in logic_results if logic_results[i]}

    for i in final:
        price = pricing[price_group_all.index(i)]
        break

    return (final, price)


def iff(A1, A2):
    """
    Custom if and only if formatter
    """
    return (A1 | ~A2) & (~A1 | A2)


def main_theory(user_departure_time, user_arrival_time, all_trip_with_time, price_per_2h, user_budget,
                user_pref_transit):
    # Compare the user defined time with the algorithm given time
    # should already be in int time format
    # T = Encoding()
    # main_theory(700, 1450, final_sample_trip, 2.5, 13, 5)
    user_st_time = user_departure_time
    user_ed_time = user_arrival_time

    day_pass_price = 13.5

    indexes = 0

    for trip in all_trip_with_time:

        # Process trip data for every trip
        trip_data = rh_factor_calc(trip)
        transit_type_percentages = percent_of_each_transit_type(trip)

        # Trip start and end times
        given_st = trip_data[0]
        given_ed = trip_data[1]

        # Trip transit type and rush hour related data
        rush_hour_percent = trip_data[3]
        slow_during_rh_percent = trip_data[2]

        # Valid if the trips first bus departure time is after user's desired departure time
        if given_st > user_st_time:
            T.add_constraint(valid_start_time[indexes])
        else:
            T.add_constraint(~(valid_start_time[indexes]))

        # Valid if the trips last bus arrival time is before user's desired end time
        if given_ed < user_ed_time:
            T.add_constraint(valid_end_time[indexes])
        else:
            T.add_constraint(~(valid_end_time[indexes]))

        # If 60% of the trip is within rush hour periods
        if rush_hour_percent >= 60:
            T.add_constraint(rush_hour[indexes])
        else:
            T.add_constraint(~(rush_hour[indexes]))

        # If 50% of the transit types are slow during rush hours
        if slow_during_rh_percent >= 50:
            T.add_constraint(more_than_fifty_strtcar_bus[indexes])
        else:
            T.add_constraint(~(more_than_fifty_strtcar_bus[indexes]))

        # Rush hour implies there can't be more than 50% slow transit types within the trip
        T.add_constraint(iff((valid_start_time[indexes] & valid_end_time[indexes]) & ~(
                    rush_hour[indexes] & more_than_fifty_strtcar_bus[indexes]), within_time_cons[indexes]))

        # Budget Constraints (Layer 2)
        if user_st_time < 1000:
            user_st = "0" + str(user_st_time)[0] + ":" + str(user_st_time)[1] + str(user_st_time)[2]
        else:
            user_st = str(user_st_time)[0] + str(user_st_time)[1] + ":" + str(user_st_time)[2] + str(user_st_time)[3]

        if user_ed_time < 1000:
            user_ed = "0" + str(user_ed_time)[0] + ":" + str(user_ed_time)[1] + str(user_ed_time)[2]
        else:
            user_ed = str(user_ed_time)[0] + str(user_ed_time)[1] + ":" + str(user_ed_time)[2] + str(user_ed_time)[3]

        st_time = datetime.strptime(user_ed, '%H:%M')
        ed_time = datetime.strptime(user_st, '%H:%M')

        total_trip_time = abs((ed_time - st_time).total_seconds()) / 3600
        total_price = math.ceil(((float(total_trip_time)) / 2) * float(price_per_2h))

        correct_price = 0

        if total_price > day_pass_price:
            correct_price = day_pass_price
        else:
            correct_price = total_price

        if correct_price > user_budget:
            T.add_constraint(~(within_budget_cons[indexes]))
        else:
            T.add_constraint(within_budget_cons[indexes])

        # Preference Constraints

        """
        --- Transit Types Classifier ---
        0 - streetcar
        1 - subway
        3 - bus
        -1 - walking (200m)
        """

        if user_pref_transit == 0:
            T.add_constraint(prefer_streetcar[indexes])
            T.add_constraint(
                ~prefer_subway[indexes] & ~prefer_walking[indexes] & ~prefer_bus[indexes] & ~no_pref[indexes])
        elif user_pref_transit == 1:
            T.add_constraint(prefer_subway[indexes])
            T.add_constraint(
                ~prefer_streetcar[indexes] & ~prefer_walking[indexes] & ~prefer_bus[indexes] & ~no_pref[indexes])
        elif user_pref_transit == -1:
            T.add_constraint(prefer_walking[indexes])
            T.add_constraint(
                ~prefer_streetcar[indexes] & ~prefer_subway[indexes] & ~prefer_bus[indexes] & ~no_pref[indexes])
        elif user_pref_transit == 3:
            T.add_constraint(prefer_bus[indexes])
            T.add_constraint(
                ~prefer_streetcar[indexes] & ~prefer_subway[indexes] & ~prefer_walking[indexes] & ~no_pref[indexes])
        elif user_pref_transit == 5:
            T.add_constraint(no_pref[indexes])
            T.add_constraint(
                ~prefer_streetcar[indexes] & ~prefer_subway[indexes] & ~prefer_walking[indexes] & ~prefer_bus[indexes])

        # transit_type_percentages format: (percent_street_car, percent_subway, percent_bus, percent_walking)
        most_percent = max(transit_type_percentages)
        inde = transit_type_percentages.index(most_percent)

        if inde == 0:
            T.add_constraint(mostly_streetcar[indexes])
            T.add_constraint(iff(prefer_streetcar[indexes] & mostly_streetcar[indexes], within_preference[indexes]))
        elif inde == 1:
            T.add_constraint(mostly_subway[indexes])
            T.add_constraint(iff(prefer_subway[indexes] & mostly_subway[indexes], within_preference[indexes]))
        elif inde == 2:
            T.add_constraint(mostly_bus[indexes])
            T.add_constraint(iff(prefer_bus[indexes] & mostly_bus[indexes], within_preference[indexes]))

        elif inde == 3:
            T.add_constraint(mostly_walking[indexes])

            T.add_constraint(iff(prefer_walking[indexes] & mostly_walking[indexes], within_preference[indexes]))

        # Solution is only valid if both time constraint and budget constraints are met
        T.add_constraint(iff((within_time_cons[indexes] & within_budget_cons[indexes] & (
                    within_preference[indexes] | no_pref[indexes])), solution[indexes]))

        indexes += 1

    return T


# >50% slow transit type & >60% rush hour, expect no solution
sample_trip_1 = [((4049, 574, 'test', 61367, 3), [('7:51:08', '9:40:10')]),
                 ((4049, 574, 'test', 61367, 3), [('9:51:08', '10:40:10')]),
                 ((4049, 574, 'test', 61367, 1), [('10:51:08', '11:40:10')]),
                 ((4049, 574, 'test', 61367, 3), [('8:51:08', '9:40:10')]),
                 ((4049, 574, 'test', 61367, -1), [('12:51:08', '13:40:10')]),
                 ((4049, 574, 'test', 61367, -1), [('13:51:08', '14:40:10')]),
                 ((4049, 574, 'test', 61367, 3), [('17:51:08', '18:40:10')]),
                 ((4049, 574, 'test', 61367, 3), [('16:51:08', '14:40:10')])]
# >50% slow transit type & <60% rush hour, expect solution
sample_trip_2 = [((4049, 574, 'close_to_close', 61367, 3), [('7:51:08', '9:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, 3), [('9:51:08', '10:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, 1), [('10:51:08', '11:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('11:51:08', '12:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('12:51:08', '13:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('13:51:08', '14:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('13:51:08', '14:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('13:51:08', '14:40:10')])]
# <50% slow transit type & >60% rush hour, expect solution
sample_trip_3 = [((4049, 574, 'close_to_close', 61367, 3), [('7:51:08', '9:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, 3), [('9:51:08', '10:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('10:51:08', '11:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('11:51:08', '12:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('16:51:08', '17:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('17:51:08', '18:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('18:51:08', '17:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('16:51:08', '14:40:10')])]
# <50% slow transit type & <60% rush hour, expect solution
sample_trip_4 = [((4049, 574, 'close_to_close', 61367, 3), [('7:51:08', '9:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, 3), [('9:51:08', '10:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, 1), [('10:51:08', '11:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('11:51:08', '12:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('12:51:08', '13:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('13:51:08', '14:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('13:51:08', '14:40:10')]),
                 ((4049, 574, 'close_to_close', 61367, -1), [('13:51:08', '14:40:10')])]


def main():
    test_mode = input("Run test? (Y/N): ")

    if test_mode == "N" or test_mode == "n":
        # Gathering and preparing data needed of logic
        all_data = start_program()

        all_trip_wt_time = all_data[0]
        pref_transit = all_data[1]
        user_age = all_data[2]
        hasPresto = all_data[3]
        user_budget = all_data[4]
        desired_departure_time = all_data[5]
        desired_arrival_time = all_data[6]

        # Layer 1 Price Group Logic
        print("\n--- Price Group Logic ---")
        print("\nConditions:")
        print("Has Presto: " + str(hasPresto) + ", Age: " + str(user_age))

        logic_price_grp = price_grp_theory(hasPresto, user_age)
        # Don't compile until you're finished adding all your constraints!
        logic_price_grp = logic_price_grp.compile()
        # After compilation (and only after), you can check some properties
        # of your model:
        print("\nSatisfiable: %s" % logic_price_grp.satisfiable())
        # print("# Solutions: %d" % count_solutions(logic_price_grp))
        print("Number of Solutions: %s" % logic_price_grp.model_count())

        budget_solution = logic_price_grp.solve()

        print("Solution: %s" % budget_solution)
        # find the specific price group
        print("\nPrice Group + Price")
        gp_price = price_grp_define(budget_solution)
        print(gp_price)
        price_grp_price = gp_price[-1]

        print("\n------------------------------------------\n")

        # Beginning of Main Logic
        print("--- Main Logic ---\n")

        print("Setting up propositions for all possible trip instance...")
        prop_setup(all_trip_wt_time)

        # Need to feed in (desired starting time, desired arrival time, singular trip option, price group pricing,
        # user budget, preferred transit type)
        main_theory(desired_departure_time, desired_arrival_time, all_trip_wt_time, price_grp_price, user_budget,
                    pref_transit)

        logic_main = T.compile()

        print("\nSatisfiable: %s" % logic_main.satisfiable())
        print("Number of Solutions: %s" % logic_main.model_count())

        final_solution = logic_main.solve()

        print("Solution: %s" % final_solution)

        # Final Output
        solution_keys = []
        for i in solution:
            solution_keys.append(solution[i])

        final_solution_keys = []
        true_solutions = 0
        for key in solution_keys:
            if final_solution.get(key):
                true_solutions += 1
                final_solution_keys.append(key)

        all_solution_index = []
        for j in final_solution_keys:
            final_key_index = int(str(j)[-1])
            all_solution_index.append(final_key_index)

        print("\n------------------------------------------")
        input("\nPress any key to contiue...")
        # Find OS and set clear termial command
        if platform.system() == 'Windows':
            clearTermial = 'cls'
        elif platform.system() == 'Darwin':
            clearTermial = 'clear'
        elif platform.system() == 'Linux':
            clearTermial = 'clear'
        else:
            clearTermial = 'clear'

        os.system(clearTermial)

        print("--- Results ---\n")
        print("Total number of trips possible meeting the user inputs: " + str(true_solutions))

        if true_solutions != 0:

            while True:

                entered = input(
                    "\nEnter anything to see a random solution trip, or enter (exit) to exit the program. \n")

                if entered == "exit" or entered == "EXIT":
                    break
                else:
                    rando = random.randint(0, (true_solutions - 1))

                    print("Currently showing trip index: " + str(rando) + "\n")
                    print(all_trip_wt_time[rando])

        else:
            print("No possible trips were found meeting user's needs.")

    else:
        # Test run theories

        print("Running Tests...\n\n")

        print("Test 1: \n")
        print("--- Parameters ---\n")

        test_departure_time = 700
        test_arrival_time = 1450
        test_grp_price = 2.3
        test_budget = 15
        test_pref_transit = 5

        test_1 = [sample_trip_2, sample_trip_3, sample_trip_1]

        print("Setting up propositions for test trip instances...")
        prop_setup(test_1)

        main_theory(test_departure_time, test_arrival_time, test_1, test_grp_price, test_budget, test_pref_transit)

        logic_main = T.compile()

        print("\nSatisfiable: %s" % logic_main.satisfiable())
        print("Number of Solutions: %s" % logic_main.model_count())

        final_solution = logic_main.solve()

        print("Solution: %s" % final_solution)

        # Final Output
        solution_keys = []
        for i in solution:
            solution_keys.append(solution[i])

        final_solution_keys = []
        true_solutions = 0

        for key in solution_keys:
            if final_solution.get(key):
                true_solutions += 1
                final_solution_keys.append(key)

        all_solution_index = []
        for j in final_solution_keys:
            final_key_index = int(str(j)[-1])
            all_solution_index.append(final_key_index)

        print("\n------------------------------------------")
        input("\nPress any key to contiue...")
        # Find OS and set clear termial command
        if platform.system() == 'Windows':
            clearTermial = 'cls'
        elif platform.system() == 'Darwin':
            clearTermial = 'clear'
        elif platform.system() == 'Linux':
            clearTermial = 'clear'
        else:
            clearTermial = 'clear'

        os.system(clearTermial)

        print("--- Results ---\n")
        print("Total number of trips possible meeting test case: " + str(true_solutions))

        if true_solutions != 0:

            while True:

                entered = input(
                    "\nEnter anything to see a random solution trip, or enter (exit) to exit the program. \n")

                if entered == "exit" or entered == "EXIT":
                    break
                else:
                    rando = random.randint(0, (true_solutions - 1))

                    print("Currently showing trip index: " + str(rando) + "\n")
                    print(test_1[rando])

        else:
            print("No possible trips were found for the test case.")


main()
