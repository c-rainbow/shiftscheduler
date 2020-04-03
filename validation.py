


def ValidateTotalScheduleFormat(total_schedule, barebone=False):
    sw_config = total_schedule.software_config
    # To validate
    # Timetable sheet
    # 1. Has all dates between start_date and end_date, consecutive
    # 2. Has all names in person configs
    # 3. Fixed shifts cells only have allowed characters (D/d, E/e, N/n, O/o, or empty)
    # 
    # 4. If there is any overassigned cell (more than assigned workers as configured in date_configs)
    # 5. If a person's shifts violate any of constraint 1-6
    # 6. Total required workers in the day <= number of non-off workers that day
    # 
    # Person Config sheet
    # 1. All names unique
    # 2. Exactly num_person of workers
    # 3. All cell values are non-empty, number, int, and non-negative
    # 4. Max consecutive workdays >= max nights
    # 5. min total workdays <= max total workdays
    # 
    # Date config sheet
    # 1. Has all dates between start_date and end_date, consecutive
    # 2. All cell values are non-empty, number, int, and non-negative
    # 
    # Software config sheet
    # 1. start_date is valid datetime.date
    # 2. end_date is valid datetime.date
    # 3. num_person is non-empty, number, int, and non-negative

