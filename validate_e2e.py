
import excel_input


import validation_scheduling as validation


if __name__ == '__main__':
    base_schedule = excel_input.ReadFromExcelFile('tmp/updated.xlsx')
    
    errors = validation.ValidateTotalScheduleFormat(base_schedule)
    print(errors)