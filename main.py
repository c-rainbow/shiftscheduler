from ortools.sat.python import cp_model
import tkinter

import build
import data


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._variables = variables
        self._solution_count = 0

    def on_solution_callback(self):
        self._solution_count += 1
        # for v in self._variables:
        #    print('%s=%i' % (v, self.Value(v)), end=' ')
        # print()

    def solution_count(self):
        return self._solution_count


#top = tkinter.Tk()
#top.mainloop()
#SearchForAllSolutionsSampleSat()

with open('data.json', 'r') as f:
    json_data = f.read()
    sch = data.Schedule.FromJSON(json_data)
    #print(sch)
    solver = build.BuildSolverFromSchedule(sch)

    status = solver.Solve()  
    print('status:', status)
    print('optimal:', solver.OPTIMAL)
    print('feasible:', solver.FEASIBLE)
    print('infeasible:', solver.INFEASIBLE)