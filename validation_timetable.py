
import data
import datetime

import date_util

import functools

import validation_util as util


_UNKNOWN_SHIFT = data.ShiftType.UNKNOWN
_DAY_SHIFT = data.ShiftType.DAY
_EVENING_SHIFT = data.ShiftType.EVENING
_NIGHT_SHIFT = data.ShiftType.NIGHT
_OFF_SHIFT = data.ShiftType.OFF
_WORK_SHIFTS = data.ShiftType.WorkShiftTypes()

_DAY_NAME = data.ShiftType.DAY.name
_EVENING_NAME = data.ShiftType.EVENING.name
_NIGHT_NAME = data.ShiftType.NIGHT.name


# 1. Basic checks on work dates
def ValidateWorkDates(assignment_dict, start_date, end_date, errors):
    for (work_date, name), shift_type in assignment_dict.items():
        if type(work_date) is not datetime.date:
            errors.append('"%s" is not a valid date' % work_date)
        elif work_date < start_date:
            errors.append('Work date %s is before the start date' % work_date)
        elif end_date < work_date:
            errors.append('Work date %s is after the end date' % work_date)


# 2. Basic checks on names 
def ValidatePersonNames(assignment_dict, person_configs, errors):
    all_names_set = set(c.name for c in person_configs)
    assigned_names_set = set()
    for _, name in assignment_dict.keys():
        if name not in all_names_set:
            errors.append('Cannot find person config for %s' % name)
        assigned_names_set.add(name)
    
    extra_names = all_names_set - assigned_names_set
    if extra_names:
        errors.append('Timetable does not have following names: %s' % sorted(extra_names))


# 3. Fixed shifts cells only have allowed characters (D/d, E/e, N/n, O/o)
def ValidateShiftCodes(assignment_dict, errors, barebone=False):
    for (work_date, name), shift_type in assignment_dict.items():
        if shift_type == _UNKNOWN_SHIFT:
            errors.append('Invalid shift code for %s on %s' % (name, work_date))
        # Empty cell is allowed for barebone input
        elif not barebone and shift_type is None:
            errors.append('Shift code is empty for %s on %s' % (name, work_date))


# 4. If there is any overassigned shift (more than assigned workers as configured in date_configs)
def ValidateOverassignment(assignment_dict, date_configs, errors, barebone=False):
    for date_config in date_configs:
        work_date = date_config.work_date
        day_count = date_config.num_workers_day
        evening_count = date_config.num_workers_evening
        night_count = date_config.num_workers_night

        # For barebone config, empty cells can be filled, so only check for <=
        error_fn = util.ErrorIfGreater if barebone else util.ErrorIfNotEqual

        # Check for number of day workers
        worker_count = util.GetWorkerCount(assignment_dict, work_date, _DAY_SHIFT)
        error_fn(
            worker_count, day_count, errors,
            '%d workers are assigned for %s on %s, when there should be %d workers', worker_count,
            _DAY_NAME, work_date, day_count)

        # Check for number of evening workers
        worker_count = util.GetWorkerCount(assignment_dict, work_date, _EVENING_SHIFT)
        error_fn(
            worker_count, evening_count, errors,
            '%d workers are assigned for %s on %s, when there should be %d workers', worker_count,
            _EVENING_NAME, work_date, evening_count)

        # Check for number of night workers
        worker_count = util.GetWorkerCount(assignment_dict, work_date, _NIGHT_SHIFT)
        error_fn(
            worker_count, night_count, errors, 
            '%d workers are assigned for %s on %s, when there should be %d workers', worker_count,
            _NIGHT_NAME, work_date, night_count)


# 5-2. No day/evening work after night shift
def ValidateConstraint2(person_config, all_dates, assignment_dict, errors):
    name = person_config.name
    previously_night = False

    for work_date in all_dates:  # Assume that all_dates are sorted
        shift_type = assignment_dict.get((work_date, name))
        if previously_night and shift_type in (_DAY_SHIFT, _EVENING_SHIFT):
            errors.append('Day/evening work after night shift for %s on %s' % (name, work_date))
        
        previously_night = (shift_type == _NIGHT_SHIFT)


# 5-3. No more than n consecutive workdays
def ValidateConstraint3(person_config, all_dates, assignment_dict, errors):
    name = person_config.name
    consecutive_workdays = 0
    start_work_date = None        
    
    # Adding [None] is a trick to include consecutive workdays ending on 'end_date'
    for work_date in (all_dates + [None]): 
        shift_type = assignment_dict.get((work_date, name))
        if shift_type in _WORK_SHIFTS:
            if start_work_date is None:  # Starting a new consecutive workdays
                start_work_date = work_date
            consecutive_workdays += 1
        # shift_type can be None for barebone input.
        elif shift_type is None or shift_type == _OFF_SHIFT:
            util.ErrorIfGreater(
                consecutive_workdays, person_config.max_consecutive_workdays, errors,
                'Worker %s should work no more than %d consecutive days, but worked for %d days from %s',
                name, person_config.max_consecutive_workdays, consecutive_workdays, start_work_date)
            consecutive_workdays = 0
            start_work_date = None  


