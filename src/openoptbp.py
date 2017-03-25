from openopt import *

N = 60

items = []

for i in range(N):
    small_vm = {
        'name': 'small%d' % i,
        'cpu': 2,
        'mem': 2048,
        'disk': 20,
        'n': 1
    }
    med_vm = {
        'name': 'medium%d' % i,
        'cpu': 4,
        'mem': 4096,
        'disk': 40,
        'n': 1
    }
    large_vm = {
        'name': 'large%d' % i,
        'cpu': 8,
        'mem': 8192,
        'disk': 80,
        'n': 1
    }
    items.append(small_vm)
    items.append(med_vm)
    items.append(large_vm)

bins = {
    'cpu': 48 * 4,  # 4.0 overcommit with cpu
    'mem': 240000,
    'disk': 2000,
}
p = BPP(items, bins, goal='min')
r = p.solve('glpk', iprint=0)  # requires cvxopt and glpk installed, see http://openopt.org/BPP for other solvers
print("XF:" + str(r.xf))
print("VALUES:" + str(r.values))  # per each bin
print "total vms is " + str(len(items))
print "servers used is " + str(len(r.xf))

for i, s in enumerate(r.xf):
    print "server " + str(i) + " has " + str(len(s)) + " vms"
