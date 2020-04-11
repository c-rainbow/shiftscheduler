
import collections
import enum


SoftwareConfig = collections.namedtuple(
    'SoftwareConfig', ['start_date', 'end_date', 'num_person'])


PersonConfig = collections.namedtuple(
    'PersonConfig', [
        'name',  # Person's name. Must be unique
        'max_consecutive_workdays',
        'max_consecutive_nights',
        'min_total_workdays',
        'max_total_workdays',
    ]
)


DateConfig = collections.namedtuple(
    'DateConfig', ['work_date', 'num_workers_day', 'num_workers_evening', 'num_workers_night'])


# All data needed to run the solver, or write to Excel file
# TODO: Find a better name for the data type name
TotalSchedule = collections.namedtuple(
    'TotalSchedule', ['software_config', 'person_configs', 'date_configs', 'assignment_dict'])


class ShiftType(enum.Enum):
    UNKNOWN = 0  # Used for conversion from unrecognized short name
    DAY = 1
    EVENING = 2
    NIGHT = 3
    OFF = 4

    @classmethod
    def WorkShiftTypes(cls):
        return (cls.DAY, cls.EVENING, cls.NIGHT)
    
    # Name of all work shifts. OFF is not included
    @classmethod
    def WorkShiftNames(cls):
        return [shift.name for shift in cls.WorkShiftTypes()]

    def ShortName(self):
        return self.name[0]

    @classmethod
    def FromShortName(cls, code):
        if code is None or code == '':
            return None
        elif code in ('D', 'd'):
            return cls.DAY
        elif code in ('E', 'e'):
            return cls.EVENING
        elif code in ('N', 'n'):
            return cls.NIGHT
        elif code in ('O', 'o'):
            return cls.OFF
        return cls.UNKNOWN
