
import data
import datetime

import date_util

import functools


import validation_util as util
import validation_timetable 

# TODO: For now, errors are simply string messages.
# In the future, change these messages to structured error objects

_DAY_NAME = data.ShiftType.DAY.name
_EVENING_NAME = data.ShiftType.EVENING.name
_NIGHT_NAME = data.ShiftType.NIGHT.name


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
                date_config.num_workers_day, errors, 'No number of %s workers on %s', _DAY_NAME, work_date)
            util.ErrorIfNone(
                date_config.num_workers_evening, errors, 'No number of %s workers on %s', _EVENING_NAME, work_date)
            util.ErrorIfNone(
                date_config.num_workers_night, errors, 'No number of %s workers on %s', _NIGHT_NAME, work_date)

        # Check for invalid values
        util.ErrorIfNaNOrNegative(
            date_config.num_workers_day, errors, '"%s" is invalid number of %s workers on %s',
            date_config.num_workers_day, _DAY_NAME, work_date)
        util.ErrorIfNaNOrNegative(
            date_config.num_workers_evening, errors, '"%s" is invalid number of %s workers on %s',
            date_config.num_workers_evening, _EVENING_NAME, work_date)
        util.ErrorIfNaNOrNegative(
            date_config.num_workers_night, errors, '"%s" is invalid number of %s workers on %s',
            date_config.num_workers_night, _NIGHT_NAME, work_date)

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

    # Check for empty config values.
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





def ValidateTotalScheduleFormat(total_schedule, barebone=False):
    # Any error in software config will block further process
    errors = ValidateSoftwareConfig(total_schedule.software_config)
    if errors:
        return errors

    # Person configs validation and date configs validation can be done in parallel
    dc_errors = ValidateDateConfigs(
        total_schedule.software_config, total_schedule.date_configs, barebone=barebone)
    pc_errors = ValidatePersonConfigs(
        total_schedule.software_config, total_schedule.person_configs, barebone=barebone)
    if dc_errors or pc_errors:
        return dc_errors + pc_errors

    # If no error is found in other sheets, validate the timetable
    tt_errors = validation_timetable.ValidateTimetable(
        total_schedule.software_config, total_schedule.date_configs, total_schedule.person_configs,
        total_schedule.assignment_dict, barebone=barebone)
    return tt_errors
    