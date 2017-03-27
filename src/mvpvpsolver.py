from pyvpsolver import VPSolver, MVP, AFG, MPS
from pyvpsolver.solvers import mvpsolver

Ws = [(100, 75), (75, 50), (40,60)]
Cs = [3, 2,1]
Qs = [-1, -1,-1]
ws = [
    [(75, 50)],
    [(40, 15), (25, 25)],
    [(30,19), (24,34)],
    [(59,45)]
]
b = [1, 1, 1,1]
instance = MVP(Ws, Cs, Qs, ws, b)

output, solution = VPSolver.script("vpsolver_glpk.sh", instance)

obj, patterns = solution
print("Obj: {}".format(obj))
print("Solution: {}".format(patterns))
mvpsolver.print_solution(solution)
