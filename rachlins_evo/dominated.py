from functools import reduce
import matplotlib.pyplot as plt

pts = {(1,9), (1.25,7), (2,4), (4,2), (7,1), (6,1), (9, .75),
       (6,6), (4,5), (7,8), (9, 5), (3,7), (5,8), (7,3)}

print(pts)

def plot(pts):
    xs = [pt[0] for pt in pts]
    ys = [pt[1] for pt in pts]
    plt.scatter(xs,ys)
    plt.xlim(0,10)
    plt.ylim(0,10)
    plt.show()

# plot(pts)

def dominates(p1, p2):
    return (p1[0]<p2[0] and p1[1]<=p2[1]) or (p1[0]<=p2[0] and p1[1]<p2[1])



# ITERATIVE APPROACH TO FINDING NON-DOMINATED SET OF SOLUTIONS
def find_nds(pts):
    """ Finds the non-dominated subset of points """
    dom = set()
    for p in pts:
        bad = {q for q in pts if dominates(p, q)} # pts dominated by p
        dom = dom.union(bad)

    return pts - dom # remove the dominated points using set difference

nds = find_nds(pts)


# FUNCTIONAL APPROACH TO FINDING NON-DOMINATED SET OF SOLUTIONS
# WAY MORE ELEGANT

def reduce_nds(S, p):
    """ Reducing set S by finding points dominated by p """
    return S - {q for q in S if dominates(p, q)}

nds2 = reduce(reduce_nds, pts, pts)
plot(nds2)


plot(nds)