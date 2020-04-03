

import datetime
import date_util

import data 
import functools

from ortools.linear_solver import pywraplp


# Variable name from nurse name, work date, and shift type name
def GetVariableName(name, date_str, shift_type_str):
    return 'x_%s_%s_%s' % (name, date_str, shift_type_str)


# Sum of solver "variables". Works for both MIP and CP solvers
def VariableSum(variables):
    return functools.reduce(lambda x, y: x + y, variables)


# 1. only work one shift in one day
def BuildConstraint1(solver, constraint, all_date_strs, var_dict):
    for date_str in all_date_strs:
        vars = []
        for shift_type, _ in data.ShiftType.__members__.items():
            var_name = GetVariableName(constraint.name, date_str, shift_type)
            vars.append(var_dict[var_name])

        solver.Add(VariableSum(vars) <= 1)


# 2. After night shift, no work next day/evening
def BuildConstraint2(solver, constraint, all_date_strs, var_dict):
    for i in range(len(all_date_strs)-1):
        work_date_str = all_date_strs[i]
        next_date_str = all_date_strs[i+1]

        night_var = var_dict[GetVariableName(
            constraint.name, work_date_str, data.ShiftType.NIGHT.name)]
        day_var = var_dict[GetVariableName(
            constraint.name, next_date_str, data.ShiftType.DAY.name)]
        evening_var = var_dict[GetVariableName(
            constraint.name, next_date_str, data.ShiftType.EVENING.name)]

        solver.Add(night_var + day_var + evening_var <= 1)


# 3. no more than n consecutive workdays
def BuildCosntraint3(solver, constraint, all_date_strs, var_dict):
    max_days = constraint.max_consecutive_workdays
    for from_index in range(len(all_date_strs) - max_days):
        vars = []
        for i in range(max_days):
            for shift_type_str in data.ShiftType.WorkShiftNames():
                var_name = GetVariableName(
                        constraint.name, all_date_strs[from_index + i], shift_type_str)
                vars.append(var_dict[var_name])
        
        solver.Add(VariableSum(vars) <=  max_days)


# 4. no more than m consecutive nights
def BuildConstraint4(solver, constraint, all_date_strs, var_dict):   
    max_nights = constraint.max_consecutive_nights
    for from_index in range(len(all_date_strs) - max_nights):
        vars = []
        for i in range(max_nights):
            var_name = GetVariableName(
                    constraint.name, all_date_strs[from_index + i], data.ShiftType.NIGHT.name)
            vars.append(var_dict[var_name])
        
        solver.Add(VariableSum(vars) <=  max_nights)


# 5. Minimum a, maximum b total workdays
def BuildConstraint5(solver, constraint, all_date_strs, var_dict):
    vars = []
    for date_str in all_date_strs:
        for shift_type_str in data.ShiftType.WorkShiftWorkShiftNames():
            var_name = GetVariableName(constraint.name, date_str, shift_type_str)
            vars.append(var_dict[var_name])

    var_sum = VariableSum(vars)
    solver.Add(constraint.min_total_workdays <= var_sum)
    solver.Add(var_sum <= constraint.max_total_workdays)


# 6. No work on off-shifts
def BuildConstraint6(solver, constraint, all_date_strs, var_dict):
    for off_shift in constraint.off_shifts:
        var_name = GetVariableName(
            constraint.name, str(off_shift.date), off_shift.shift_type.name)
        solver.Add(var_dict[var_name] == 0)


# 7. Work in pre-defined shifts
def BuildConstraint7(solver, constraint, all_date_strs, var_dict):
    for fixed_shift in constraint.fixed_shifts:
        var_name = GetVariableName(constraint.name, str(fixed_shift.date), fixed_shift.shift_type.name)
        solver.Add(var_dict[var_name] == 1)


# 8. Exactly 1 person should work in each shift
def BuildConstraint8(solver, constraints, date_str, var_dict):
    for shift_type_str in data.ShiftType.WorkShiftNames():
        vars = []
        for constraint in constraints:
            var_name = GetVariableName(constraint.name, date_str, shift_type_str)
            vars.append(var_dict[var_name])
        
        solver.Add(VariableSum(vars) == 1)


def BuildSolverFromSchedule(schedule):

    solver = pywraplp.Solver(
            'scheduling_program', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    var_dict = dict()         
    all_date_strs = list(date_util.GenerateAllDateStrs(schedule.start_date, schedule.end_date))   

    # Create variables
    for date_str in all_date_strs:
        for constraint in schedule.constraints:
            for shift_type_str in data.ShiftType.WorkShiftNames():
                var_name = GetVariableName(constraint.name, date_str, shift_type_str)
                var_dict[var_name] = solver.BoolVar(var_name)
            
    # Create constraints 1-7
    for constraint in schedule.constraints:
        # 1. only work one shift in one day
        BuildConstraint1(solver, constraint, all_date_strs, var_dict)

        # 2. After night shift, no work next day/evening
        BuildConstraint2(solver, constraint, all_date_strs, var_dict)

        # 3. no more than n consecutive workdays
        BuildCosntraint3(solver, constraint, all_date_strs, var_dict)

        # 4. no more than m consecutive nights
        BuildConstraint4(solver, constraint, all_date_strs, var_dict)

        # 5. Minimum a, maximum b total workdays
        BuildConstraint5(solver, constraint, all_date_strs, var_dict)

        # 6. No work on off-shifts
        BuildConstraint6(solver, constraint, all_date_strs, var_dict)

        # 7. Work in pre-defined shifts
        BuildConstraint7(solver, constraint, all_date_strs, var_dict)
        
    # Create constraint 8
    for date_str in all_date_strs:
        # 8. Exactly 1 person should work in each shift
        BuildConstraint8(solver, schedule.constraints, date_str, var_dict)

            


    print(solver.NumConstraints())
   # print(solver.constraints)
    for co in solver.constraints():
        pass #print(co)


    return (solver, var_dict)
            
            
