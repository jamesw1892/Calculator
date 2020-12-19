"""
The calculator's core functionality
Use the 'calculate' function to calculate the answer to an expression
"""

from Datatypes import Stack, Queue, Operator, BothOperators, Num, OpenBracket, CloseBracket, valid_tokens, regex, FunctionType, FunctionInstance
from Errors import CalcError
from decimal import DecimalException, Overflow, InvalidOperation

# instructions read from the text file for other files to import
with open("Instructions.txt", "r") as f:
    instructions = "".join(f.readlines())

def find_matched_key(match):
    """Return the key which was matched"""

    # exactly 1 value in 'match' will not be 'None'
    # so this will always return exactly once
    for key in match:
        if match[key] is not None:
            return key

def should_be_unary(prev_token):
    """Return whether or not the current token should be a unary operator depending on the previous token"""

    # if it is the first token in the expression, it should
    if prev_token is None:
        return True

    # if it's an open bracket, it should
    if isinstance(prev_token, OpenBracket):
        return True

    # if it's an operator, it should if it's binary or (unary and right associative)
    if isinstance(prev_token, Operator):

        # if it is binary, it should
        if not prev_token.is_unary:
            return True

        # if it is unary and right associative, it should
        if not prev_token.is_left_associative:
            return True

    # if none of the others are true, it shouldn't
    return False

def identify(name, value, prev_token):
    """Return an instance of a class to identify the token"""

    # if it's a number, convert my standard form notation into python's and make it an instance of 'Num'
    if name == "number":
        return Num(value.replace("~", "e"))

    # if it's a bracket, make it an instance of one of my bracket classes
    if value == "(":
        return OpenBracket()
    if value == ")":
        return CloseBracket()

    # if it's a comma, give an error message as commas can only be inside functions
    if value == ",":
        raise CalcError("Commas only allowed inside functions")

    # if it's in 'valid_tokens', it's a valid operator so:
    if value in valid_tokens:
        token = valid_tokens[value]

        # if it could be unary or binary, use the helper function to decide which and return that
        if isinstance(token, BothOperators):
            return token.unary if should_be_unary(prev_token) else token.binary

        # if it's a function, create a unique instance and return that
        if isinstance(token, FunctionType):
            return token.create(calculate)

        # otherwise just return it
        return token

    # otherwise, it is an invalid token so error
    raise CalcError("Invalid token: '{}'".format(value))

def identify_operand(operand, function):
    """Validate and format the operand of a function and store it in the function"""

    #remove whitespace at the start and end of the operand
    operand = operand.strip()

    # remove the '(' or ',' at the start of the operand or error if neither
    if operand[0] == "(" or operand[0] == ",":
        operand = operand[1:]
    else:
        raise CalcError("Functions must be immediately followed by brackets")

    # remove the ',' or ')' at the end of the operand or error if neither
    if operand[-1] == ")" or operand[-1] == ",":
        operand = operand[:-1]
    else:
        raise CalcError("Functions must end with a close bracket")

    # add the operand to the function object
    function.add_operand(operand)

def tokenise(expr):
    """Split the expression up into tokens and make them instances of classes to identify them"""

    # remove whitespace at the start or end of the expression and make lower case
    expr = expr.strip().lower()

    # initialise variables
    tokens = []
    pos = 0
    in_func = False

    while pos < len(expr):

        # find a regex match with the expression 'pos' characters in
        match = regex.match(expr, pos)

        # adjust 'pos' to be the end of the last match
        # so the next iteration doesn't match the same characters
        pos = match.end()

        # convert to a dictionary with the named patterns as keys
        match = match.groupdict()

        # find which key has been matched
        key = find_matched_key(match)

        # ignore whitespace
        if key != "whitespace":

            # if not in a function, identify the token and add it to the list of tokens
            if not in_func:

                # the previous token is the last token in the list 'tokens[-1]' but if the list is empty, it is 'None'
                token = identify(key, match[key], tokens[-1] if tokens else None)
                tokens.append(token)

                # if the token is a function, initialise the function variables
                if isinstance(token, FunctionInstance):
                    in_func = True
                    bracket_depth = 0
                    operand_start_pos = pos

            # if in a function, ignore everything except brackets and commas
            # to get the operands as strings and add them to the function object
            else:
                if key == "bracket":

                    # if it's an open bracket, increase the bracket depth
                    if match[key] == "(":
                        bracket_depth += 1

                    # if it's a close bracket, decrease the bracket depth
                    else:
                        bracket_depth -= 1

                        # if the bracket depth is now 0, add the last operand and execute the function
                        if bracket_depth == 0:
                            in_func = False
                            identify_operand(expr[operand_start_pos:pos], tokens[-1])
                            tokens[-1] = tokens[-1].execute()

                # if it's a comma, add the operand to the function
                # and update the start pos for the next operand
                elif key == "comma" and bracket_depth == 1:
                    identify_operand(expr[operand_start_pos:pos], tokens[-1])
                    operand_start_pos = pos - 1

                # add omitted closing brackets around functions
                elif pos >= len(expr):
                    expr += ")"

    return tokens

