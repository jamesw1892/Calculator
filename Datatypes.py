"""
Contains datatypes the calculator needs to function as part of its internal operation
as well as the list of all valid tokens and the regex pattern to tokenise expressions
"""

from re import VERBOSE, compile as compile_regex
from collections import deque
from Operations import op_pos, op_add, op_neg, op_sub, op_mul, op_true_div, op_floor_div, op_mod, op_exp, op_root, op_permutations, op_combinations, op_factorial, func_ln, func_log, func_abs, func_lcm, func_hcf, func_rand, func_quadp, func_quadn, func_sin, func_cos, func_tan, func_arsin, func_arcos, func_artan, func_sinh, func_cosh, func_tanh, func_arsinh, func_arcosh, func_artanh
from decimal import Decimal
from Errors import CalcError

class Stack:
    """Represents a stack - a LIFO data structure similar to a list/array with only access to the top"""

    def __init__(self):
        # private attribute denoted by the double underscore prefix
        self.__stack = deque()

    def push(self, item):
        """Add 'item' to the top of the stack"""
        self.__stack.append(item)

    def pop(self):
        """Remove and return the item on the top of the stack. Return 'None' if the stack is empty"""
        return self.__stack.pop() if self else None

    def peek(self):
        """Return the item on the top of the stack without removing it from the stack. Return 'None' if the stack is empty"""
        return self.__stack[-1] if self else None

    def __bool__(self):
        return bool(self.__stack)

    def __len__(self):
        return len(self.__stack)

    def __repr__(self):
        return "Stack({})".format(str(list(self.__stack)).replace("[", "").replace("]", ""))

    def __iter__(self):

        # need to copy it because the variable is a pointer to where the actual stack is so
        # creating a new variable will mean they both reference the same thing whereas now
        # they reference identical but different stacks which is what I want because I am removing
        # items from the copy which I don't want to happen to the real stack
        temp = self.__stack.copy()

        while temp:
            yield temp.pop()

    def __contains__(self, item):

        for i in self:
            if i == item:
                return True

        return False

class Queue:
    """Represents a queue - a FIFO data structure similar to a list/array with only access to the head and tail"""

    def __init__(self):
        # private attribute denoted by the double underscore prefix
        self.__queue = deque()

    def enqueue(self, item):
        """Add 'item' to the tail of the queue"""
        self.__queue.appendleft(item)

    def dequeue(self):
        """Remove and return the item at the head of the queue. Return 'None' if the queue is empty"""
        return self.__queue.pop() if self else None

    def peek(self):
        """Return the item at the head of the queue without removing it from the queue. Return 'None' if the queue is empty"""
        return self.__queue[-1] if self else None

    def __bool__(self):
        return bool(self.__queue)

    def __len__(self):
        return len(self.__queue)

    def __repr__(self):
        return "Queue({})".format(str([item for item in self]).replace("[", "").replace("]", ""))

    def __iter__(self):

        # need to copy it because the variable is a pointer to where the actual queue is so
        # creating a new variable will mean they both reference the same thing whereas now
        # they reference identical but different queues which is what I want because I am removing
        # items from the copy which I don't want to happen to the real queue
        temp = self.__queue.copy()

        while temp:
            yield temp.pop()

    def __contains__(self, item):

        for i in self:
            if i == item:
                return True

        return False

class Operator:
    """
    Represents an operator and stores information about it

    :param name (str): The name of the operator
    :param func (identifier): The identifier of the function to execute the operation
    :param precedence (int/float): The precedence of the operation compared to other operations. Lower numbers means executed first
    :param is_left_associative (bool): Whether or not the operator is left (-to-right) associative (right (-to-left) associative otherwise)
    :param is_unary (bool): Whether or not the operator is a unary operator (takes only 1 operand) or otherwise it is binary (takes 2 operands)
    """

    def __init__(self, name, func, precedence, is_left_associative, is_unary):
        self.name = name
        self.func = func
        self.precedence = precedence
        self.is_left_associative = is_left_associative
        self.is_unary = is_unary

    def execute(self, operands):
        """
        Return the answer when the operator is executed with its operands

        :param operands (list): The operands to execute the operator with
        :return answer (int/float): The answer when the operator is executed with the operands
        """

        # the star splits the 'operands' list out into individual parameters
        return self.func(*operands)

    def __repr__(self):
        return "UnaryOperator({})".format(self.name) if self.is_unary else "BinaryOperator({})".format(self.name)

