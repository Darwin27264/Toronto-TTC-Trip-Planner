from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# Some custom imports including time, SQLite， unzipper
from datetime import datetime
import sqlite3
import json
import os.path
import geocoder

# importing geopy library
from geopy.geocoders import Nominatim
from geopy import distance

# These two lines make sure a faster SAT solver is used.
from nnf import config
from nnf import Var

# Importing database
data = sqlite3.connect('routes.db')
d = data.cursor()

data_trip = sqlite3.connect('trips.db')
t = data_trip.cursor()

data_stop = sqlite3.connect('stops.db')
s = data_stop.cursor()

config.sat_backend = "kissat"

# Encoding that will store all of your constraints
global E


# Class for Budget propositions
@proposition(E)
class budget_prop:
    # instantiate with name to be given to the proposition
    def __init__(self, name):
        self = name


# class for Time propositions
@proposition(E)
class time_prop:
    # instantiate with name to be given to the proposition
    def __init__(self, name):
        self = name


# class for Additional Stops propositions
@proposition(E)
class add_stops_prop:
    # instantiate with name to be given to the proposition
    def __init__(self, name):
        self = name


# Declaring Propositions

# Budget
kid = budget_prop('kids/children')
adult = budget_prop('adult')
youth = budget_prop('youth')
senior = budget_prop('senior')
presto = budget_prop('presto user')
presto_adult = budget_prop('presto user (adult)')
presto_youth = budget_prop('presto user (youth)')
presto_senior = budget_prop('presto user (senior)')
presto_day_pass = budget_prop('buy presto day pass')
surpass_day_pass = budget_prop('cheaper to go with day pass')
within_budget = budget_prop('trip plan is within budget')
# Time
within_time_constraint = time_prop('within time constraint')
rush_hour = time_prop('rush hour')
# Additional Stops Requested
additional_stops = add_stops_prop('additional stops')


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
    E = Encoding()

    # Reference Code found here:
    # https://github.com/beckydvn/modelling-project-remaster/blob/main/modelling-project-original-and-remaster/modelling-project-1-REMASTER-2.0/run.py

    # User must be fall into one of the age groups
    E.add_constraint(adult | youth | senior | kid)
    # The user may only fall into one age group at a time
    constraint.add_exactly_one(E, adult, youth, senior, kid)

    # If the user is not a Presto holder
    if not presto_holder:
        E.add_constraint(~presto)
    else:
        E.add_constraint(~presto_senior | (~presto & ~senior))

    # this needs more work
    if not trip_withing_rush_hour:
        E.add_constraint(~rush_hour)

    E.add_constraint(additional_stops & (within_time_constraint | within_budget))


    # Add custom constraints by creating formulas with the variables you created.
    # E.add_constraint((a | b) & ~x)
    # # Implication
    # E.add_constraint(y >> z)
    # # Negate a formula
    # E.add_constraint(~(x & y))
    # # You can also add more customized "fancy" constraints. Use case: you don't want to enforce "exactly one"
    # # for every instance of BasicPropositions, but you want to enforce it for a, b, and c.:
    # constraint.add_exactly_one(E, a, b, c)

    return E


