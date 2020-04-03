
import data
import datetime

import date_util

import functools


from . import util as util

# TODO: For now, errors are simply string messages.
# In the future, change these messages to structured error objects

_DAY_NAME = data.ShiftType.DAY.name
_EVENING_NAME = data.ShiftType.EVENING.name
_NIGHT_NAME = data.ShiftType.NIGHT.name

def GetAllWorkShifts(assignment_dict, expected_date, expected_shift_type):
    names = []
    for (work_date, name), shift_type in assignment_dict.items():
        if work_date == expected_date and shift_type == expected_shift_type:
            names.append(name)

    return names


def ValidateSoftwareConfig(software_config):
    # Software config sheet
    # 1. start_date is valid datetime.date
    # 2. end_date is valid datetime.date
    # 3. num_person is non-empty, number, int, and non-negative
    # 4. Make sure that start_date <= end_date
    start_date = software_config.start_date
    end_date = software_config.end_date

    errors = []
    if start_date is None:
        errors.append('Start date is empty')
    elif type(start_date) is not datetime.date:
        errors.append('Start date %s is not a valid date' % start_date)

    if end_date is None:
        errors.append('End date is empty')   
    elif type(end_date) is not datetime.date:
        errors.append('End date %s is not a valid date' % end_date)
    
    if errors:
        return errors

    if start_date > end_date:
        return ['Start date is later than the end date']

    return []


def ValidateDateConfigs(software_config, date_configs, barebone=False):
    # Date config sheet
    # 1. Has all dates between start_date and end_date
    # 2. All cell values are non-empty, number, int, and non-negative (except barebone)
    all_dates = set(date_util.GenerateAllDates(software_config.start_date, software_config.end_date))

    errors = []
    missing_dates = []
    for date_config in date_configs:
        work_date = date_config.work_date
        if util.ErrorIfNone(work_date, errors, 'Empty work date is found'):
            continue

        if work_date not in all_dates:
            missing_dates.append(work_date)
            continue
        all_dates.remove(work_date)

        if not barebone:
            # Check for empty values
            util.ErrorIfNone(
                work_date.num_workers_day, errors, 'No number of %s workers on %s', _DAY_NAME, work_date)
            util.ErrorIfNone(
                work_date.num_workers_evening, errors, 'No number of %s workers on %s', _EVENING_NAME, work_date)
            util.ErrorIfNone(
                work_date.num_workers_night, errors, 'No number of %s workers on %s', _NIGHT_NAME, work_date)

        # Check for invalid values
        util.ErrorIfNaNOrNegative(
            work_date.num_workers_day, errors, '"%s" is invalid number of %s workers on %s',
            work_date.num_workers_day, _DAY_NAME, work_date)
        util.ErrorIfNaNOrNegative(
            work_date.num_workers_evening, errors, '"%s" is invalid number of %s workers on %s',
            work_date.num_workers_evening, _EVENING_NAME, work_date)
        util.ErrorIfNaNOrNegative(
            work_date.num_workers_night, errors, '"%s" is invalid number of %s workers on %s',
            work_date.num_workers_night, _NIGHT_NAME, work_date)

    if all_dates:  # Some dates do not have config
        errors.append('%d dates do not have date configs, %s' % (len(all_dates), all_dates))
    if missing_dates:  # Some date configs are out of range
        errors.append('%d dates are missing in date configs, %s' % (len(missing_dates), missing_dates))
    
    return errors
    