def should_be_executed_first(top_of_stack_token, current_token):
    """Return whether or not the token at the top of the stack should be executed before the current token"""

    # the token at the top of the stack should be executed before the current token if 1 and 2:
    #   1) the token at the top of the stack is an operator
    #   2) if a or b:
    #       a) the operator at the top of the stack has better precedence than the current operator
    #       b) i and ii:
    #           i)  they have equal precedences
    #           ii) the operator at the top of the stack is left associative

    #      ------------------ 1 ------------------- and -------------------------------------------------------------------------------------- 2 ---------------------------------------------------------------------------
    #                                                    --------------------------- a -------------------------- or ---------------------------------------------------- b -----------------------------------------------
    #                                                                                                                 --------------------------- i --------------------------- and ------------------ ii ----------------
    return isinstance(top_of_stack_token, Operator) and (top_of_stack_token.precedence < current_token.precedence or (top_of_stack_token.precedence == current_token.precedence and top_of_stack_token.is_left_associative))

def convert(tokens):
    """Convert the tokens from infix notation to postfix notation (AKA reverse polish notation) by the shunting yard algorithm"""

    output_queue = Queue()      # we only ever add numbers or operators to the output queue
    operator_stack = Stack()    # we only ever add operators and open brackets to the operator stack

    for token in tokens:

        # add numbers to the output queue
        if isinstance(token, Num):
            output_queue.enqueue(token)

        # if it's an operator, add any operators on the stack that should be executed before
        # it (using 'should_be_executed_first') to the output queue and then add it to the stack
        elif isinstance(token, Operator):
            while should_be_executed_first(operator_stack.peek(), token):
                output_queue.enqueue(operator_stack.pop())
            operator_stack.push(token)

        # add open brackets to the operator stack
        elif isinstance(token, OpenBracket):
            operator_stack.push(token)

        # otherwise, it must be a close bracket so add everything from the operator stack to the output queue
        # until there is an open bracket, then remove this too but don't add it to the output queue
        else:
            while not isinstance(operator_stack.peek(), OpenBracket) and operator_stack.peek() is not None:
                output_queue.enqueue(operator_stack.pop())

            # if there is nothing left in the stack but we haven't
            # found an open bracket, there are too few open brackets
            if operator_stack.peek() is None:
                raise CalcError("Too many close brackets or not enough open brackets")

            # remove the open bracket from the stack and discard
            else:
                operator_stack.pop()

    # move everything on the stack to the output queue
    while operator_stack:
        token = operator_stack.pop()

        # if an open bracket didn't have a matching closing bracket,
        # it could appear here but we don't want it so ignore it
        if not isinstance(token, OpenBracket):
            output_queue.enqueue(token)

    return output_queue

def execute(queue):
    """
    Execute the tokens to get a final answer
    As in postfix notation, the first operator in the queue is the first operator to be executed
    so execute this with the operands repeatedly until all of them have been executed to get a final answer
    """

    stack = Stack()

    for token in queue:

        # if it's a number, push it to the stack
        if isinstance(token, Num):
            stack.push(token)

        # otherwise it must be an operator so pop its operands from the stack, execute it with them and add push the result to the stack
        else:

            # at least 1 operand is needed for all operators
            operands = [stack.pop()]

            # binary operators need another
            if not token.is_unary:
                operands.append(stack.pop())

            # the stack returns None if empty so if 'None' is in there, there are too few operands
            if None in operands:
                raise CalcError("Too few operands or too many operators")

            # execute the operator with its operands (reversed)
            # catch errors raised by the 'decimal' library and convert them to my format
            try:
                token = token.execute(operands[::-1])
            except InvalidOperation:
                raise CalcError("Invalid operation")
            except Overflow:
                raise CalcError("Number too big")
            except DecimalException as e:
                raise CalcError("Error: " + str(e).split("decimal.")[1].split("'>]")[0])

            # make it a 'Num' and push it to the stack
            stack.push(Num(token))

    # there should be exactly 1 number on the stack at the end - the answer
    # if not, there are too many operands or too few operators
    if len(stack) != 1:
        raise CalcError("Too many operands or too few operators")

    # the last item on the stack is the answer
    return stack.pop()

def post_calc(ans):
    """Apply settings to the answer"""

    # check a valid number
    ans = float(ans)
    if ans == float("inf"):
        raise CalcError("Number too big")

    # round all answers to 15 decimal places
    ans = round(ans, 15)

    # convert to a string so it is in an exact and built-in type
    ans = str(ans)

    # remove trailing 0s
    while ans[-1] == "0":
        ans = ans[:-1]

    # remove the decimal point if it ends in one but nothing after that
    if ans[-1] == ".":
        ans = ans[:-1]

    # if the number is now '-0', make '0'
    if ans == "-0":
        ans = "0"

    # convert back to my representation of standard form
    ans = ans.lower().replace("e", "~")

    return ans

def calculate(expr, debug=False):
    """
    Calculate the answer to 'expr'.
    If CalcError (or it's child CalcOperationError) has been raised,
    it is due to an invalid expression so needs to be caught and presented as an error message
    Any other exceptions are errors in the code

    :param expr (str): The expression to execute
    :param debug (bool): Whether or not to print out extra information to check for errors. Default: False
    :return ans (str): The answer to 'expr'
    """

    assert isinstance(expr, str), "param 'expr' must be a string"

    for func in [tokenise, convert, execute, post_calc]:

        # execute each function with the result from the last
        expr = func(expr)

        # output the progress if debug is on
        if debug:
            print(str(func).split("function ")[1].split(" at ")[0] + ":", repr(expr))

    return expr

# only runs if the file is run directly (not if imported)
if __name__ == "__main__":

    # quick interface to test the calculator with debug on to check it's working
    # catches errors due to the user's input and displays them as error messages
    # repeats until the user enters an empty expression
    expression = input("\n>")
    while expression != "":
        try:
            print(calculate(expression))
        except CalcError as e:
            print(e)
        expression = input("\n>")
