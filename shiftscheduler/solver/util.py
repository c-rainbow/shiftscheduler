
import functools


# Variable name from nurse name, work date, and shift type name
# work_date can be either datetime.date or str
# shift_type_str is str
def GetVariableName(name, work_date, shift_type_str):
    return 'x_%s_%s_%s' % (name, str(work_date), shift_type_str)


# Sum of solver "variables". Works for both MIP and CP solvers
# TODO: Check if this can be replaced with Python's built-in sum()
def VariableSum(variables):
    return functools.reduce(lambda x, y: x + y, variables)