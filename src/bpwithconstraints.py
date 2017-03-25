from openopt import *
from numpy import sin, cos

N = 15

items = [
    {
        'name': 'item %d' % i,  # name of item or item type
        'weight': 1.5 * (cos(i) + 1) ** 2,
        'volume': 2 * sin(i) + 3,
        'n': 1 if i < N / 3 else 2 if i < 2 * N / 3 else 3  # optional: number of items of the type, "1" by default
    }
    for i in range(N)
]

bins = {
    'volume': 35,
    'weight': 30,
    'n': 5
}

constraints = lambda values: 2*values['volume']+0.5*values['weight'] <70
p = BPP(items, bins, constraints = constraints)
r = p.solve('glpk', iprint = 0)

for i, s in enumerate(r.xf):
    print "bin " + str(i) + " has " + str(len(s)) + " items"
