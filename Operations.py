"""
Contains the code for the operations that can be used in the calculator
"""

from Errors import CalcOperationError
from math import log, sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh
from random import randint

def op_add(x, y):
    """Return x add y"""

    # typical cases
    return x + y

def op_sub(x, y):
    """Return x subtract y"""

    # typical cases
    return x - y

def op_mul(x, y):
    """Return x multiplied by y"""

    # typical cases
    return x * y

def op_true_div(x, y):
    """Return x divided by y"""

    # invalid case
    if y == 0:
        raise CalcOperationError("Cannot divide by 0", "/", [x, y])

    # typical cases
    return x / y

def op_floor_div(x, y):
    """Return x divided by y, rounded down"""

    # invalid case
    if y == 0:
        raise CalcOperationError("Cannot divide by 0", "\\", [x, y])

    # typical cases
    return x // y

def op_mod(x, y):
    """Return x mod y - the remainder when x is divided by y"""

    # invalid case
    if y == 0:
        raise CalcOperationError("Cannot divide by 0", "%", [x, y])

    # typical cases
    return x % y

def op_exp(x, y):
    """Return x to the power of y"""

    # invalid case
    if x == 0 and y == 0:
        raise CalcOperationError("0 to the power of 0 is undefined", "^", [x, y])

    # typical cases
    return x ** y

def op_root(root, x):
    """Return the root th root of x"""

    # invalid cases
    if root <= 0 or root % 1 != 0:
        raise CalcOperationError("The root must be a positive whole number", "¬", [root, x])

    # specific case of power
    return x ** (1 / root)

def op_permutations(n, r):
    """Return the number of ways there are to arrange r things in n places, counting all orders"""

    # invalid cases
    if n % 1 != 0 or r % 1 != 0 or n < 0 or r < 0:
        raise CalcOperationError("Both must be whole numbers and cannot be negative", "P", [n, r])
    if r > n:
        raise CalcOperationError("r ({}) cannot be greater than n ({})".format(r, n), "P", [n, r])

    # use the factorial operation already defined
    return op_factorial(n) / op_factorial(n - r)

def op_combinations(n, r):
    """Return the number of ways there are to arrange r things in n places, only counting 1 order"""

    # invalid cases
    if n % 1 != 0 or r % 1 != 0 or n < 0 or r < 0:
        raise CalcOperationError("Both must be whole numbers and cannot be negative", "C", [n, r])
    if r > n:
        raise CalcOperationError("r ({}) cannot be greater than n ({})".format(r, n), "C", [n, r])

    # use the factorial operation already defined
    return op_factorial(n) / (op_factorial(r) * op_factorial(n - r))

def op_pos(x):
    """Return the positive of x"""

    # typical cases
    return +x

def op_neg(x):
    """Return the negative of x"""

    # typical cases
    return -x

def op_factorial(x):
    """Return x factorial"""

    # invalid cases
    if x < 0 or x % 1 != 0:
        raise CalcOperationError("Must be whole number and cannot be negative", "!", [x])

    # multiply all numbers between 1 and x together
    product = 1
    while x > 1:
        product *= x
        x -= 1

    return product

def func_ln(x):
    """Return ln(x)"""

    # invalid cases
    if x <= 0:
        raise CalcOperationError("Can only find the natural log of positive numbers", "ln", [x])

    # use the function from the 'math' library
    return log(x)

def func_log(x, base):
    """Return log of x to the base 'base'"""

    # invalid cases
    if x <= 0 or base <= 0:
        raise CalcOperationError("Can only find the log of a positive number with a positive base", "log", [base, x])

    # use the function from the 'math' library
    return log(x, base)

def func_abs(x):
    """Return the absolute value of x"""

    # use the built-in function
    return abs(x)

def prime_factors(x):
    """Return a list of all of x's prime factors"""

    # invalid cases
    if x % 1 != 0 or x < 1:
        raise CalcOperationError("Must be a positive whole number", "LCM or HCF", [x])

    # typical cases
    factors = []
    i = 2

    # for each possible factor
    while i ** 2 <= x:

        # if it is a factor, add it and adjust x to prevent repeats
        # don't increment i as more than 1 of the same factor is possible
        if x % i == 0:
            x //= i
            factors.append(i)

        # if it's not a factor, increment it to find the next
        else:
            i += 1

    # add the last factor if x isn't 1
    if x > 1:
        factors.append(x)

    return factors

def to_dict(factors):
    """Gets a dictionary of all numbers and the number of times they occur"""

    factors_dict = {}
    for factor in factors:

        # if that prime factor is already in the dictionary, increment the count
        if factor in factors_dict:
            factors_dict[factor] += 1

        # otherwise, add it with an initial count of 1
        else:
            factors_dict[factor] = 1

    return factors_dict

def product_dict(dictionary):

    # the number of times each key appears is the value corresponding to that key
    # so the product is the product of all keys each to the power of their value
    product = 1
    for key in dictionary:
        product *= key ** dictionary[key]

    return product

