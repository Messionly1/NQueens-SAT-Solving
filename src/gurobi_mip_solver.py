import time
import gurobipy as gp
from gurobipy import GRB
from verify import is_valid_placement

class GurobiMIPSolver:
    def __init__(self, n: int):
        self.n = n
        self.solution = None
        self.timed_out = False
        
        self.model = gp.Model("NQueens_Gurobi")
        self.model.setParam("OutputFlag", 0)

        self.x = self.model.addVars(n, n, vtype=GRB.BINARY, name="q")

        for i in range(n):
            self.model.addConstr(gp.quicksum(self.x[i, j] for j in range(n)) == 1)

        for j in range(n):
            self.model.addConstr(gp.quicksum(self.x[i, j] for i in range(n)) == 1)

        for k in range(-n + 1, n):
            self.model.addConstr(gp.quicksum(self.x[i, i - k] for i in range(max(0, k), min(n, n + k))) <= 1)

        for k in range(2 * n - 1):
            self.model.addConstr(gp.quicksum(self.x[i, k - i] for i in range(max(0, k - n + 1), min(n, k + 1))) <= 1)

    def solve(self, time_limit_sec: float = 100.0, first_solution: bool = False):
        self.model.setParam("TimeLimit", time_limit_sec)
        self.model.setParam("Threads", 1)
     
        self.model.setParam("SolutionLimit", 1 if first_solution else 2000000000)

        start_time = time.perf_counter()
        self.model.optimize()
        end_time = time.perf_counter()

        runtime = end_time - start_time

        if self.model.Status in (GRB.OPTIMAL, GRB.SOLUTION_LIMIT):
            is_sat = True
            self.solution = []
            for i in range(self.n):
                for j in range(self.n):
                    if self.x[i, j].X > 0.5:
                        self.solution.append(j)
                        break
        elif self.model.Status == GRB.TIME_LIMIT:
            is_sat = False
            self.timed_out = True
            self.solution = None
        else:
            is_sat = False
            self.solution = None
            self.timed_out = False

        return is_sat, runtime

    def get_model(self):
        return self.solution

    def verify_solution(self) -> bool:
        return is_valid_placement(self.solution, self.n)

if __name__ == "__main__":
    solver = GurobiMIPSolver(8)
    is_sat, runtime = solver.solve()
    print(f"Gurobi SAT={is_sat}, Runtime={runtime:.6f}, Valid={solver.verify_solution()}")