class BinaryOperator(Operator):
    """
    Represents a binary operator and stores information about it

    :param name (str): The name of the operator
    :param func (identifier): The identifier of the function to execute the operation
    :param precedence (int/float): The precedence of the operation compared to other operations. Lower numbers means executed first
    :param is_left_associative (bool): Whether or not the operator is left (-to-right) associative (alternative is right (-to-left) associative)
    """

    def __init__(self, name, func, precedence, is_left_associative):
        super().__init__(name, func, precedence, is_left_associative, False)

class UnaryOperator(Operator):
    """
    Represents a unary operator and stores information about it

    :param name (str): The name of the operator
    :param func (identifier): The identifier of the function to execute the operation
    :param is_left_associative (bool): Whether or not the operand is on the left side of the operator (alternative is on the right)
    """

    def __init__(self, name, func, is_left_associative):
        super().__init__(name, func, 1, is_left_associative, True)

class BothOperators:
    """
    Represents a symbol that could represent a binary operator or a unary operator.

    :param unary (UnaryOperator): The unary operator that it could be
    :param binary (BinaryOperator): The binary operator that it could be
    """

    def __init__(self, unary, binary):
        assert isinstance(unary, Operator) and unary.is_unary, "Must be an instance of 'Operator' and be unary"
        assert isinstance(binary, Operator) and not binary.is_unary, "must be an instance of 'Operator' and be binary"
        self.unary = unary
        self.binary = binary

    def __repr__(self):
        return "BothOperators({}, {})".format(self.unary, self.binary)

class FunctionType:
    """
    Represents a type of function and stores information about it

    :param name (str): The name of the type of function
    :param func (identifier): The identifier of the function to execute the operation
    :param num_operands (int): The number of operands the function takes
    """

    def __init__(self, name, func, num_operands):
        self.__name = name
        self.__func = func
        self.__num_operands = num_operands

    def create(self, calc):
        """
        Return a new object which has the same properties as this object
        but is unique for all instances of the function in the expression

        :param calc (function): The calculate function from the main calculator
        :return (object): An instance of the 'FunctionInstance' class
        """

        return FunctionInstance(self.__name, self.__func, self.__num_operands, calc)

    def __repr__(self):
        return "FunctionType({})".format(self.__name)

class FunctionInstance:
    """
    Represents a function instance and stores information about it

    :param name (str): The name of the type of function
    :param func (function): The function to execute the operation
    :param num_operands (int): The number of operands the function takes
    :param calc (function): The calculate function from the main calculator
    """

    def __init__(self, name, func, num_operands, calc):
        self.__name = name
        self.__func = func
        self.__num_operands = num_operands
        self.__calc = calc
        self.__operands = []

    def add_operand(self, operand):
        """
        Execute the operand with the calculator to simplify it and then add it to the stored operands

        :param operand (num): The operand to add
        """

        self.__operands.append(Num(self.__calc(operand)))

    def execute(self):
        """
        Recursively execute all operands using the calculator and then
        return the answer when the function is executed with its operands

        :return (Num): The answer to the function when executed on its operands
        """

        if len(self.__operands) != self.__num_operands:
            raise CalcError("{} operands required in {} function call".format(self.__num_operands, self.__name))

        # execute the function with its operands and return it
        # the star splits the list out into individual arguments
        return Num(self.__func(*self.__operands))

    def __repr__(self):
        return "{}({})".format(self.__name, ", ".join([str(operand) for operand in self.__operands]))

class Num(Decimal):
    """Represents a number"""
    # inherits all methods from Decimal but overrides representation method
    def __repr__(self):
        return "Num({})".format(self)

