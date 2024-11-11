from functools import reduce

def even(x):
    return x % 2 == 0

def square(x):
    return x**2

L = list(range(10))

L_even = list(filter(even, L))
L_even2 = [x for x in L if even(x)]

print(L)
print(L_even)
print(L_even2)

squares = list(map(square, L))
squares2 = [square(x) for x in L]

print(squares)
print(squares2)

def add(x, y):
    return x + y

rslt = reduce(add, L, 100) # third parameter = "accumulator"
total = 100
for x in L:
    total = total + x

print("Result of reduce: ", L, rslt, total)



dna = "atgctatcagttgttggtccaccaccagtgtgtgtcacattgtgtcaggtctcccatttgtttga"

from collections import defaultdict
counts = defaultdict(int)  # key=a,t,g,c    value=# times that nucleotide occurs.

def reducer(acc, val):
    acc[val] += 1
    return acc

totals = reduce(reducer, dna, counts)
print(dict(totals))







