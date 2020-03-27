from ortools.sat.python import cp_model
import tkinter

import build
import data
import datetime

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

def GenerateAllDateStrs(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield str(start_date + datetime.timedelta(n))

def PrintShifts(nurse_name, var_dict):
    shift_dict = dict()
    for var_name, var in var_dict.items():
        if nurse_name in var_name and var.solution_value() == 1:
            splited = var_name.split('_')
            shift_dict[splited[2]] = splited[3]

    sorted_list = sorted(shift_dict.items())
    print(len(sorted_list))
    print(sorted_list)



#top = tkinter.Tk()
#top.mainloop()
#SearchForAllSolutionsSampleSat()

with open('data.json', 'r') as f:
    json_data = f.read()
    sch = data.Schedule.FromJSON(json_data)
    #print(sch)
    solver, var_dict = build.BuildSolverFromSchedule(sch)

    status = solver.Solve()  
    print('status:', status)
    print('optimal:', solver.OPTIMAL)
    print('feasible:', solver.FEASIBLE)
    print('infeasible:', solver.INFEASIBLE)

    print("nurse1")
    PrintShifts("nurse1", var_dict)

    print("nurse2")
    PrintShifts("nurse2", var_dict)

    print("nurse3")
    PrintShifts("nurse3", var_dict)

    print("nurse4")
    PrintShifts("nurse4", var_dict)

    