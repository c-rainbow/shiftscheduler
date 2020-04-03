"""From Solver variables to assignment dict."""
import data
import datetime
import date_util

from ortools.linear_solver import pywraplp


# Variable name from nurse name, work date, and shift type name
def GetVariableName(name, date_str, shift_type_str):
    return 'x_%s_%s_%s' % (name, date_str, shift_type_str)


# all_dates: iterable of datetime.date
# name: iterable of str
# var_dict: dict of str to solver variable.
def ToAssignmentDict(all_dates, names, var_dict):
    assignment_dict = dict()
    for name in names:
        for work_date in all_dates:
            has_work = False
            for work_shift_type in data.ShiftType.WorkShiftTypes():
                variable = var_dict[GetVariableName(name, str(work_date), work_shift_type.name)]
                # A work shift is assigned to the person on this date.
                if variable.solution_value() == 1:
                    assignment_dict[(work_date, name)] = work_shift_type
                    has_work = True
                    break  # There should be max 1 assignment that day, by constraint 1.
            
            # Mark as 'OFF' if no work is found that day
            if not has_work:
                assignment_dict[(work_date, name)] = data.ShiftType.OFF

    return assignment_dict


# Returns TotalSchedule object from solver output
def ToTotalSchedule(software_config, person_configs, date_configs, var_dict):
    
    all_dates = list(date_util.GenerateAllDates(
        software_config.start_date, software_config.end_date))
    names = [c.name for c in person_configs]
    assignment_dict = ToAssignmentDict(all_dates, names, var_dict)

    return data.TotalSchedule(
        software_config=software_config,
        person_configs=person_configs,
        date_configs=date_configs,
        assignment_dict=assignment_dict)
