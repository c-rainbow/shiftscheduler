"""Test for timetable validation logic"""
import data
import datetime
import unittest

import validation_timetable as vt


_START_DATE = datetime.date(2020, 4, 1)
_END_DATE = datetime.date(2020, 4, 2)

_UNKNOWN_SHIFT = data.ShiftType.UNKNOWN
_DAY_SHIFT = data.ShiftType.DAY
_EVENING_SHIFT = data.ShiftType.EVENING
_NIGHT_SHIFT = data.ShiftType.NIGHT
_OFF_SHIFT = data.ShiftType.OFF

_DAY1 = datetime.date(2020, 4, 1)
_DAY2 = datetime.date(2020, 4, 2)
_DAY3 = datetime.date(2020, 4, 3)
_DAY4 = datetime.date(2020, 4, 4)
_DAY5 = datetime.date(2020, 4, 5)
_DAY6 = datetime.date(2020, 4, 6)


class BaseTestClass(unittest.TestCase):

    def setUp(self):
        self.assignment_dict = {
            (_START_DATE, 'name1'): _DAY_SHIFT, (_END_DATE, 'name1'): _EVENING_SHIFT,
            (_START_DATE, 'name2'): _OFF_SHIFT, (_END_DATE, 'name2'): _NIGHT_SHIFT}
        self.person_configs = [
            data.PersonConfig('name1', 5, 3, 1, 30), data.PersonConfig('name2', 6, 4, 2, 20)]
        self.date_configs = [
            data.DateConfig(_START_DATE, 1, 1, 1), data.DateConfig(_END_DATE, 1, 2, 1)]
        self.all_dates = [_START_DATE, _END_DATE]
        self.errors = []

# Test for validation 1, 2, 3
class BasicValidationTest(BaseTestClass):

    # Test of validation 1
    def testWorkDates(self):
        vt.ValidateWorkDates(self.assignment_dict, _START_DATE, _END_DATE, self.errors)
        self.assertEqual(len(self.errors), 0)
        
    # Test of validation 1 with invalid date format
    def testWorkDatesInvalidDate(self):
        assignment_dict = {('invalid date', 'name1'): _DAY_SHIFT}
        vt.ValidateWorkDates(assignment_dict, _START_DATE, _END_DATE, self.errors)

        self.assertEqual(len(self.errors), 1)
        self.assertEqual(self.errors[0], '"invalid date" is not a valid date')

    # Test of validation 1 with date before start date
    def testWorkDatesBeforeStartDate(self):
        test_date = datetime.date(2020, 3, 31)
        assignment_dict = {(test_date, 'name1'): _DAY_SHIFT}
        vt.ValidateWorkDates(assignment_dict, _START_DATE, _END_DATE, self.errors)

        self.assertEqual(len(self.errors), 1)
        self.assertEqual(self.errors[0], 'Work date 2020-03-31 is before the start date')
 
    # Test of validation 1 with date after end date
    def testWorkDatesAfterEndDate(self):
        test_date = datetime.date(2020, 4, 3)
        assignment_dict = {(test_date, 'name1'): _DAY_SHIFT}
        vt.ValidateWorkDates(assignment_dict, _START_DATE, _END_DATE, self.errors)

        self.assertEqual(len(self.errors), 1)
        self.assertEqual(self.errors[0], 'Work date 2020-04-03 is after the end date')


    # Test of validation 2
    def testPersonNames(self):
        vt.ValidatePersonNames(self.assignment_dict, self.person_configs, self.errors)
        self.assertEqual(len(self.errors), 0)

    # Test of validation 2 when timetable does not have names in person_configs
    def testPersonNamesTimetableHasMissingNames(self):
        assignment_dict = {(_END_DATE, 'name1'): _DAY_SHIFT}
        vt.ValidatePersonNames(assignment_dict, self.person_configs, self.errors)
        self.assertEqual(len(self.errors), 1)
        self.assertEqual(self.errors[0], "Timetable does not have following names: ['name2']")

    # Test of validation 2 when timetable has names not in person_configs
    def testPersonNamesTimetableHasUnexpectedNames(self):
        self.assignment_dict[(_END_DATE, 'name3')] = _OFF_SHIFT
        vt.ValidatePersonNames(self.assignment_dict, self.person_configs, self.errors)
        self.assertEqual(len(self.errors), 1)
        self.assertEqual(self.errors[0], 'Cannot find person config for name3')

    # Test of validation 3, both barebone and not 
    def testShiftCodes(self):
        vt.ValidateShiftCodes(self.assignment_dict, self.errors, barebone=False)
        self.assertEqual(len(self.errors), 0)
        vt.ValidateShiftCodes(self.assignment_dict, self.errors, barebone=True)
        self.assertEqual(len(self.errors), 0)

    # Test of validation 3, when No assignment is found.
    def testShiftCodesEmpty(self):
        assignment_dict = {(_END_DATE, 'name1'): None}
        # Empty assignment is OK for barebone
        vt.ValidateShiftCodes(assignment_dict, self.errors, barebone=True)
        self.assertEqual(len(self.errors), 0)

        vt.ValidateShiftCodes(assignment_dict, self.errors, barebone=False)
        self.assertEqual(len(self.errors), 1)
        self.assertEqual(self.errors[0], 'Shift code is empty for name1 on 2020-04-02')

    def testShiftCodesInvalid(self):
        self.assignment_dict[(_END_DATE, 'name3')]  = _UNKNOWN_SHIFT
        vt.ValidateShiftCodes(self.assignment_dict, self.errors, barebone=True)
        self.assertEqual(len(self.errors), 1)
        self.assertEqual(self.errors[0], 'Invalid shift code for name3 on 2020-04-02')

        errors = []
        assignment_dict = {(_START_DATE, 'name1'): _UNKNOWN_SHIFT}
        vt.ValidateShiftCodes(assignment_dict, errors, barebone=False)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], 'Invalid shift code for name1 on 2020-04-01')


