import datetime


# Dates in Excel can be str, datetime.date, or datetime.datetime in Python.
# Convert them to datetime.date
def CellToDate(cell):
    value = cell.value
    value_type = type(value)
    if value_type is str:
        return datetime.date.fromisoformat(value)
    elif value_type is datetime.datetime:
        return value.date()
    elif value_type is datetime.date:
        return value
    raise TypeError('%s is not a valid type for date' % value_type)


