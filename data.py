
import collections
import datetime
import enum
import json
import build


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
        return [shift.name for shift in cls.WorkShift()]

    def ShortName(self):
        return self.name[0]

    @classmethod
    def FromShortName(cls, code):
        if code is None:
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


# TODO: Break this into two constraint classes : person and date
class Schedule(object):
    def __init__(self, start_date, end_date):        
        self.start_date = start_date  # datetime.date 
        self.end_date = end_date  # datetime.date
        self.constraints = []
        self.date_constraints = []

    def AddConstraint(self, constraint):
        self.constraints.append(constraint)

    def AddDateConstraint(self, date_constraint):
        self.date_constraints.append(date_constraint)

    def GetConstraintByName(self, name):
        for constraint in self.constraints:
            if constraint.name == name:
                return constraint
        return None

    def GetDateConstraint(self, work_date):
        for date_constraint in self.date_constraints:
            if date_constraint.work_date == work_date:
                return date_constraint
        return None
    
    def GetDateConstraints(self):
        return list(self.date_constraints)

    def GetPersonConstraints(self):
        return list(self.person_constraints)

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


# Assignment of shifts
class Assignment(object):

    def __init__(self, assignment_dict, schedule, dates, names):
        self._assignment_dict = assignment_dict  # tuple of (datetime.date, name) -> data.ShiftType
        self._schedule = schedule  # Schedule object
        self._dates = sorted(dates)  # Sorted dates
        self._names = names  # Names, not necessarily sorted

    def GetAssignment(self, work_date, name):
        return self._assignment_dict.get((work_date, name))

    # Get list of (work date, shift) of a person, sorted by date
    def GetAssignmentsByPerson(self, name):
        assignments = []
        for work_date in self._dates: 
            shift = self._assignment_dict.get((work_date, name))
            if shift is not None:
                assignments.append((work_date, shift))
        
        return assignments        

    # Get list of (name, shift) at a specific date, sorted by name
    def GetAssignmentsByDate(self, work_date):
        assignments = []
        for name in self._names:
            shift = self._assignment_dict.get((work_date, name))
            if shift is not None:
                assignments.append((name, shift))
        
        return assignments     

    # Get names of people. Returns copy of the original list
    def GetNames(self):
        return list(self._names)

    # Check if this assignment is valid. Used when an existing solution is modified
    # Check constraint 1-8
    # Returns: list of errors
    def Validate(self):
        pass

    # var_dict: dict of solver variables, after the solver runs
    # schedule: original Schedule object. Required for validation
    @staticmethod
    def FromSolvedVariables(var_dict, schedule):
        pass