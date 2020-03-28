
import pandas
import openpyxl  

from openpyxl import styles
from openpyxl.styles import fills

from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, FormulaRule
from openpyxl.utils import cell as xlcell
import date_util
import datetime

CONFIG_PERSON_HEADER_NAMES = (
    '최대 근무일 (연속)',
    '최대 나이트 (연속)',
    '최소 근무일 (전체)',
    '최대 근무일 (전체)',
)

CONFIG_DATE_HEADER_NAMES = (
    '데이 근무자 수',
    '이브닝 근무자 수',
    '나이트 근무자 수',
)


COLOR_MELON = 'fdbcb4'  # Peach-like soft red
COLOR_PASTEL_YELLOW = 'fdfd96'
COLOR_AERO_BLUE = 'c9ffe5'
COLOR_LIGHT_GRAY = 'bbbbbb'

fff1 = styles.PatternFill(fill_type=fills.FILL_SOLID, start_color=COLOR_MELON, end_color=COLOR_MELON)
fff2 = styles.PatternFill(fill_type=fills.FILL_SOLID, start_color=COLOR_AERO_BLUE, end_color=COLOR_AERO_BLUE)
fff3 = styles.PatternFill(fill_type=fills.FILL_SOLID, start_color=COLOR_PASTEL_YELLOW, end_color=COLOR_PASTEL_YELLOW)
fff4 = styles.PatternFill(fill_type=fills.FILL_SOLID, start_color=COLOR_LIGHT_GRAY, end_color=COLOR_LIGHT_GRAY)


def AllNamesUnique(names):
    return len(names) == len(set(names))



# ws: Excel sheet
# names: names of people. Must be all unique
# start_date: datetime.date. First date to write to Excel file
# end_date: datetime.date. Last date to write to Excel file
def CreateBareboneTimetable(ws, names, start_date, end_date, row_offset=0, col_offset=0):
    
    # TODO: Create custom exceptions
    if not AllNamesUnique(names):
        raise Exception("Duplicate names")
    if start_date > end_date:
        raise Exception("Start date is later than end date")
    
    # Fill the head rows with people's names
    # Note that row/col indexes are 1-based in Excel    
    names = sorted(names)
    for i, name in enumerate(names):
        c = ws.cell(row=i+2+row_offset, column=1+col_offset)
        c.value = name
    
    # Fill the head columns with dates
    all_dates = list(date_util.GenerateAllDates(start_date, end_date))
    for i, work_date in enumerate(all_dates):
        c = ws.cell(row=1+row_offset, column=i+2+col_offset)
        c.value = work_date

    # Add conditional formatting to cells
    start_row = 2 + row_offset
    start_col = 2 + col_offset
    end_row = start_row + len(names) - 1
    end_col = start_col + len(all_dates) - 1

    start_cell_name = xlcell.get_column_letter(start_col) + str(start_row)
    end_cell_name = xlcell.get_column_letter(end_col) + str(end_row)

    cell_range_str = start_cell_name + ":" + end_cell_name

    ws.conditional_formatting.add(cell_range_str, CellIsRule(operator='==', formula=['"D"'], fill=fff1))
    ws.conditional_formatting.add(cell_range_str, CellIsRule(operator='==', formula=['"E"'], fill=fff2))
    ws.conditional_formatting.add(cell_range_str, CellIsRule(operator='==', formula=['"N"'], fill=fff3))
    ws.conditional_formatting.add(cell_range_str, CellIsRule(operator='==', formula=['"O"'], fill=fff4))



def CreateBarebonePersonConfig(ws, names, row_offset=0, col_offset=0):
    
    # Fill the head rows with people's names
    # Note that row/col indexes are 1-based in Excel    
    names = sorted(names)
    for i, name in enumerate(names):
        c = ws.cell(row=i+2+row_offset, column=1+col_offset)
        c.value = name

    # Fill the head columns with config names
    for i, config_display_name in enumerate(CONFIG_PERSON_HEADER_NAMES):
        c = ws.cell(row=1+row_offset, column=i+2+col_offset)
        c.value = config_display_name
        

def CreateBareboneDateConfig(ws, start_date, end_date, row_offset=0, col_offset=0):
    
    # Fill the head rows with dates
    # Note that row/col indexes are 1-based in Excel    
    all_dates = list(date_util.GenerateAllDates(start_date, end_date))
    for i, work_date in enumerate(all_dates):
        c = ws.cell(row=i+2+row_offset, column=1+col_offset)
        c.value = work_date

    # Fill the head columns with config names
    for i, config_display_name in enumerate(CONFIG_DATE_HEADER_NAMES):
        c = ws.cell(row=1+row_offset, column=i+2+col_offset)
        c.value = config_display_name
    

wb = openpyxl.Workbook()
start_date = datetime.date.fromisoformat('2020-02-04')
end_date = datetime.date.fromisoformat('2020-03-16')
names = ["간호사1", "간호사4", "간호사2", "간호사3"]
CreateBareboneTimetable(wb.active, names, start_date, end_date,
    row_offset=2, col_offset=3)

ws = wb.create_sheet(title="간호사별 설정")
CreateBarebonePersonConfig(ws, names, row_offset=5, col_offset=2)

ws = wb.create_sheet(title="날짜별 설정")
CreateBareboneDateConfig(ws, start_date, end_date, row_offset=2, col_offset=1)

wb.save("sample.xlsx")