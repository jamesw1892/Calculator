"""
Contains the interface between a user interface and the calculator

User interfaces should use the calculator via this to record and provide access to memory by instantiating the 'Interface' class and:
- if the user wants to calculate the answer to an expression, use the 'calculate' method
- if the user wants to view instructions, use the 'instructions' attribute
- if the user wants to view memory, use the 'recent_memory' method
- if the user wants to clear memory, use the 'clear_memory' method
- if the user wants to insert a specific memory answer into their expression:
    1) get which memory item is being requested
    2) use the 'memory_item' method to get the original expression and answer of interest
    3) it may be best to re-calculate the answer using the original expression and the 'calculate' method
    4) insert the answer from memory or the re-calculated answer into the expression

Before calling the 'recent_memory' or 'memory_item' methods with a number from the user,
the interface should call 'len_memory' to check how many items are in memory and verify the number wanted
is a valid number and equal to or less than the number of items in memory. If not, display the relevant error message
If either of these methods are called with invalid parameters, they will raise 'IndexError'
"""

from Calc import calculate, instructions
from Errors import CalcError

class Interface:
    """
    The interface between a user interface and the calculator
    Stores and allows access to memory
    """

    def __init__(self):

        # private attributes
        self.__memory = []
        self.__instructions = instructions

    @property
    def instructions(self):
        """Return the instructions without being able to change it"""
        return self.__instructions

    def calculate(self, expr):
        """
        Calculate the answer to 'expr', storing the expression and answer in memory for later recall
        If CalcError (or it's child CalcOperationError) has been raised,
        it is due to an invalid expression so needs to be caught and presented as an error message
        Any other exceptions are errors in the code

        :param expr (str): The expression to execute
        :return ans (str): The answer to 'expr'
        """

        # calculate the answer with the calculator
        ans = calculate(expr)

        # add the expression and answer to the front of the list
        self.__memory.insert(0, (expr, ans))

        return ans

    def len_memory(self):
        """
        Return the number of items in memory

        :return (int): The number of items in memory
        """

        return len(self.__memory)

    def memory_item(self, num_calculations_ago=1):
        """
        Retrieve an answer from memory along with the expression that resulted in it
        Will raise 'IndexError' if 'num_calculations_ago' isn't an integer between 1 and the number of items in memory

        :param num_calculations_ago (int): The item to retrieve from memory: 1 is the most recent calculation, ascending from there. Default: None
        :return (tuple): A 2-value tuple where the 0th index is the string expression and the 1st is the string answer
        """

        # invalid cases
        if not isinstance(num_calculations_ago, int):
            raise IndexError("Must be an integer")
        if self.len_memory() < num_calculations_ago:
            raise IndexError("There aren't that many items saved in memory")
        if num_calculations_ago < 1:
            raise IndexError("Must be greater than or equal to 1")

        # typical cases
        return self.__memory[num_calculations_ago - 1]

    def recent_memory(self, num_to_retrieve=None):
        """
        Retrieve a list of answers from memory along with the expressions that resulted in each of them
        Will raise IndexError if 'num_to_retrieve' isn't an integer greater than or equal to 1

        :param num_to_retrieve (int): The number of answers to retrieve. 'None' means all. Default: None
        :return (list): The memory items (most recent first) which are each a 2-value tuple where the 0th
                        index is the string expression and the 1st is the string answer
        """

        # make 'None' mean all and if there are less than asked for, just return the number available
        if num_to_retrieve is None or num_to_retrieve > self.len_memory():
            num_to_retrieve = self.len_memory()

        # invalid cases
        if not isinstance(num_to_retrieve, int):
            raise IndexError("Must be an integer (whole number")
        if num_to_retrieve < 0:
            raise IndexError("Must be greater than or equal to 0")

        # typical cases
        # the slice selects the first 'num_to_retrieve' items in the list 'self.__memory'
        return self.__memory[:num_to_retrieve]

    def clear_memory(self):
        """Clear the calculator's memory"""

        self.__memory.clear()

# only runs if the file is run directly (not if imported)
if __name__ == "__main__":

    # instantiate the class
    calc = Interface()

    # extend instructions
    new_instructions = calc.instructions + "\n\nType 'memory' to view previous calculations, 'instructions' to view instructions, 'clear' to clear the memory, 'ans' in place of the previous answer and 'Mx' where x is a number in place of the xth previous answer"

    # quick user interface to test the calculator through the interface and memory access
    # repeats until the user enters an empty expression
    expression = input("\n>").lower()
    while expression != "":

        # typing 'instructions' will output the general instructions
        if "instructions" in expression:
            print(new_instructions)

        # typing 'clear' will clear the memory
        elif "clear" in expression:
            calc.clear_memory()
            print("Memory cleared")

        # typing 'memory' will output all previous calculations
        elif "memory" in expression:
            count = 1
            for expr, ans in calc.recent_memory():
                print("{}: {} = {}".format(count, expr, ans))
                count += 1
            if count == 1:
                print("Memory is empty")

        else:
            try:
                # including 'ans' will replace it with the previous answer
                if "ans" in expression:
                    if calc.len_memory() == 0:
                        raise CalcError("Memory is empty")
                    else:
                        expression = expression.replace("ans", calc.memory_item()[1])

                # including 'Mx' will replace it with the xth previous answer
                while "m" in expression:

                    # take all digits between the 'M' and the first non-digit
                    index = expression.split("m")[1]
                    pos = 0
                    while pos < len(index) and index[pos] in "0123456789":
                        pos += 1
                    index = index[:pos]

                    if index == "":
                        raise CalcError("You must give a memory reference after 'm'")

                    try:
                        index = int(index)
                    except ValueError:
                        raise CalcError("Memory references must be whole numbers")
                    else:
                        if index > calc.len_memory():
                            raise CalcError("Not enough items in memory")
                        elif index < 1:
                            raise CalcError("Memory references must be greater than or equal to 1")
                    expression = expression.replace("m{}".format(index), calc.memory_item(index)[1])

                # calculate the answer
                print(calc.calculate(expression))

            # catch and output errors
            except CalcError as e:
                print(e)

        expression = input("\n>").lower()
