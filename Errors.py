"""
Contains custom error types that could occur in the calculator
When the error is in the expression, raise the one of these exceptions
This means it can be distinguished from errors in code, caught and presented as an error message without crashing
Make error messages as clear as possible so the user can understand them
"""

class CalcError(Exception):
    """General errors in the calculator"""
    # inherits all of 'Exception's methods and attributes
    pass

class CalcOperationError(CalcError):
    """
    Errors in the calculator due to specific requirements of operations
    eg: factorial is undefined for negatives or decimals

    :param msg (str): The error message - as clear as possible so someone with no mathematical or programming knowledge can understand
    :param op_name (str): The name of the operation that errored
    :param operands (iterable): The operands the operation was called with
    """
    # inherits all of 'CalcError' and therefore 'Exception's method and attributes but overrides the init method
    def __init__(self, msg, op_name, operands):
        # converts all operands to strings and separates them by commas in the message
        super().__init__("While performing {} with {}: {}".format(op_name, ", ".join([str(operand) for operand in operands]), msg))
