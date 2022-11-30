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

from get_User_Input import get_input, route_within_rh

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

global user_input

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
presto_other=  budget_prop('presto users (not adults)')
presto_day_pass = budget_prop('buy presto day pass')
surpass_normal_price = budget_prop('cheaper to go with day pass')
within_budget = budget_prop('trip plan is within budget')
# Time
within_time_constraint = time_prop('within time constraint')
rush_hour = time_prop('rush hour')
valid_trip = time_prop('valid trip')
start_time = time_prop('start time')
end_time = time_prop('end time')
# Additional Stops Requested
additional_stops = add_stops_prop('additional stops')


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory(additional_stops_budget_surpass=None):

    E = Encoding()
    T = Encoding()

    # Reference Code found here:
    # https://github.com/beckydvn/modelling-project-remaster/blob/main/modelling-project-original-and-remaster/modelling-project-1-REMASTER-2.0/run.py

    # User must be fall into one of the age groups
    E.add_constraint(adult | youth | senior | kid)
    # The user may only fall into one age group at a time
    constraint.add_exactly_one(E, adult, youth, senior, kid)

    # If the user is not a Presto holder
    if not user_input.hasPresto:
        E.add_constraint(~presto)

    # Determining and adding the user to an age group
    if user_input.age <= 12:
        E.add_constraint(~(~kid))
        E.add_constraint(~(~within_budget))
    elif 13 <= user_input.age <= 19:
        E.add_constraint(~(~youth))
    elif 20 <= user_input.age < 65:
        E.add_constraint(~(~adult))
    else:
        E.add_constraint(~(~senior))

    E.add_constraint(~(presto & (youth | senior) | presto_other))
    E.add_constraint(~(presto & adult) | presto_adult)
    E.add_constraint(~presto | ~kid)

    constraint.add_exactly_one(E, presto_other, presto_adult)

    # the maximum expenditure calculated by the algorithm and compare with user's budget
    expenditure = ''
    budget = ''
    if expenditure > budget:
        E.add_constraint(~within_budget)
        E.add_constraint(~valid_trip)
    else:
        E.add_constraint(within_budget)

    # Traffic operation time
    T.add_constraint(start_time | ~valid_trip)
    T.add_constraint(end_time | ~valid_trip)

    # Compare the user defined time with the algorithm given time
    user_defined_time_s = user_input
    user_defined_time_e = ''
    given_st = ''
    given_et = ''
    if given_st < user_defined_time_s:
        T.add_constraint(~valid_trip)
    elif given_et > user_defined_time_e:
        T.add_constraint(~valid_trip)
    else:
        T.add_constraint(within_time_constraint)

    # Rush Hour constraints
    # this needs more work
    if not route_within_rh:
        T.add_constraint(~rush_hour)
        T.add_constraint(~valid_trip | within_time_constraint & within_budget & ~rush_hour)

    # # Additional stops constraints

    # if not additional_stops_budget_surpass:
    #     E.add_constraint(~(~surpass_normal_price))
    #
    #     E.add_constraint(~surpass_normal_price | presto_day_pass)
    #
    # # Main/final constraint, all must satisfy route to be valid
    # E.add_constraint(additional_stops & (within_time_constraint & within_budget))

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
    user_input = get_input()


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
