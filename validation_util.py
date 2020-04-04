"""Utility functions for validation."""
import datetime

def ToInt(cell_value):
    try:
        s = int(cell_value)
    except ValueError:
        s = None
    return s


def ErrorIfNone(value, errors, message, *args):
    if value is None:
        errors.append(message % args)
        return True
    return False


# Error if not a number or negative.
# Not an error if None.
# Returns True if error is found, False otherwise
def ErrorIfNaNOrNegative(value, errors, message, *args):
    if value is None:
        return False

    int_value = ToInt(value)
    if int_value is None or int_value < 0:
        errors.append(message % args)
        return True
    return False



# Error if 'value' is less than 'to_compare'
# Not an error if at least one of them are None
def ErrorIfLess(value, to_compare, errors, message, *args):
    if value is None or to_compare is None:
        return False

    if value < to_compare:
        errors.append(message % args)
        return True
    return False


# Error if 'value' is greater than 'to_compare'
# Not an error if at least one of them are None
def ErrorIfGreater(value, to_compare, errors, message, *args):
    if value is None or to_compare is None:
        return False

    if value > to_compare:
        errors.append(message % args)
        return True
    return False


# Error if 'value' is not equal to 'to_compare'
# Not an error if at least one of them are None
def ErrorIfNotEqual(value, to_compare, errors, message, *args):
    if value is None or to_compare is None:
        return False
        
    if value != to_compare:
        errors.append(message % args)
        return True
    return False



def SanitizeDate(obj):
    obj_type = type(obj)
    if obj_type is str:
        return datetime.date.fromisoformat(obj)
    elif obj_type is datetime.datetime:
        return obj.date()
    elif obj_type is datetime.date:
        return obj
    raise TypeError('%s is not a valid type for date' % obj_type)


def GetWorkerCount(assignment_dict, expected_date, expected_shift_type):
    count = 0
    for (work_date, name), shift_type in assignment_dict.items():
        if work_date == expected_date and shift_type == expected_shift_type:
            count += 1

    return count