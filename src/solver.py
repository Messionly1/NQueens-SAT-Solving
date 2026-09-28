class SATSolverWrapper:
    def __init__(self, clauses: list):
        self.clauses = clauses
        
    def solve(self, solver_name: str = 'glucose3'):
        """
        TODO: Tích hợp pysat.solvers để tìm nghiệm
        """
        is_sat = False
        runtime = 0.0
        return is_sat, runtime