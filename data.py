
import datetime
import enum
import json


# JSON keys
KEY_START_DATE = 'start_date'
KEY_END_DATE = 'end_date'
KEY_CONSTRAINTS = 'constraints'

KEY_NAME = 'name'
KEY_MAX_CONSECUTIVE_WORKDAYS = 'max_consecutive_workdays'
KEY_MAX_CONSECUTIVE_NIGHTS = 'max_consecutive_nights'
KEY_MIN_TOTAL_WORKDAYS = 'min_total_workdays'
KEY_MAX_TOTAL_WORKDAYS = 'max_total_workdays'
KEY_FIXED_SHIFTS = 'fixed_shifts'
KEY_OFF_SHIFTS = 'off_shifts'


class ShiftType(enum.Enum):
    DAY = 1
    EVENING = 2
    NIGHT = 6

    @classmethod
    def Items(cls):
        return cls.__members__.items()

    @classmethod
    def Names(cls):
        items = cls.Items()
        return [name for name, _ in items]


class Shift(object):
    def __init__(self, date, shift_type):
        self.date = date  # datetime.date
        self.shift_type = shift_type  # ShiftType

    # Convert JSON stringified expression of shift to a Shift object
    # Input is a string of format "2020-03-26-NIGHT", "2052-12-04-DAY", etc.
    @staticmethod
    def FromJSON(json_str):
        date = datetime.date.fromisoformat(json_str[:10])
        shift_type = ShiftType[json_str[11:]]
        return Shift(date, shift_type)    


class Constraint(object):
    def __init__(self, name):
        self.name = name
        self.max_consecutive_workdays = 0
        self.max_consecutive_nights = 0
        self.min_total_workdays = 0
        self.max_total_workdays = 0
        self.fixed_shifts = []  # list of Shift
        self.off_shifts = []  # list of Shift

    # Convert from JSON-decoded dict to Constraint object
    @staticmethod
    def FromJSONDict(json_dict):
        constraint = Constraint(json_dict[KEY_NAME])

        constraint.max_consecutive_workdays = json_dict[KEY_MAX_CONSECUTIVE_WORKDAYS]
        constraint.max_consecutive_nights = json_dict[KEY_MAX_CONSECUTIVE_NIGHTS]
        constraint.min_total_workdays = json_dict[KEY_MIN_TOTAL_WORKDAYS]
        constraint.max_total_workdays = json_dict[KEY_MAX_TOTAL_WORKDAYS]

        for fixed_shift_str in json_dict[KEY_FIXED_SHIFTS]:
            fixed_shift = Shift.FromJSON(fixed_shift_str)
            constraint.fixed_shifts.append(fixed_shift)

        for off_shift_str in json_dict[KEY_OFF_SHIFTS]:
            off_shift = Shift.FromJSON(off_shift_str)
            constraint.off_shifts.append(off_shift)

        return constraint


class Schedule(object):
    def __init__(self, start_date, end_date):        
        self.start_date = start_date  # datetime.date 
        self.end_date = end_date  # datetime.date
        self.constraints = []

    def AddConstraint(self, constraint):
        self.constraints.append(constraint)

    # Convert JSON string to Schedule object
    @staticmethod
    def FromJSON(json_str):
        decoded = json.loads(json_str)

        # Dates are of ISO format "2019-01-02"
        start_date = datetime.date.fromisoformat(decoded[KEY_START_DATE])
        end_date = datetime.date.fromisoformat(decoded[KEY_END_DATE])
        sch = Schedule(start_date, end_date)

        # Add constraints
        for constraint_dict in decoded[KEY_CONSTRAINTS]:
            constraint = Constraint.FromJSONDict(constraint_dict)
            sch.constraints.append(constraint)

        return sch
