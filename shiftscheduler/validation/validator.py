
import datetime
import gettext

from shiftscheduler.data_types import data_types
from shiftscheduler.util import date_util
from shiftscheduler.validation import constants_kr as constants
from shiftscheduler.validation import timetable
from shiftscheduler.validation import util


# TODO: For now, errors are simply string messages.
# In the future, change these messages to structured error objects

_DAY_NAME = data_types.ShiftType.DAY.name
_EVENING_NAME = data_types.ShiftType.EVENING.name
_NIGHT_NAME = data_types.ShiftType.NIGHT.name


_ = gettext.gettext 



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
        errors.append(constants.EMPTY_START_DATE)
    elif type(start_date) is not datetime.date:        
        util.AddError(
            errors, _('Start date {start_date} is not a valid date'), start_date=start_date)

    if end_date is None:
        util.AddError(errors, _('End date is empty'))
    elif type(end_date) is not datetime.date:
        util.AddError(errors, _('End date {end_date} is not a valid date'), end_date=end_date)
    
    if errors:
        return errors

    if start_date > end_date:
        return [_('Start date is later than the end date')]

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
        if util.ErrorIfNone(work_date, errors, _('Empty work date is found')):
            continue

        if work_date not in all_dates:
            missing_dates.append(work_date)
            continue
        all_dates.remove(work_date)

        if not barebone:
            # Check for empty values
            util.ErrorIfNone(
                date_config.num_workers_day, errors, _('No number of {shift_type} workers on {work_date}'),
                shift_type=_DAY_NAME, work_date=work_date)
            util.ErrorIfNone(
                date_config.num_workers_evening, errors, _('No number of {shift_type} workers on {work_date}'),
                shift_type=_EVENING_NAME, work_date=work_date)
            util.ErrorIfNone(
                date_config.num_workers_night, errors, _('No number of {shift_type} workers on {work_date}'),
                shift_type=_NIGHT_NAME, work_date=work_date)

        # Check for invalid values
        util.ErrorIfNaNOrNegative(
            date_config.num_workers_day, errors,
            _('"{num_worker}" is invalid number of {shift_type} workers on {work_date}'),
            num_worker=date_config.num_workers_day, shift_type=_DAY_NAME, work_date=work_date)
        util.ErrorIfNaNOrNegative(
            date_config.num_workers_evening, errors,
            _('"{num_worker}" is invalid number of {shift_type} workers on {work_date}'),
            num_worker=date_config.num_workers_evening, shift_type=_EVENING_NAME, work_date=work_date)
        util.ErrorIfNaNOrNegative(
            date_config.num_workers_night, errors,
            _('"{num_worker}" is invalid number of {shift_type} workers on {work_date}'),
            num_worker=date_config.num_workers_night, shift_type=_NIGHT_NAME, work_date=work_date)

    if all_dates:  # Some dates do not have config
        util.AddError(
            errors, _('{date_count} dates do not have date configs: {dates}'),
            date_count=len(all_dates), dates=all_dates)
    if missing_dates:  # Some date configs are out of range
        util.AddError(
            errors, _('{date_count} dates are missing in date configs, {dates}'),
            date_count=len(missing_dates), dates=missing_dates)
    
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
        util.AddError(errors, _('All person names should be unique in {person_sheet} sheet'))
        return errors

    if len(person_configs) != software_config.num_person:
        util.AddError(
            errors,
            _('There should be {num_person} people, but there are rows for {num_configs} people in {person_sheet} sheet'),
            num_person=software_config.num_person, num_configs=len(person_configs))

    # Check for empty config values.
    for pc in person_configs:
        util.ErrorIfNone(
            pc.max_consecutive_workdays, errors, _('No number for max consecutive workdays for {person_name}'),
            person_name=pc.name)
        util.ErrorIfNone(
            pc.max_consecutive_nights, errors, _('No number for max consecutive nights for {person_name}'),
            person_name=pc.name)
        util.ErrorIfNone(
            pc.min_total_workdays, errors, _('No number for min total workdays for {person_name}'),
            person_name=pc.name)
        util.ErrorIfNone(
            pc.max_total_workdays, errors, _('No number for max total workdays for {person_name}'),
            person_name=pc.name)

    # Check for invalid config values 
    for pc in person_configs:
        util.ErrorIfNaNOrNegative(
            pc.max_consecutive_workdays, errors, _('"{number}" is invalid number for {person_name}'),
            number=pc.max_consecutive_workdays, person_name=pc.name)
        util.ErrorIfNaNOrNegative(
            pc.max_consecutive_nights, errors, '"{number}" is invalid number for {person_name}',
            number=pc.max_consecutive_nights, person_name=pc.name)
        util.ErrorIfNaNOrNegative(
            pc.min_total_workdays, errors, '"{number}" is invalid number for {person_name}',
            number=pc.min_total_workdays, person_name=pc.name)
        util.ErrorIfNaNOrNegative(
            pc.max_total_workdays, errors, _('"{number}" is invalid number for {person_name}'),
            number=pc.max_total_workdays, person_name=pc.name)

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
    tt_errors = timetable.ValidateTimetable(
        total_schedule.software_config, total_schedule.date_configs, total_schedule.person_configs,
        total_schedule.assignment_dict, barebone=barebone)
    return tt_errors
    