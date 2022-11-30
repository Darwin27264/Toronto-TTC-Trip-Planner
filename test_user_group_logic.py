
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# Encoding that will store all of your constraints
E = Encoding()


# Class for Budget propositions
@proposition(E)
class budget_prop:
    # instantiate with name to be given to the proposition
    def __init__(self, name):
        self = name


# Budget
kid = budget_prop('kids/children')
adult = budget_prop('adult')
youth = budget_prop('youth')
senior = budget_prop('senior')
presto = budget_prop('presto user')
presto_adult = budget_prop('presto user (adult)')
presto_youth = budget_prop('presto user (youth)')
presto_senior = budget_prop('presto user (senior)')
presto_other = budget_prop('presto users (not adults)')
presto_day_pass = budget_prop('buy presto day pass')
surpass_normal_price = budget_prop('cheaper to go with day pass')
within_budget = budget_prop('trip plan is within budget')


def example_theory():
    hasPresto = True
    age = 19

    # User must be fall into one of the age groups
    E.add_constraint(adult | youth | senior | kid)
    # The user may only fall into one age group at a time
    constraint.add_exactly_one(E, adult, youth, senior, kid)

    # If the user is not a Presto holder
    if not hasPresto:
        E.add_constraint(~presto)

    # Determining and adding the user to an age group
    if age <= 12:
        E.add_constraint(~(~kid))
        E.add_constraint(~(~within_budget))
    elif 13 <= age <= 19:
        E.add_constraint(~(~youth))
    elif 20 <= age < 65:
        E.add_constraint(~(~adult))
    else:
        E.add_constraint(~(~senior))

    E.add_constraint(~(presto & (youth | senior) | presto_other))
    E.add_constraint(~(presto & adult) | presto_adult)
    E.add_constraint(~presto | ~kid)

    constraint.add_exactly_one(E, presto_other, presto_adult)

    return E


if __name__ == "__main__":

    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())
    #
    # print("\nVariable likelihoods:")
    # for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
    #     # Ensure that you only send these functions NNF formulas
    #     # Literals are compiled to NNF here
    #     print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()