def ValidatePersonConfigs(software_config, person_configs, barebone=False):
    # Person Config sheet
    # 1. All names unique
    # 2. Exactly num_person of workers
    # 3. All cell values are non-empty, number, int, and non-negative (except barebone)
    # 4. Max consecutive workdays >= max nights (except barebone)
    # 5. min total workdays <= max total workdays (except barebone)
    errors = []

    all_names = [c.name for c in person_configs]
    if len(all_names) != len(set(all_names)):
        errors.append('All person names should be unique in Persons sheet')
        return errors

    if len(person_configs) != software_config.num_person:
        errors.append(
            'There should be %d people, but there are rows for %s people in Persons sheet',
            software_config.num_person, len(person_configs))

    # Check for empty config values. Skipped for barebone Excel file
    if not barebone:
        for pc in person_configs:
            util.ErrorIfNone(
                pc.max_consecutive_workdays, errors, 'No number for max consecutive workdays for %s',
                pc.name)
            util.ErrorIfNone(
                pc.max_consecutive_nights, errors, 'No number for max consecutive nights for %s',
                pc.name)
            util.ErrorIfNone(
                pc.min_total_workdays, errors, 'No number for min total workdays for %s',
                pc.name)
            util.ErrorIfNone(
                pc.max_total_workdays, errors, 'No number for max total workdays for %s',
                pc.name)

    # Check for invalid config values 
    for pc in person_configs:
        util.ErrorIfNaNOrNegative(
            pc.max_consecutive_workdays, errors, '"%s" is invalid number for %s',
            pc.max_consecutive_workdays, pc.name)
        util.ErrorIfNaNOrNegative(
            pc.max_consecutive_nights, errors, '"%s" is invalid number for %s',
            pc.max_consecutive_nights, pc.name)
        util.ErrorIfNaNOrNegative(
            pc.min_total_workdays, errors, '"%s" is invalid number for %s',
            pc.min_total_workdays, pc.name)
        util.ErrorIfNaNOrNegative(
            pc.max_total_workdays, errors, '"%s" is invalid number for %s',
            pc.max_total_workdays, pc.name)

    return errors