def func_lcm(x, y):
    """Return the lowest common multiple of x and y"""

    # gets dictionaries for each input with the prime factors
    # as the key and the number of occurances as the value
    prime_factors_x = to_dict(prime_factors(x))
    prime_factors_y = to_dict(prime_factors(y))

    # the prime factors of the LCM of x and y starts as those of x
    prime_factors_lcm = prime_factors_x.copy()

    for factor in prime_factors_y:

        # if the factor is not in LCM or it is in LCM but y has more, add the number y has
        if factor not in prime_factors_lcm or prime_factors_y[factor] > prime_factors_lcm[factor]:
            prime_factors_lcm[factor] = prime_factors_y[factor]

    # multiply all the prime factors together to get the LCM
    return product_dict(prime_factors_lcm)

def func_hcf(x, y):
    """Return the highest common factor of x and y"""

    # gets dictionaries for each input with the prime factors
    # as the key and the number of occurances as the value
    prime_factors_x = to_dict(prime_factors(x))
    prime_factors_y = to_dict(prime_factors(y))

    prime_factors_hcf = {}

    # the prime factors of the HCF are the minimum number that are in both x and y
    for factor in prime_factors_x:
        if factor in prime_factors_y:
            prime_factors_hcf[factor] = min(prime_factors_x[factor], prime_factors_y[factor])

    # multiply all the prime factors together to get the HCF
    return product_dict(prime_factors_hcf)

def func_quadp(a, b, c):
    """Return the positive square root answer of the quadratic equation ax^2 + bx + c = 0"""

    from Datatypes import Num

    discriminant = b**2 - 4*a*c

    # invalid cases
    if discriminant < 0:
        raise CalcOperationError("No real solutions", "quadp", [a, b, c])

    # quadratic formula with positive square root
    return (-b + discriminant**Num("0.5")) / (2 * a)

def func_quadn(a, b, c):
    """Return the positive square root answer of the quadratic equation ax^2 + bx + c = 0"""

    from Datatypes import Num

    discriminant = b**2 - 4*a*c

    # invalid cases
    if discriminant < 0:
        raise CalcOperationError("No real solutions", "quadn", [a, b, c])

    # quadratic formula with negative square root
    return (-b - discriminant**Num("0.5")) / (2 * a)

def func_rand(low, high):
    """Return a random integer between 'low' and 'high'"""

    # invalid cases
    if low % 1 != 0 or high % 1 != 0:
        raise CalcOperationError("Must be whole numbers", "rand", [low, high])

    # if the wrong way around, swap them
    if low > high:
        low, high = high, low

    # use the function from the 'random' library
    return randint(low, high)

def func_sin(x):
    """Return sin(x) where x is in radians"""

    # use the function from the 'math' library
    return sin(x)

def func_cos(x):
    """Return cos(x) where x is in radians"""

    # use the function from the 'math' library
    return cos(x)

def func_tan(x):
    """Return tan(x) where x is in radians"""

    from Datatypes import valid_tokens, Num

    # invalid cases
    if x % valid_tokens["pi"] == Num("0.5") * valid_tokens["pi"]:
        raise CalcOperationError("Tangent is undefined for values half way between multiples of pi", "tan", [x])

    # use the function from the 'math' library
    return tan(x)

def func_arsin(x):
    """Return arsin(x) where the answer is in radians"""

    # invalid cases
    if x < -1 or x > 1:
        raise CalcOperationError("Inverse sine is only defined for values between -1 and 1 inclusive", "arsin", [x])

    # use the function from the 'math' library
    return asin(x)

def func_arcos(x):
    """Return arcos(x) where the answer is in radians"""

    # invalid cases
    if x < -1 or x > 1:
        raise CalcOperationError("Inverse cosine is only defined for values between -1 and 1 inclusive", "arcos", [x])

    # use the function from the 'math' library
    return acos(x)

def func_artan(x):
    """Return artan(x) where the answer is in radian"""

    # use the function from the 'math' library
    return atan(x)

def func_sinh(x):
    """Return sinh(x) where x is in radians"""

    # use the function from the 'math' library
    return sinh(x)

def func_cosh(x):
    """Return cosh(x) where x is in radians"""

    # use the function from the 'math' library
    return cosh(x)

def func_tanh(x):
    """Return tanh(x) where x is in radians"""

    # use the function from the 'math' library
    return tanh(x)

def func_arsinh(x):
    """Return arsinh(x) where the answer is in radians"""

    # use the function from the 'math' library
    return asinh(x)

def func_arcosh(x):
    """Return arcosh(x) where the answer is in radians"""

    # invalid cases
    if x < 1:
        raise CalcOperationError("Inverse hyperbolic cosine is undefined for values less than 1", "arcosh", [x])

    # use the function from the 'math' library
    return acosh(x)

def func_artanh(x):
    """Return artanh(x) where the answer is in radian"""

    # invalid cases
    if x <= -1 or x >= 1:
        raise CalcOperationError("Inverse hyperbolic tangent is only defined for values between -1 and 1 exclusive", "artanh", [x])

    # use the function from the 'math' library
    return atanh(x)