# Test of validation 4
class OverAssignmentValidationTest(BaseTestClass):
    # ValidateOverassignment(assignment_dict, date_configs, errors, barebone=False)
    
    def setUp(self):
        super().setUp()
        self.exact_match_date_configs = [
            data.DateConfig(_START_DATE, 1, 0, 0), data.DateConfig(_END_DATE, 0, 1, 1)
        ]
    
    def testBarebone(self):
        # incomplete assignment does not cause error for barebone
        vt.ValidateOverassignment(
            self.assignment_dict, self.date_configs, self.errors, barebone=True)
        self.assertEqual(len(self.errors), 0)

        # Exact match also does not cause error for barebone
        vt.ValidateOverassignment(
            self.assignment_dict, self.exact_match_date_configs, self.errors, barebone=True)
        self.assertEqual(len(self.errors), 0)

   
    def testNonBarebone(self):
        # Exact match does not cause error for non-barebone
        vt.ValidateOverassignment(
            self.assignment_dict, self.exact_match_date_configs, self.errors, barebone=False)
        self.assertEqual(len(self.errors), 0)

    def testNonBareboneUnderAssignment(self):
        # Under-assignment causes error for non-barebone
        date_configs = [
            data.DateConfig(_START_DATE, 1, 1, 0), data.DateConfig(_END_DATE, 1, 1, 2)
        ]
        vt.ValidateOverassignment(self.assignment_dict, date_configs, self.errors, barebone=False)
        self.assertEqual(len(self.errors), 3)
        self.assertEqual(
            self.errors[0], '0 workers are assigned for EVENING on 2020-04-01, when there should be 1 workers')
        self.assertEqual(
            self.errors[1], '0 workers are assigned for DAY on 2020-04-02, when there should be 1 workers')
        self.assertEqual(
            self.errors[2], '1 workers are assigned for NIGHT on 2020-04-02, when there should be 2 workers')

    def testBareboneOverassignment(self):
        date_configs = [
            data.DateConfig(_START_DATE, 0, 1, 1), data.DateConfig(_END_DATE, 1, 1, 2)
        ]
        vt.ValidateOverassignment(self.assignment_dict, date_configs, self.errors, barebone=True)
        self.assertEqual(len(self.errors), 1)
        self.assertEqual(
            self.errors[0], '1 workers are assigned for DAY on 2020-04-01, when there should be 0 workers')

    def testNonBareboneOverassignment(self):
        date_configs = [
            data.DateConfig(_START_DATE, 0, 0, 0), data.DateConfig(_END_DATE, 0, 0, 1)
        ]
        vt.ValidateOverassignment(self.assignment_dict, date_configs, self.errors, barebone=False)
        self.assertEqual(len(self.errors), 2)
        self.assertEqual(
            self.errors[0], '1 workers are assigned for DAY on 2020-04-01, when there should be 0 workers')
        self.assertEqual(
            self.errors[1], '1 workers are assigned for EVENING on 2020-04-02, when there should be 0 workers')


