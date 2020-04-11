import sys

from shiftscheduler.excel import input as excel_input
from shiftscheduler.excel import output as excel_output
from shiftscheduler.solver import input as solver_input
from shiftscheduler.solver import output as solver_output
from shiftscheduler.validation import validator


_INPUT_FILE_PATH = 'shiftscheduler/tmp/sample.xlsx'
_OUTPUT_FILE_PATH = 'shiftscheduler/tmp/updated.xlsx'


# 1. Read input Excel file (pre-configured with values)
# 2. Validate the input file
# 3. Run the solver
# 4. Validate solver output (just to make sure)
# 5. Write to the output file
if __name__ == '__main__':
    base_schedule = excel_input.ReadFromExcelFile(_INPUT_FILE_PATH)
    errors = validator.ValidateTotalScheduleFormat(base_schedule, barebone=True)
    print('errors', errors)
    if errors:
        sys.exit(0)
    solver, var_dict = solver_input.FromTotalSchedule(base_schedule)

    status = solver.Solve()
    print('Status:', status)

    new_schedule = solver_output.ToTotalSchedule(
        base_schedule.software_config, base_schedule.person_configs, base_schedule.date_configs, var_dict)
    
    errors = validator.ValidateTotalScheduleFormat(new_schedule, barebone=False)
    print('new errors', errors)
    if errors:
        sys.exit(0)
    excel_output.FromTotalSchedule(new_schedule, _OUTPUT_FILE_PATH)
