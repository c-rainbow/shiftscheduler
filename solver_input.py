
from ortools.linear_solver import pywraplp

import datetime

import data 
import functools
import date_util

_DAY_NAME = data.ShiftType.DAY.name
_EVENING_NAME = data.ShiftType.EVENING.name
_NIGHT_NAME = data.ShiftType.NIGHT.name


# Variable name from nurse name, work date, and shift type name
def GetVariableName(name, date_str, shift_type_str):
    return 'x_%s_%s_%s' % (name, date_str, shift_type_str)


# Sum of solver "variables". Works for both MIP and CP solvers
def VariableSum(variables):
    return functools.reduce(lambda x, y: x + y, variables)


# 1. only work one shift in one day
def BuildConstraint1(solver, person_config, all_date_strs, var_dict):
    for date_str in all_date_strs:
        vars = []
        for shift_type in data.ShiftType.WorkShiftNames():
            var_name = GetVariableName(person_config.name, date_str, shift_type)
            vars.append(var_dict[var_name])

        solver.Add(VariableSum(vars) <= 1)


# 2. After night shift, no work next day/evening
def BuildConstraint2(solver, person_config, all_date_strs, var_dict):
    for i in range(len(all_date_strs)-1):
        work_date_str = all_date_strs[i]
        next_date_str = all_date_strs[i+1]

        night_var = var_dict[GetVariableName(person_config.name, work_date_str, _NIGHT_NAME)]
        day_var = var_dict[GetVariableName(person_config.name, next_date_str, _DAY_NAME)]
        evening_var = var_dict[GetVariableName(person_config.name, next_date_str, _EVENING_NAME)]

        solver.Add(night_var + day_var + evening_var <= 1)


# 3. no more than n consecutive workdays
def BuildCosntraint3(solver, person_config, all_date_strs, var_dict):
    max_days = person_config.max_consecutive_workdays
    for from_index in range(len(all_date_strs) - max_days):
        vars = []
        for i in range(max_days + 1):
            for shift_type_str in data.ShiftType.WorkShiftNames():
                var_name = GetVariableName(
                        person_config.name, all_date_strs[from_index + i], shift_type_str)
                vars.append(var_dict[var_name])
        
        solver.Add(VariableSum(vars) <=  max_days)


# 4. no more than m consecutive nights
def BuildConstraint4(solver, person_config, all_date_strs, var_dict):   
    max_nights = person_config.max_consecutive_nights
    for from_index in range(len(all_date_strs) - max_nights):
        vars = []
        for i in range(max_nights + 1):
            var_name = GetVariableName(
                    person_config.name, all_date_strs[from_index + i], _NIGHT_NAME)
            vars.append(var_dict[var_name])
        
        solver.Add(VariableSum(vars) <=  max_nights)


# 5. Minimum a, maximum b total workdays
def BuildConstraint5(solver, person_config, all_date_strs, var_dict):
    vars = []
    for date_str in all_date_strs:
        for shift_type_str in data.ShiftType.WorkShiftNames():
            var_name = GetVariableName(person_config.name, date_str, shift_type_str)
            vars.append(var_dict[var_name])

    var_sum = VariableSum(vars)
    solver.Add(person_config.min_total_workdays <= var_sum)
    solver.Add(var_sum <= person_config.max_total_workdays)


# 6. No work on off-shifts
def BuildConstraint6(solver, assignment_dict, var_dict):
    for (work_date, name), fixed_shift in assignment_dict.items():
        if fixed_shift is None:
            continue
        
        var_name = GetVariableName(name, str(work_date), fixed_shift.name)
        if fixed_shift == data.ShiftType.OFF:
            for work_shift_type in data.ShiftType.WorkShiftNames():
                work_var_name = GetVariableName(name, str(work_date), work_shift_type)
                solver.Add(var_dict[work_var_name] == 0)
        else:
            solver.Add(var_dict[var_name] == 1)


# 7. Match the number of workers in a specific shift
def BuildConstraint7(solver, person_configs, date_config, var_dict):
    date_str = str(date_config.work_date)

    vars_day = []
    vars_evening = []
    vars_night = []
    for person_config in person_configs:
        var_name = GetVariableName(person_config.name, date_str, _DAY_NAME)
        vars_day.append(var_dict[var_name])

        var_name = GetVariableName(person_config.name, date_str, _EVENING_NAME)
        vars_evening.append(var_dict[var_name])

        var_name = GetVariableName(person_config.name, date_str, _NIGHT_NAME)
        vars_night.append(var_dict[var_name])
    
    solver.Add(VariableSum(vars_day) == date_config.num_workers_day)
    solver.Add(VariableSum(vars_evening) == date_config.num_workers_evening)
    solver.Add(VariableSum(vars_night) == date_config.num_workers_night)


def Build(software_config, person_configs, date_configs, assignment_dict):
    """Returns (solver, var_dict)
    
    assignment_dict: dict of (datetime.date, str) -> data.ShiftType, assignment dict
    
    """

    solver = pywraplp.Solver(
            'scheduling_program', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    var_dict = dict()         
    all_date_strs = list(date_util.GenerateAllDateStrs(software_config.start_date, software_config.end_date))   

    # Create variables
    for work_date in all_date_strs:
        for person_config in person_configs:
            for shift_type_str in data.ShiftType.WorkShiftNames():
                var_name = GetVariableName(person_config.name, work_date, shift_type_str)
                var_dict[var_name] = solver.BoolVar(var_name)
            
    # Create constraints 1-7
    for person_config in person_configs:
        # 1. only work one shift in one day
        BuildConstraint1(solver, person_config, all_date_strs, var_dict)

        # 2. After night shift, no work next day/evening
        BuildConstraint2(solver, person_config, all_date_strs, var_dict)

        # 3. no more than n consecutive workdays
        BuildCosntraint3(solver, person_config, all_date_strs, var_dict)

        # 4. no more than m consecutive nights
        BuildConstraint4(solver, person_config, all_date_strs, var_dict)

        # 5. Minimum a, maximum b total workdays
        BuildConstraint5(solver, person_config, all_date_strs, var_dict)

        # 6. No work on off-shifts & Work in predefined shift
        BuildConstraint6(solver, assignment_dict, var_dict)
        
    # 7. Match the number of workers in each shift
    for date_config in date_configs:
        BuildConstraint7(solver, person_configs, date_config, var_dict)

    return (solver, var_dict)


# Wrapper function to convert from TotalSchedule to (solver, var_dict)
def FromTotalSchedule(total_schedule):
    return Build(
        total_schedule.software_config,
        total_schedule.person_configs, 
        total_schedule.date_configs,
        total_schedule.assignment_dict)



if __name__ == '__main__':
    print('hello')
    config = data.SoftwareConfig(
        start_date=datetime.date(2020, 3, 1), 
        end_date=datetime.date(2020, 3, 3),
        num_person=1)


    Build(config, [], [], {})