# Test of validation 5 (constraint 2, 3, 4, 5)
class ConstraintsValidationTest(BaseTestClass):

    # 5-2. No day/evening work after night shift
    def testConstraint2Normal(self):
        # Normal case
        config = self.person_configs[0]
        vt.ValidateConstraint2(config, self.all_dates, self.assignment_dict, self.errors)
        self.assertEqual(len(self.errors), 0)
        
    def testConstraint2DayAfterNight(self):
        # Day after night
        config = self.person_configs[0]
        assignment_dict = {
            (_START_DATE, 'name1'): _NIGHT_SHIFT, (_END_DATE, 'name1'): _DAY_SHIFT}
        vt.ValidateConstraint2(config, self.all_dates, assignment_dict, self.errors)
        self.assertEqual(len(self.errors), 1)
        self.assertEqual(self.errors[0], 'Day/evening work after night shift for name1 on 2020-04-02')

    def testConstraint2EveningAfterNight(self):
        # Evening after night
        config = self.person_configs[0]
        assignment_dict = {
            (_START_DATE, 'name1'): _NIGHT_SHIFT, (_END_DATE, 'name1'): _EVENING_SHIFT}
        vt.ValidateConstraint2(config, self.all_dates, assignment_dict, self.errors)
        self.assertEqual(len(self.errors), 1)
        self.assertEqual(self.errors[0], 'Day/evening work after night shift for name1 on 2020-04-02')

    # 5-3. No more than n consecutive workdays
    def testConstraint3Normal(self):
        config = self.person_configs[0]
        vt.ValidateConstraint3(config, self.all_dates, self.assignment_dict, self.errors)
        self.assertEqual(len(self.errors), 0)

    def testConstraint3Exact(self):
        # Working exactly n days
        config = data.PersonConfig('name4', 3, 2, 5, 5)
        assignment_dict = {
            (_DAY1, 'name4'): _OFF_SHIFT, (_DAY2, 'name4'): _EVENING_SHIFT,
            (_DAY3, 'name4'): _EVENING_SHIFT, (_DAY4, 'name4'): _DAY_SHIFT}
        all_dates = [_DAY1, _DAY2, _DAY3, _DAY4]
        vt.ValidateConstraint3(config, all_dates, assignment_dict, self.errors)
        self.assertEqual(len(self.errors), 0)

    def testConstraint3Error(self):
        # Working more than n days
        config = data.PersonConfig('name4', 3, 2, 5, 5)
        assignment_dict = {
            (_DAY1, 'name4'): _DAY_SHIFT, (_DAY2, 'name4'): _EVENING_SHIFT,
            (_DAY3, 'name4'): _EVENING_SHIFT, (_DAY4, 'name4'): _DAY_SHIFT}
        all_dates = [_DAY1, _DAY2, _DAY3, _DAY4]
        vt.ValidateConstraint3(config, all_dates, assignment_dict, self.errors)
        self.assertEqual(len(self.errors), 1)
        self.assertEqual(
            self.errors[0],
            'Worker name4 should work no more than 3 consecutive days, but worked for 4 days from 2020-04-01')

        # Working 4 consecutive days in the middle
        assignment_dict = {
            (_DAY1, 'name4'): _OFF_SHIFT, (_DAY2, 'name4'): _EVENING_SHIFT,
            (_DAY3, 'name4'): _EVENING_SHIFT, (_DAY4, 'name4'): _DAY_SHIFT,
            (_DAY5, 'name4'): _DAY_SHIFT, (_DAY6, 'name4'): _OFF_SHIFT}
        all_dates = [_DAY1, _DAY2, _DAY3, _DAY4, _DAY5, _DAY6]
        errors = []
        vt.ValidateConstraint3(config, all_dates, assignment_dict, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[0],
            'Worker name4 should work no more than 3 consecutive days, but worked for 4 days from 2020-04-02')

    def testConstraint3OffInTheMiddle(self):
        # Constraint3. Work not for more than n consecutive days, because OFF in the middle
        config = data.PersonConfig('name4', 2, 2, 5, 5)
        assignment_dict = {  # Person works on 1st & 2nd day, takes a break on 3rd day and works again
            (_DAY1, 'name4'): _DAY_SHIFT, (_DAY2, 'name4'): _EVENING_SHIFT,
            (_DAY3, 'name4'): _OFF_SHIFT, (_DAY4, 'name4'): _DAY_SHIFT}
        all_dates = [_DAY1, _DAY2, _DAY3, _DAY4]
        vt.ValidateConstraint3(config, all_dates, assignment_dict, self.errors)
        self.assertEqual(len(self.errors), 0)

    def testConstraint3MultipleViolations(self):
        # Constraint3. Multiple errors
        config = data.PersonConfig('name4', 1, 1, 5, 5)  # Can work max 1 day at a time
        assignment_dict = {  # 2 days from 04-01, 3 days from 04-04
            (_DAY1, 'name4'): _DAY_SHIFT, (_DAY2, 'name4'): _NIGHT_SHIFT,
            (_DAY3, 'name4'): _OFF_SHIFT, (_DAY4, 'name4'): _DAY_SHIFT,
            (_DAY5, 'name4'): _EVENING_SHIFT, (_DAY6, 'name4'): _EVENING_SHIFT}
        all_dates = [_DAY1, _DAY2, _DAY3, _DAY4, _DAY5, _DAY6]
        vt.ValidateConstraint3(config, all_dates, assignment_dict, self.errors)
        self.assertEqual(len(self.errors), 2)

        self.assertEqual(
            self.errors[0],
            'Worker name4 should work no more than 1 consecutive days, but worked for 2 days from 2020-04-01')
        self.assertEqual(
            self.errors[1],
            'Worker name4 should work no more than 1 consecutive days, but worked for 3 days from 2020-04-04')

    # 5-4. No more than n consecutive nights
    def testConstraint4Normal(self):
        config = self.person_configs[0]
        vt.ValidateConstraint4(config, self.all_dates, self.assignment_dict, self.errors)
        self.assertEqual(len(self.errors), 0)

    def testConstraint4Exact(self):
        # Working exactly n nights
        config = data.PersonConfig('name4', 3, 2, 5, 5)
        assignment_dict = {
            (_DAY1, 'name4'): _DAY_SHIFT, (_DAY2, 'name4'): _NIGHT_SHIFT,
            (_DAY3, 'name4'): _NIGHT_SHIFT, (_DAY4, 'name4'): _OFF_SHIFT}
        all_dates = [_DAY1, _DAY2, _DAY3, _DAY4]
        vt.ValidateConstraint4(config, all_dates, assignment_dict, self.errors)
        self.assertEqual(len(self.errors), 0)

    def testConstraint4Error(self):
        # Working more than n nights
        config = data.PersonConfig('name4', 3, 2, 5, 5)
        assignment_dict = {
            (_DAY1, 'name4'): _NIGHT_SHIFT, (_DAY2, 'name4'): _NIGHT_SHIFT,
            (_DAY3, 'name4'): _NIGHT_SHIFT, (_DAY4, 'name4'): _NIGHT_SHIFT}
        all_dates = [_DAY1, _DAY2, _DAY3, _DAY4]
        vt.ValidateConstraint4(config, all_dates, assignment_dict, self.errors)
        self.assertEqual(len(self.errors), 1)
        self.assertEqual(
            self.errors[0],
            'Worker name4 should work no more than 2 consecutive nights, but worked for 4 nights from 2020-04-01')

        # Working 3 consecutive nights in the middle
        assignment_dict = {
            (_DAY1, 'name4'): _DAY_SHIFT, (_DAY2, 'name4'): _DAY_SHIFT,
            (_DAY3, 'name4'): _NIGHT_SHIFT, (_DAY4, 'name4'): _NIGHT_SHIFT,
            (_DAY5, 'name4'): _NIGHT_SHIFT, (_DAY6, 'name4'): _OFF_SHIFT}
        all_dates = [_DAY1, _DAY2, _DAY3, _DAY4, _DAY5, _DAY6]
        errors = []
        vt.ValidateConstraint4(config, all_dates, assignment_dict, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[0],
            'Worker name4 should work no more than 2 consecutive nights, but worked for 3 nights from 2020-04-03')

# Test of validation 6
class MinRequiredWorkersTest(BaseTestClass):
    pass


# Test of validation 7
class MinTotalWorkSlotsTest(BaseTestClass):
    pass


# Test of validation 8
class MaxTotalWorkSlotsTest(BaseTestClass):
    pass


if __name__ == '__main__':
    unittest.main()