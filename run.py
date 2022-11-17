from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# Some custom imports including time, SQLite， unzipper
from datetime import datetime
import sqlite3
import json
import os.path

# Get user location using geopy
# importing geopy library
from geopy.geocoders import Nominatim

# Importing database
# from trips import Trips
# from routes import Routes
# from stops import Stops

# These two lines make sure a faster SAT solver is used.
from nnf import config
from nnf import Var

config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()


# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
@proposition(E)
class BasicPropositions:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"A.{self.data}"


# Different classes for propositions are useful because this allows for more dynamic constraint creation
# for propositions within that class. For example, you can enforce that "at least one" of the propositions
# that are instances of this class must be true by using a @constraint decorator.
# other options include: at most one, exactly one, at most k, and implies all.
# For a complete module reference, see https://bauhaus.readthedocs.io/en/latest/bauhaus.html
@constraint.at_least_one(E)
@proposition(E)
class FancyPropositions:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"A.{self.data}"


# # Budget/Price
# kid = Var('kids/children')
# adult = Var('adult')
# youth = Var('youth')
# senior = Var('senior')
# presto = Var('presto user')
# presto_adult = Var('presto user (adult)')
# presto_youth = Var('presto user (youth)')
# presto_senior = Var('presto user (senior)')
# presto_day_pass = Var('buy presto day pass')
# surpass_day_pass = Var('cheaper to go with day pass')
# # Time
# within_time_constraint = Var('within time constraint')
# rush_hour = Var('rush hour')
# # Additional Stops Requested
# additional_stops = Var('additional stops')

kid = BasicPropositions('kids/children')
adult = BasicPropositions('adult')
youth = BasicPropositions('youth')
senior = BasicPropositions('senior')
presto = BasicPropositions('presto user')
presto_adult = BasicPropositions('presto user (adult)')
presto_youth = BasicPropositions('presto user (youth)')
presto_senior = BasicPropositions('presto user (senior)')
presto_day_pass = BasicPropositions('buy presto day pass')
surpass_day_pass = BasicPropositions('cheaper to go with day pass')

# Time
within_time_constraint = BasicPropositions('within time constraint')
rush_hour = BasicPropositions('rush hour')
# Additional Stops Requested
additional_stops = BasicPropositions('additional stops')


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
    # User must be fall into one of the age groups
    E.add_constraint(adult | youth | senior | kid)

    # Add custom constraints by creating formulas with the variables you created. 
    E.add_constraint((a | b) & ~x)
    # Implication
    E.add_constraint(y >> z)
    # Negate a formula
    E.add_constraint(~(x & y))
    # You can also add more customized "fancy" constraints. Use case: you don't want to enforce "exactly one"
    # for every instance of BasicPropositions, but you want to enforce it for a, b, and c.:
    constraint.add_exactly_one(E, a, b, c)

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

    # Geopy preloading
    loc = Nominatim(user_agent="GetLoc")

    # Defining variables
    additional_stops_list = []
    desired_stops_time = []

    origin = input("Welcome to the Toronto CTC Trip Planner, let's start by entering your starting stop \n"
                   "(the street you are currently on or looking to leave from, for example: Yonge Street): ")

    # entering the location name
    getLoc = loc.geocode(origin)

    # printing address
    print("Ok, you will be leaving from: " + getLoc.address)

    # printing latitude and longitude
    print("Latitude = ", getLoc.latitude, "\n")
    print("Longitude = ", getLoc.longitude)

    origin_coords = (getLoc.longitude, getLoc.latitude)

    destination = input("\nNow enter your destination: ")

    # Getting current time (device time)
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


def main():
    print("test")


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
