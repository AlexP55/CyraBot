from ortools.linear_solver import pywraplp

def find_minimal_cost(constraint_coeffs, lower_bounds, cost_coeffs):
  # Create the mip solver with the SCIP backend.
  num_vars = len(cost_coeffs)
  num_constraints = len(lower_bounds)
  solver = pywraplp.Solver.CreateSolver('SCIP')
  infinity = solver.infinity()
  x = {}
  for j in range(num_vars):
    x[j] = solver.IntVar(0, infinity, f'x[{j}]')

  for i in range(num_constraints):
    constraint = solver.RowConstraint(lower_bounds[i], infinity, '')
    for j in range(num_vars):
      constraint.SetCoefficient(x[j], constraint_coeffs[i][j])

  objective = solver.Objective()
  for j in range(num_vars):
    objective.SetCoefficient(x[j], cost_coeffs[j])
  objective.SetMinimization()

  status = solver.Solve()

  if status == pywraplp.Solver.OPTIMAL:
    return [(i, int(x[i].solution_value())) for i in range(num_vars) if x[i].solution_value() > 0]
  else:
    return []