class Bracket:
    """
    Represents a bracket

    :param is_open (bool): Whether or not the bracket is an open bracket (alternative is a close bracket)
    """

    def __init__(self, is_open):
        self.is_open = is_open

    def __repr__(self):
        return "OpenBracket" if self.is_open else "CloseBracket"

class OpenBracket(Bracket):
    """Represents an open bracket"""

    def __init__(self):
        super().__init__(True)

class CloseBracket(Bracket):
    """Represents a close bracket"""

    def __init__(self):
        super().__init__(False)

# create the tokens that can be used in the calculator with the classes above and the operations in 'Operations.py'
# the key is the symbol that will be in expressions and the value is an instance of one of the following classes:
# UnaryOperator, BinaryOperator, Operator, or BothOperators
valid_tokens = {
    "+": BothOperators(UnaryOperator("Positive (+)", op_pos, False), BinaryOperator("Addition (+)", op_add, 4, True)),
    "-": BothOperators(UnaryOperator("Negative (-)", op_neg, False), BinaryOperator("Subtraction (-)", op_sub, 4, True)),
    "*": BinaryOperator("Multiplication (*)", op_mul, 3, True),
    "/": BinaryOperator("Division (/)", op_true_div, 3, True),
    "\\": BinaryOperator("Floor division (\\)", op_floor_div, 3, True),
    "%": BinaryOperator("Mod (%)", op_mod, 3, True),
    "^": BinaryOperator("Exponentiation (^)", op_exp, 2, False),
    "¬": BinaryOperator("Root (¬)", op_root, 2, False),
    "p": BinaryOperator("Permutations (P)", op_permutations, 0, True),
    "c": BinaryOperator("Combinations (C)", op_combinations, 0, True),
    "!": UnaryOperator("Factorial (!)", op_factorial, True),
    "ln": FunctionType("Natural log (ln)", func_ln, 1),
    "log": FunctionType("Logarithm (log)", func_log, 2),
    "abs": FunctionType("Absolute value (abs)", func_abs, 1),
    "lcm": FunctionType("Lowest common multiple", func_lcm, 2),
    "hcf": FunctionType("Highest common factor", func_hcf, 2),
    "rand": FunctionType("Random number generator", func_rand, 2),
    "quadp": FunctionType("Quadratic equation solver (postive square root)", func_quadp, 3),
    "quadn": FunctionType("Quadratic equation solver (negative square root)", func_quadn, 3),
    "sin": FunctionType("Sin (sin)", func_sin, 1),
    "cos": FunctionType("Cosine (cos)", func_cos, 1),
    "tan": FunctionType("Tangent (tan)", func_tan, 1),
    "arsin": FunctionType("Inverse sine (arsin)", func_arsin, 1),
    "arcos": FunctionType("Inverse cosine (arcos)", func_arcos, 1),
    "artan": FunctionType("Inverse tangent (artan)", func_artan, 1),
    "sinh": FunctionType("Hyperbolic sin (sinh)", func_sinh, 1),
    "cosh": FunctionType("Hyperbolic cosine (cosh)", func_cosh, 1),
    "tanh": FunctionType("Hyperbolic tangent (tanh)", func_tanh, 1),
    "arsinh": FunctionType("Inverse hyperbolic sine (arsinh)", func_arsinh, 1),
    "arcosh": FunctionType("Inverse hyperbolic cosine (arcosh)", func_arcosh, 1),
    "artanh": FunctionType("Inverse hyperbolic tangent (artanh)", func_artanh, 1),
    "pi": Num("3.14159265358979323846264338327950288"),
    "tau": Num("6.28318530717958647692528676655900576"),
    "e": Num("2.71828182845904523536028747135266249"),
    "g": Num("9.80665"),
    "phi": Num("1.61803398874989484820458683436563811")
}

# compile the regex pattern that will be used to check for tokens
regex = compile_regex(r"""
    (?P<whitespace>\s+)
    |(?P<number>(\d*\.)?\d+(~[+-]?\d+)?)
    |(?P<word>[a-z]+)
    |(?P<bracket>[()])
    |(?P<comma>,)
    |(?P<other>.)
""", VERBOSE)
