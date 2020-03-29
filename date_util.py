import datetime


# Generate all dates in between [start_date, end_date], both inclusive.
def GenerateAllDates(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield start_date + datetime.timedelta(n)
