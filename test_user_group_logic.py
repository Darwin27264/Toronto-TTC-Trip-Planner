
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# # Encoding that will store all of your constraints
# E = Encoding()
#
#
# # Class for Budget propositions
# @proposition(E)
# class budget_prop:
#     # instantiate with name to be given to the proposition
#     def __init__(self, name):
#         self = name
#
#
# # Budget
# kid = budget_prop('kids/children')
# adult = budget_prop('adult')
# youth = budget_prop('youth')
# senior = budget_prop('senior')
# presto = budget_prop('presto user')
# presto_adult = budget_prop('presto user (adult)')
# presto_youth = budget_prop('presto user (youth)')
# presto_senior = budget_prop('presto user (senior)')
# presto_other = budget_prop('presto users (not adults)')
# presto_day_pass = budget_prop('buy presto day pass')
# surpass_normal_price = budget_prop('cheaper to go with day pass')
# within_budget = budget_prop('trip plan is within budget')
#
# kid,adult,youth,senior,presto,presto_youth,presto_adult,presto_senior,presto_other,presto_day_pass,surpass_normal_price,within_budget
# def example_theory():
#     hasPresto = False
#     age = 19
#
#     # Determining and adding the user to an age group
#     if age <= 12:
#         E.add_constraint(~(~kid))
#         E.add_constraint(~(~within_budget))
#     elif 13 <= age <= 19:
#         E.add_constraint(~(~youth))
#     elif 20 <= age < 65:
#         E.add_constraint(~(~adult))
#     else:
#         E.add_constraint(~(~senior))
#
#     # The user may only fall into one age group at a time
#     constraint.add_exactly_one(E, adult, youth, senior, kid)
#
#     # If the user is not a Presto holder
#     if not hasPresto:
#         E.add_constraint(~presto)
#
#     E.add_constraint(~(presto & (youth | senior) | presto_other))
#     E.add_constraint(~(presto & adult) | presto_adult)
#     E.add_constraint(~presto | ~kid)
#
#     constraint.add_exactly_one(E, presto_other, presto_adult)
#
#     return E
#
#
# if __name__ == "__main__":
#
#     T = example_theory()
#     # Don't compile until you're finished adding all your constraints!
#     T = T.compile()
#     # After compilation (and only after), you can check some of the properties
#     # of your model:
#     # print("\nSatisfiable: %s" % T.satisfiable())
#     # print("# Solutions: %d" % count_solutions(T))
#
#     print("   Solution: %s" % T.solve())
#     print("   Number of Solutions: %s" % T.model_count())
#
#
#     print("\nVariable likelihoods:")
#     for v,vn in zip([kid,adult,youth,senior,presto,presto_youth,presto_adult,presto_senior,presto_other,presto_day_pass,surpass_normal_price,within_budget],
#                     'kidadultyouthseniorprestopresto_youthpresto_adultpresto_seniorpresto_otherpresto_day_passsurpass_normal_pricewithin_budget'):
#         # Ensure that you only send these functions NNF formulas
#         # Literals are compiled to NNF here
#         print(" %s: %.2f" % (vn, likelihood(T, v)))
#     print()

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

# Call your variables whatever you want
a = BasicPropositions("a")
b = BasicPropositions("b")
c = BasicPropositions("c")
d = BasicPropositions("d")
e = BasicPropositions("e")
# At least one of these will be true
x = FancyPropositions("x")
y = FancyPropositions("y")
z = FancyPropositions("z")


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
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


if __name__ == "__main__":

    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())

    print("\nVariable likelihoods:")
    for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
        # Ensure that you only send these functions NNF formulas
        # Literals are compiled to NNF here
        print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()
