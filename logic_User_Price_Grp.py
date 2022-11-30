from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# Encoding that will store all of your constraints
E = Encoding()


# Class for Budget propositions
@proposition(E)
class budget_prop:
    # instantiate with name to be given to the proposition
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"E.{self.data}"


# Budget
kid = budget_prop('kid')
adult = budget_prop('adult')
youth = budget_prop('youth')
senior = budget_prop('senior')

presto = budget_prop('presto user')

normal_adult = budget_prop('normal user (adult)')
normal_other = budget_prop('normal user (others)')

presto_adult = budget_prop('presto user (adult)')
presto_other = budget_prop('presto user (others)')

presto_day_pass = budget_prop('buy presto day pass')
surpass_normal_price = budget_prop('cheaper to go with day pass')
within_budget = budget_prop('trip plan is within budget')


def example_theory(hasPresto, age):
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


def main(test_Presto, test_age):
    print("\nConditions:")
    print(str(test_Presto) + ", " + str(test_age))

    T = example_theory(test_Presto, test_age)
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    # print("# Solutions: %d" % count_solutions(T))
    print("   Number of Solutions: %s" % T.model_count())

    budget_solution = T.solve()

    print("   Solution: %s" % budget_solution)
    # find the specific price group
    print(price_grp_define(budget_solution))

    print("\nVariable likelihoods:")
    for v, vn in zip(
            [kid, adult, youth, senior, presto, normal_adult, normal_other, presto_adult, presto_other, presto_day_pass,
             surpass_normal_price, within_budget],
            'kayspodpodsw'):
        # Ensure that you only send these functions NNF formulas
        # Literals are compiled to NNF here
        print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()

# main(True, 24)
# main(False, 24)
# main(True, 17)
# main(False, 17)
# main(True, 80)
# main(False, 80)
# main(False, 10)