def ValidateTimetable(assignment_dict, software_config, date_configs, person_configs, barebone=False):
    # Timetable validation
    # 1. Has all dates between start_date and end_date, consecutive
    # 2. Has exactly the names in person configs
    # 3. Fixed shifts cells only have allowed characters (D/d, E/e, N/n, O/o)  (also empty if barebone)
    # 
    # 4. If there is any overassigned cell (more than assigned workers as configured in date_configs) (except barebone)
    # 5. If a person's shifts violate any of constraint 1-6 (except barebone)
    # 6. Total required workers in the day <= number of non-off workers that day (except barebone)
    # 7. Make sure sum of minimum total workdays <= Number of non-off cells
    # 8. Make sure number of non-off cells <= Sum of maximum total workdays
    errors = []
    # 1. Basic checks on work dates
    for (work_date, name), shift_type in assignment_dict.items():
        if type(work_date) is not datetime.date:
            errors.append('%s is not a valid date' % work_date)
        elif work_date< software_config.start_date:
            errors.append('Work date %s is before the start date' % work_date)
        elif software_config.end_date < work_date:
            errors.append('Work date %s is after the end date' % work_date)
        # Should it give error on invalid shift on invalid date?
        if not errors and shift_type == data.ShiftType.UNKNOWN:
            errors.append('Invalid shift code for %s on %s' % (name, work_date))

    # 2. Basic checks on names 
    all_names_set = set(c.name for c in person_configs)
    all_timetable_names = set()
    for _, name in assignment_dict.values():
        if name not in all_names_set:
            errors.append('Cannot find person config for %s' % name)
        if name in all_timetable_names:
            errors.append('Name %s is duplicate in timetable' % name)
        all_timetable_names.add(name)
    
    # Value error prevents further validation
    if errors:
        return errors

    # 4. If there is any overassigned cell for barebone (more than assigned workers as configured in date_configs)
    # Also check for underassigned cell for complete assignment.
    for date_config in date_configs:
        if barebone:  # For barebone config, empty cells can be filled, so only check for <=
            worker_count = len(GetAllWorkShifts(assignment_dict, work_date, data.ShiftType.DAY))
            util.ErrorIfGreater(
                worker_count, date_config.num_workers_day,
                '%d workers are assigned for %s on %s, when there can be only %d workers', worker_count,
                _DAY_NAME, date_config.work_date, date_config.num_workers_day)
            worker_count = len(GetAllWorkShifts(assignment_dict, work_date, data.ShiftType.EVENING))
            util.ErrorIfGreater(
                worker_count, date_config.num_workers_evening,
                '%d workers are assigned for %s on %s, when there can be only %d workers', worker_count,
                _EVENING_NAME, date_config.work_date, date_config.num_workers_evening)
            worker_count = len(GetAllWorkShifts(assignment_dict, work_date, data.ShiftType.NIGHT))
            util.ErrorIfGreater(
                worker_count, date_config.num_workers_night, errors,
                '%d workers are assigned for %s on %s, when there can be only %d workers', worker_count,
                _NIGHT_NAME, date_config.work_date, date_config.num_workers_night)
        else:  # For non-barebone complete assignment, the values must match.
            worker_count = len(GetAllWorkShifts(assignment_dict, work_date, data.ShiftType.DAY))
            util.ErrorIfNotEqual(
                worker_count, date_config.num_workers_day,
                '%d workers are assigned for %s on %s, when there can be only %d workers', worker_count,
                _DAY_NAME, date_config.work_date, date_config.num_workers_day)
            worker_count = len(GetAllWorkShifts(assignment_dict, work_date, data.ShiftType.EVENING))
            util.ErrorIfNotEqual(
                worker_count, date_config.num_workers_evening,
                '%d workers are assigned for %s on %s, when there can be only %d workers', worker_count,
                _EVENING_NAME, date_config.work_date, date_config.num_workers_evening)
            worker_count = len(GetAllWorkShifts(assignment_dict, work_date, data.ShiftType.NIGHT))
            util.ErrorIfNotEqual(
                worker_count, date_config.num_workers_night, errors,
                '%d workers are assigned for %s on %s, when there can be only %d workers', worker_count,
                _NIGHT_NAME, date_config.work_date, date_config.num_workers_night)


    # 5. If a person's shifts violate any of constraint 2-5. (except barebone)
    # Constraint 1, 6, 7 are not part of validation.
    all_dates = date_util.GenerateAllDates(software_config.start_date, software_config.end_date)
    
    # 5-2. No day/evening work after night shift
    for person_config in person_configs:
        name = person_config.name
        previously_night = False
        for work_date in all_dates:
            shift_type = assignment_dict.get((work_date, name))
            if previously_night and shift_type in (data.ShiftType.DAY, data.ShiftType.EVENING):
                errors.append('Day/evening work after night shift for %s on %s' % (name, work_date))
            
            previously_night = True if shift_type == data.ShiftType.NIGHT else False

    # 5-3. No more than n consecutive workdays
    for person_config in person_configs:
        name = person_config.name
        consecutive_workdays = 0
        start_work_date = None        
        
        # Adding [None] is a trick to include consecutive workdays till end_date
        for work_date in all_dates + [None]: 
            shift_type = assignment_dict.get((work_date, name))
            if shift_type in data.ShiftType.WorkShiftTypes():
                if start_work_date is None:  # Starting a new consecutive workdays
                    start_work_date = work_date
                consecutive_workdays += 1
            elif shift_type is None or shift_type == data.ShiftType.OFF:
                util.ErrorIfGreater(
                    consecutive_workdays, person_config.max_consecutive_workdays, errors,
                    'Worker %s should work no more than %d consecutive days, but worked for %d days from %s',
                    name, person_config.max_consecutive_workdays, consecutive_workdays, start_work_date)
                consecutive_workdays = 0
                start_work_date = None       

    # 5-4. No more than n consecutive nights
    for person_config in person_configs:
        name = person_config.name
        consecutive_nights = 0
        start_work_date = None        
        
        # Adding [None] is a trick to include consecutive nights till end_date
        for work_date in all_dates + [None]: 
            shift_type = assignment_dict.get((work_date, name))
            if shift_type == data.ShiftType.NIGHT:
                if start_work_date is None:  # Starting a new consecutive nights
                    start_work_date = work_date
                consecutive_nights += 1 
            else:
                util.ErrorIfGreater(
                    consecutive_nights, person_config.max_consecutive_nights, errors,
                    'Worker %s should work no more than %d consecutive nights, but worked for %d nights from %s',
                    name, person_config.max_consecutive_nights, consecutive_nights, start_work_date)
                consecutive_nights = 0
                start_work_date = None       
    
    # 5-5. min_total_workdays <= total schedule <= max_total_workdays
    for person_config in person_configs:
        name = person_config.name
        fixed_total_workdays = 0
        off_count = 0
        
        for work_date in all_dates:
            shift_type = assignment_dict.get((work_date, name))
            if shift_type in data.ShiftType.WorkShiftTypes():
                fixed_total_workdays += 1
            elif shift_type == data.ShiftType.OFF:
                off_count += 1
        
        util.ErrorIfLess( 
            len(all_dates) - off_count, person_config.min_total_workdays, errors,
            'Worker %s should work for at least %s days, but is already scheduled to off for %d days out of %d days',
            name, person_config.min_total_workdays, off_count, len(all_dates))

        util.ErrorIfGreater(
            fixed_total_workdays, person_config.max_total_workdays, errors,
            'Worker %s should work no more than %d days, but is already scheduled to work for %d days',
            name, person_config.max_total_workdays, fixed_total_workdays)

    # 6. Total required workers in the day <= number of non-off workers that day (except barebone)
    num_person = software_config.num_person
    for date_config in date_configs:
        total_required = date_config.num_workers_day + date_config.num_workers_evening + date_config.num_workers_night
        off_count = len(GetAllWorkShifts(assignment_dict, work_date, data.ShiftType.OFF))
        available_workers = num_person - off_count

        util.ErrorIfGreater(
            total_required, available_workers, errors,
            '%d workers are required on %s, but %d out of %d people scheduled to off that day',
            total_required, date_config.work_date, off_count, num_person)
    
    # 7. Make sure that sum of minimum total workdays <= Number of non-off cells
    sum_min_workdays = functools.reduce(lambda sum, pc: sum + pc.min_total_workdays, person_configs, initializer=0)
    off_count = len([c for c in assignment_dict.values() if c == data.ShiftType.OFF])
    non_off_count = len(person_configs) * len(date_configs) - off_count
    util.ErrorIfGreater(
        sum_min_workdays, non_off_count, errors,
        'Sum of total minimum workdays of all people are %d, but there are only %d available slots to work',
        sum_min_workdays, non_off_count)
    
    # 8. Make sure number of non-off cells <= Sum of maximum total workdays
    sum_max_workdays = functools.reduce(lambda sum, pc: sum + pc.max_total_workdays, person_configs, initializer=0)
    util.ErrorIfGreater(
        non_off_count, sum_max_workdays, errors,
        'There are %d slots to fill, but the sum of total maximum workdays of all people are %d',
        non_off_count, sum_max_workdays)

    return errors


def ValidateTotalScheduleFormat(total_schedule, barebone=False):
    # Any error in software config will block further process
    errors = ValidateSoftwareConfig(total_schedule.software_configs)
    if errors:
        return errors

    # Person configs validation and date configs validation can be done in parallel
    dc_errors = ValidateDateConfigs(
        total_schedule.software_config, total_schedule.software_configs, barebone=barebone)
    pc_errors = ValidatePersonConfigs(
        total_schedule.software_config, total_schedule.person_configs, barebone=barebone)
    if dc_errors or pc_errors:
        return dc_errors + pc_errors

    # If no error is found in other sheets, validate the timetable
    tt_errors = ValidateTimetable(
        total_schedule.software_config, total_schedule.date_configs, total_schedule.person_configs,
        total_schedule.assignment_dict, barebone=barebone)
    return tt_errors
    