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