# 5-4. No more than n consecutive nights
def ValidateConstriant4(person_config, all_dates, assignment_dict, errors):
    name = person_config.name
    consecutive_nights = 0
    start_work_date = None        
    
    # Adding [None] is a trick to include consecutive nights ending on end_date
    for work_date in all_dates + [None]: 
        shift_type = assignment_dict.get((work_date, name))
        if shift_type == _NIGHT_SHIFT:
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


# 5-5. Make sure min_total_workdays <= total schedule <= max_total_workdays
def ValidateConstraint5(person_config, all_dates, assignment_dict, errors):
    name = person_config.name
    fixed_total_workdays = 0
    off_count = 0
    
    for work_date in all_dates:
        shift_type = assignment_dict.get((work_date, name))
        if shift_type in _WORK_SHIFTS:
            fixed_total_workdays += 1
        elif shift_type == _OFF_SHIFT:
            off_count += 1
    
    util.ErrorIfLess( 
        len(all_dates) - off_count, person_config.min_total_workdays, errors,
        'Worker %s should work for at least %s days, but is already scheduled to off for %d days out of %d days',
        name, person_config.min_total_workdays, off_count, len(all_dates))

    util.ErrorIfGreater(
        fixed_total_workdays, person_config.max_total_workdays, errors,
        'Worker %s should work no more than %d days, but is already scheduled to work for %d days',
        name, person_config.max_total_workdays, fixed_total_workdays)


# 6. Total required workers in the day <= number of non-off workers that day
def ValidateMinimumRequiredWorkers(date_configs, assignment_dict, num_person, errors):
    for date_config in date_configs:
        total_required = date_config.num_workers_day + date_config.num_workers_evening + date_config.num_workers_night
        off_count = util.GetWorkerCount(assignment_dict, date_config.work_date, _OFF_SHIFT)
        available_workers = num_person - off_count

        util.ErrorIfGreater(
            total_required, available_workers, errors,
            '%d workers are required on %s, but %d out of %d people already scheduled to off that day',
            total_required, date_config.work_date, off_count, num_person)


# 7. Make sure sum of minimum total workdays <= Number of non-off cells
def ValidateMinimumTotalWorkSlots(person_configs, off_count, date_count, errors):
    sum_min_workdays = functools.reduce(lambda sum, pc: sum + pc.min_total_workdays, person_configs, 0)
    non_off_count = len(person_configs) * date_count - off_count
    util.ErrorIfGreater(
        sum_min_workdays, non_off_count, errors,
        'Sum of total minimum workdays of all people are %d, but there are only %d available slots to work',
        sum_min_workdays, non_off_count)


# 8. Make sure number of non-off cells <= Sum of maximum total workdays
def ValidateMaximumTotalWorkSlots(person_configs, off_count, date_count, errors):
    sum_max_workdays = functools.reduce(lambda sum, pc: sum + pc.max_total_workdays, person_configs, 0)
    non_off_count = len(person_configs) * date_count - off_count
    util.ErrorIfGreater(
        non_off_count, sum_max_workdays, errors,
        'There are %d slots to fill, but the sum of total maximum workdays of all people are %d',
        non_off_count, sum_max_workdays)


def ValidateTimetable(software_config, date_configs, person_configs, assignment_dict, barebone=False):
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
    ValidateWorkDates(assignment_dict, software_config.start_date, software_config.end_date, errors)

    # 2. Basic checks on names 
    ValidatePersonNames(assignment_dict, person_configs, errors)

    # 3. Basic checks on shift types
    ValidateShiftCodes(assignment_dict, errors, barebone=barebone)
    
    # Value error prevents further validation
    if errors:
        return errors

    # 4. If there is any overassigned cell for barebone (more than assigned workers as configured in date_configs)
    # Also check for underassigned cell for complete assignment.
    ValidateOverassignment(assignment_dict, date_configs, errors, barebone=barebone)
     
    # 5. If a person's shifts violate any of constraint 2-5.
    # Constraint 1, 6, 7 are not part of validation.
    all_dates = date_util.GenerateAllDates(software_config.start_date, software_config.end_date)
    for person_config in person_configs:
        # 5-2. No day/evening work after night shift
        ValidateConstraint2(person_config, all_dates, assignment_dict, errors)
        # 5-3. No more than n consecutive workdays
        ValidateConstraint3(person_config, all_dates, assignment_dict, errors)   
        # 5-4. No more than n consecutive nights
        ValidateConstriant4(person_config, all_dates, assignment_dict, errors)       
        # 5-5. min_total_workdays <= total schedule <= max_total_workdays
        ValidateConstraint5(person_config, all_dates, assignment_dict, errors)

    # 6. Total required workers in the day <= number of non-off workers that day (except barebone)
    ValidateMinimumRequiredWorkers(date_configs, assignment_dict, software_config.num_person, errors)
    
    # Common variables for both check 7 and 8
    off_count = len([c for c in assignment_dict.values() if c == _OFF_SHIFT])  # Total number of OFF's
    date_count = len(date_configs)

    # 7. Make sure that sum of minimum total workdays <= Number of non-off cells
    ValidateMinimumTotalWorkSlots(person_configs, off_count, date_count, errors)
    
    # 8. Make sure number of non-off cells <= Sum of maximum total workdays
    ValidateMaximumTotalWorkSlots(person_configs, off_count, date_count, errors)

    return errors