import collections
import openpyxl  

from openpyxl import styles
from openpyxl.styles import fills

from openpyxl.formatting import rule as xlrule
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, FormulaRule
from openpyxl.utils import cell as xlcell
import date_util
import datetime
import data


# Config data from Excel file
Config = collections.namedtuple('Config', ['start_date', 'end_date', 'num_person'])



def GetShiftType(code):
    if code in ('D', 'd'):
        return data.ShiftType.DAY
    elif code in ('E', 'e'):
        return data.ShiftType.EVENING
    elif code in ('N', 'n'):
        return data.ShiftType.NIGHT
    elif code in ('O', 'o'):
        return data.ShiftType.OFF
    return None



# Returns dict of (datetime.date, str) -> data.ShiftType. assignment dict
def ReadTimetable(ws, config, constraints, start_row=1, start_col=1):
   
    total_dates = (config.end_date - config.start_date).days + 1
    num_person = config.num_person

    assignment_dict = dict()

    for row_index in range(start_row+1, start_row+num_person+1):
        name_cell = ws.cell(row=row_index, column=start_col)
        name = name_cell.value

        for col_index in range(start_col+1, start_col+total_dates+1):
            date_cell = ws.cell(row=start_row, column=col_index)
            work_date = date_cell.value
            
            shift_cell = ws.cell(row=row_index, column=col_index)
            shift_type = GetShiftType(shift_cell.value)
            
            if shift_type is not None:
                assignment_dict[(work_date, name)] = shift_type

    return assignment_dict
    

# Returns list of data.Constraint
def ReadPersonConstraints(ws, config, start_row=1, start_col=1):
    constraints = []
    for row_index in range(start_row+1, start_row+config.num_person+1):
        name_cell = ws.cell(row=row_index, column=start_col)
        constraint = data.Constraint(name_cell.value)

        mcw_cell = ws.cell(row=row_index, column=start_col+1)
        constraint.max_consecutive_workdays = mcw_cell.value

        mcn_cell = ws.cell(row=row_index, column=start_col+2)
        constraint.max_consecutive_nights = mcn_cell.value

        min_tw_cell = ws.cell(row=row_index, column=start_col+3)
        constraint.min_total_workdays = min_tw_cell.value

        max_tw_cell = ws.cell(row=row_index, column=start_col+4)
        constraint.max_total_workdays = max_tw_cell.value

        constraints.append(constraint)
    
    return constraints
    


# Returns list of data.DateConstraint
def ReadDateConstraint(ws, config, start_row=1, start_col=1):
    date_constraints = []

    total_dates = (config.end_date - config.start_date).days + 1
    for row_index in range(start_row+1, start_row+total_dates+1):
        date_cell = ws.cell(row=row_index, column=start_col)
        work_date = date_cell.value

        day_cell = ws.cell(row=row_index, column=start_col+1)
        num_workers_day = day_cell.value

        evening_cell = ws.cell(row=row_index, column=start_col+2)
        num_workers_evening = evening_cell.value

        night_cell = ws.cell(row=row_index, column=start_col+3)
        num_workers_night = night_cell.value

        date_constraint = data.DateConstraint(
            work_date, num_workers_day, num_workers_evening, num_workers_night)
        date_constraints.append(date_constraint)
    
    return date_constraints



# Returns Config
def ReadSoftwareConfig(ws):
    # TODO: Do not hardcode the cell indexes
    return Config(start_date=ws['B1'].value, end_date=ws['B2'].value, num_person=ws['B3'].value)
    

# Read Excel file and convert to (data.Schedule, data.Assignment) objects
def ReadFromExcelFile(filepath):
    wb = openpyxl.load_workbook(filepath, keep_vba=False) 

    ws = wb['Config']
    config = ReadSoftwareConfig(ws)
    
    ws= wb['간호사별 설정']
    constraints = ReadPersonConstraints(ws, config)
    
    ws = wb['날짜별 설정']
    date_constraints = ReadDateConstraint(ws, config)

    ws = wb['일정표']
    assignment_dict = ReadTimetable(ws, config, constraints)

    # Crate schedule object
    schedule = data.Schedule(config.start_date, config.end_date)
    for constraint in constraints:
        schedule.AddConstraint(constraint)
    for date_constraint in date_constraints:
        schedule.AddDateConstraint(date_constraint)

    all_dates = date_util.GenerateAllDates(config.start_date, config.end_date)
    all_names = [constraint.name for constraint in constraints]
    assignments = data.Assignment(assignment_dict, schedule, all_dates, all_names)

    return (schedule, assignments)



if __name__ == '__main__':
    schedule, assignments = ReadFromExcelFile('tmp/sample.xlsx')
    print(schedule)
    print(assignments)