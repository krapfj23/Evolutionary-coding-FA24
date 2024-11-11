"""
Sort numbers in a list using evolutionary computing
(Without implementing a sort algorithm.)
N.B. THIS IS NOT AN EFFICIENT WAY TO DO SORT. But its kinda cool to know
that you can sort without writing a sorting algorithm. (Simply describing what it means to be sorted!)

"""
from evo import Evo
import random as rnd

def sumstepdowns(L):
    """ Our only objective function: Sum of the step-downs in a list of numbers. """
    return sum([x - y for x, y in zip(L, L[1:]) if y < x])

def swapper(solutions):
    """ Our only agent: Swap two random values in the ONE solution provided """
    L = solutions[0]
    i = rnd.randrange(0, len(L))
    j = rnd.randrange(0, len(L))
    L[i], L[j] = L[j], L[i]
    return L


def main():

    # create the environment
    E = Evo()

    # Add the objective functions
    E.add_fitness_criteria("ssd", sumstepdowns)


    # Register our agents (there is only one) with Evo
    E.add_agent("swapper", swapper, k=1)


    # Create an initial solution
    N = 50
    L = [rnd.randrange(1, 99) for _ in range(N)]
    E.add_solution(L)

    print(E)
    E.evolve(n=5000000, dom=100, status=100000)
    print(E)

main()



