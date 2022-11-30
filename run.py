# import SQLite
import sqlite3

from bauhaus import Encoding, proposition, constraint
# These two lines make sure a faster SAT solver is used.
from nnf import config

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
global T

global user_input


# Class for Budget propositions
@proposition(E)
class budget_prop:
    # instantiate with name to be given to the proposition
    def __init__(self, name):
        self.name = name


# class for Time propositions
@proposition(E)
class time_prop:
    # instantiate with name to be given to the proposition
    def __init__(self, name):
        self.name = name


# Declaring Propositions

# Budget
kid = budget_prop('kid')
adult = budget_prop('adult')
youth = budget_prop('youth')
senior = budget_prop('senior')

presto = budget_prop('presto user')

normal_adult = budget_prop('normal user (adult)')
normal_other = budget_prop('normal user (others)')

presto_adult = budget_prop('presto user (adult)')
presto_other = budget_prop('presto users (not adults)')

presto_day_pass = budget_prop('buy presto day pass')
surpass_normal_price = budget_prop('cheaper to go with day pass')
within_budget = budget_prop('trip plan is within budget')
# Time
within_time_constraint = time_prop('within time constraint')
rush_hour = time_prop('rush hour')
valid_trip = time_prop('valid trip')
start_time = time_prop('start time')
end_time = time_prop('end time')


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory(hasPresto, age):
    E = Encoding()
    T = Encoding()

    # Reference Code found here:
    # https://github.com/beckydvn/modelling-project-remaster/blob/main/modelling-project-original-and-remaster/modelling-project-1-REMASTER-2.0/run.py

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
