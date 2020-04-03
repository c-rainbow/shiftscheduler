
import excel_input
import excel_output
import solver_input
import solver_output


if __name__ == '__main__':
    base_schedule = excel_input.ReadFromExcelFile('tmp/sample.xlsx')
    solver, var_dict = solver_input.FromTotalSchedule(base_schedule)

    status = solver.Solve()
    print('Status:', status)

    new_schedule = solver_output.ToTotalSchedule(
        base_schedule.software_config, base_schedule.person_configs, base_schedule.date_configs, var_dict)

    excel_output.FromTotalSchedule(new_schedule, 'tmp/updated.xlsx')