def get_input():
    """
    Get initial user input.

    User will input their starting location, desired ending location,
    current time, desired arrival time, travel budget, age, extra
    visiting locations.

    :return:
    origin_coords - tuple - starting location coordinates (lon, lat)

    destination - string - final destination
    time_now - string - current time (system time)
    arrival_time - string - time the user wishes to arrive at

    age - int - user age

    additional_stops_list - Python array - array of extra stop
    desired_stops_time - Python array - array of amount time spent at each additional stops

    Note: the lists will still be returned if empty
    """

    # Max and min coordinates defining Toronto Boundaries
    max_lat = 43.909707
    max_lon = -79.123111
    min_lat = 43.591811
    min_lon = -79.649908

    # Geopy preloading
    loc = Nominatim(user_agent="GetLoc")

    # Defining variables
    additional_stops_list = []
    desired_stops_time = []

    input_method = input("Welcome to the Toronto TTC Trip Planner, let's start by entering your starting stop \n"
                         "Your input methods are: \n"
                         "(1) Address/General Location (Example: Yonge St, Zoo, 382 Yonge St, etc...)\n"
                         "(2) Exact Stop Names from TTC Website\n"
                         "(3) (Latitude, Longitude)\n")

    if int(input_method) == 1:
        origin = input("Enter the location you wish to leave from: ")
        # entering the location name
        getLoc_no_toronto = loc.geocode(origin)
        getLoc_toronto = loc.geocode(origin + " Toronto")

        if getLoc_no_toronto is None or getLoc_toronto is None:
            print("Location is not found!")

            # While loop is needed here

        else:
            within_bound_no_toronto = min_lat < getLoc_no_toronto.latitude < max_lat and min_lon < \
                                      getLoc_no_toronto.longitude < max_lon
            within_bound_toronto = min_lat < getLoc_toronto.latitude < max_lat and min_lon < \
                                   getLoc_toronto.longitude < max_lon

            if getLoc_toronto.address == getLoc_no_toronto.address:
                if within_bound_no_toronto and within_bound_toronto:
                    # printing address
                    print("Ok, you will be leaving from: " + getLoc_no_toronto.address)

                    # printing latitude and longitude
                    print("Latitude = ", getLoc_no_toronto.latitude, "")
                    print("Longitude = ", getLoc_no_toronto.longitude)

                    origin_coords = (getLoc_no_toronto.latitude, getLoc_no_toronto.longitude)
                else:
                    print("Location is not in Toronto!")
                    print("Ok, you will be leaving from: " + getLoc_no_toronto.address)
            else:
                if within_bound_no_toronto and within_bound_toronto:
                    print("We have gotten two different locations based on your inputs, "
                          "\nplease select the one you are at: ")

                    print("(1) " + getLoc_no_toronto.address)
                    print("(2) " + getLoc_toronto.address)

                    correct_location = input("\nEnter 1 or 2 to select: ")

                    if int(correct_location) == 1:
                        print("Ok, you will be leaving from: " + getLoc_no_toronto.address)

                        # printing latitude and longitude
                        print("Latitude = ", getLoc_no_toronto.latitude, "\n")
                        print("Longitude = ", getLoc_no_toronto.longitude)

                        origin_coords = (getLoc_no_toronto.latitude, getLoc_no_toronto.longitude)
                    else:
                        print("Ok, you will be leaving from: " + getLoc_toronto.address)

                        # printing latitude and longitude
                        print("Latitude = ", getLoc_toronto.latitude, "\n")
                        print("Longitude = ", getLoc_toronto.longitude)

                        origin_coords = (getLoc_toronto.latitude, getLoc_toronto.longitude)
                elif within_bound_toronto:
                    print("Ok, you will be leaving from: " + getLoc_toronto.address)

                    # printing latitude and longitude
                    print("Latitude = ", getLoc_toronto.latitude, "\n")
                    print("Longitude = ", getLoc_toronto.longitude)

                    origin_coords = (getLoc_toronto.latitude, getLoc_toronto.longitude)
                else:
                    print("Ok, you will be leaving from: " + getLoc_no_toronto.address)

                    # printing latitude and longitude
                    print("Latitude = ", getLoc_no_toronto.latitude, "\n")
                    print("Longitude = ", getLoc_no_toronto.longitude)

                    origin_coords = (getLoc_no_toronto.latitude, getLoc_no_toronto.longitude)
    elif int(input_method) == 2:
        specific_stop = input("Enter the specific stop name (ones found in the TTC website): ")

        s.execute("SELECT * FROM stops WHERE stop_name=:stop_name", {'stop_name': specific_stop.upper()})
        stop = s.fetchall()

        origin_coords = (stop[0][2], stop[0][3])
    elif int(input_method) == 3:
        coords = input("Enter coordinate values in this format --- lat, lon: ")
        origin_coords = tuple(map(float, coords.split(', ')))
    else:
        print("No value input was received!")

    destination = input("\nNow enter your destination: ")

    # Getting current time
    now = datetime.now()
    time_now = now.strftime("%H:%M")
    print("\nCurrent Time:", time_now)

    # The time user wants to get to the final destination by

    # user's additional stops shouldn't exceed this time, need a constraint for this
    arrival_time = input("\nNow enter the time you wish to arrive at your final destination by (HH:MM): ")

    age = input("\nEnter your age (for trip price calculation): ")

    # Ask if there will be any additional stops first, will return an empty
    # additional_stops array if user chooses no
    more_stops = input("\nWould you like to take any additional stops \nin between your starting "
                       "location and final destination? (Y/N): ")

    if more_stops.capitalize() == "Y":
        print("\nEnter the additional stops below, once you are done, \nsimply hit *enter* again to record "
              "all the stops.")

        counter = 0

        # Emulating a do while loop
        while True:
            counter += 1

            add_stops = input("\nEnter additional stop #" + str(counter) + ":")

            if add_stops != "":
                additional_stops_list.append(add_stops)
            else:
                break

        print("\nNow enter the amount of time you wish to stay at for each "
              "\nof the additional stops you have inputted: ")

        for i in additional_stops_list:
            desired_stops_time = input("Amount of time you wish to stop for at " + i + ": ")

    return origin_coords, destination, time_now, arrival_time, int(age), additional_stops_list, desired_stops_time


def distance_finder(location, ttc_stops):
    return distance.distance(location, ttc_stops).km


def find_closest_stop(location):
    s.execute("SELECT * FROM stops")
    all_stops = s.fetchall()

    min_stop_id = all_stops[0][0]
    min_dis = distance_finder(location, (all_stops[0][2], all_stops[0][3]))

    for i in all_stops:
        cur_dis = distance_finder(location, (i[2], i[3]))
        if cur_dis < min_dis:
            min_dis = cur_dis
            min_stop_id = i[0]

    return min_stop_id


def main():
    test_array = get_input()
    print(test_array[0])
    # print(distance_finder((43.6950093, -79.3959279), (43.909707, -79.123111)))
    print(find_closest_stop(test_array[0]))


main()

''' Original Test Main
if __name__ == "__main__":

    print("test")

    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())

    print("\nVariable likelihoods:")
    for v, vn in zip([a, b, c, x, y, z], 'abcxyz'):
        # Ensure that you only send these functions NNF formulas
        # Literals are compiled to NNF here
        print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()
'''
