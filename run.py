from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import likelihood

# Encoding that will store all of your constraints
# User Price Group Logic Encoding: E
E = Encoding()
T = Encoding()

# Proposition Dictionary

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


# Budget (1st layer)
kid = budget_prop('kid')
adult = budget_prop('adult')
youth = budget_prop('youth')
senior = budget_prop('senior')

presto = budget_prop('presto user')

normal_adult = budget_prop('normal user (adult)')
normal_other = budget_prop('normal user (others)')

presto_adult = budget_prop('presto user (adult)')
presto_other = budget_prop('presto user (others)')


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
