import datetime


# Generate all dates in between [start_date, end_date], both inclusive.
def GenerateAllDates(start_date, end_date):
    output = []
    for n in range((end_date - start_date).days + 1):
        output.append((start_date + datetime.timedelta(days=n)))
    return output


# Generate all dates in string form of 2020-05-31
def GenerateAllDateStrs(start_date, end_date):
    output = GenerateAllDates(start_date, end_date)
    return [str(o) for o in output]