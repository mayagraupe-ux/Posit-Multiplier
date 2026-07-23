
import mul
from decimal import getcontext, Decimal
import math



def test(name, func, tests):
    print("-" * 10)
    print("Running {} tests for \033[;;1m{}()".format(len(tests), name))
    passed = 0
    failed = []

    for i in range(len(tests)):
        if func(*tests[i][0]) == tests[i][1]:
            passed +=1
        else:
            failed.append(i)

    print("\033[1;32m{}\033[0;37m out of {} tests passed".format(passed, len(tests)))

    for i in failed:
        actual_val = func(*tests[i][0])
        expected_val = tests[i][1]
        
        # Convert the actual and expected values to bitstrings
        actual_bits = get_bits(actual_val, 8)
        expected_bits = get_bits(expected_val, 8)
        
        print("\033[1;31mTest {} failed: \033[0;37mInput: {}. Actual: {} ({}). Expected: {} ({}).".format(
            i, 
            tests[i][0], 
            actual_bits,   # Prints bitstring
            actual_val,    # Prints integer in parentheses for debugging
            expected_bits, # Prints bitstring
            expected_val   # Prints integer in parentheses
        ))
       


def test_method(name, generator, method, tests):
    print("-" * 10)
    print("Running {} tests for \033[;;1m{}()".format(len(tests), name))
    passed = 0
    failed = []
    for i in range(len(tests)):
        actual = getattr(generator(*(tests[i][0])), method)()
        expected = tests[i][1]

        is_match = False
        if actual is None or expected is None:
            is_match = (actual == expected)
        else:
            try:
                #check if they are close
                is_match= math.isclose(float(actual), float(expected), rel_tol =1e-7)
            except (ValueError, TypeError):
                #if can't convert to floats ahhh, then use normal equality
                is_match = (actual == expected)
        
        if is_match: 
            passed+=1
        else:
            failed.append(i)

    print("\033[1;32m{}\033[0;37m out of {} tests passed".format(passed, len(tests)))
    for i in failed:
        print("\033[1;31mTest {} failed: \033[0;37mInput: {}. Actual: {}. Expected: {}.".format(i, tests[i][0], getattr(generator(*(tests[i][0])), method)(), tests[i][1]))
    
    print("-" * 10)


def make_posit_from_bit_pattern(es, bit_pattern):
    p = mul.Posit(len(bit_pattern), es)
    p.set_bit_pattern(bit_pattern)
    return p

def make_posit_and_construct(N, es, sign, scale, fraction):
    p = mul.Posit(N, es)
    return p.construct(sign, scale, fraction)

def get_bits(val, N):
    if (val is None):
        return 0
    if(type(val) is int):
        temp = mul.Posit(N, 2)
        temp.set_value(val)
    else:
        temp = val
    return temp.get_bits()
    
def make_posit_from_int(es, int, N):
    p = mul.Posit(N= N, es= es, value= int)
    return p
    





test("removeTrailingZeroes", mul.removeTrailingZeros, [
    ((int("111000000", 2),), int("111", 2)),
    ((int("111000100", 2),), int("1110001", 2))
])



test_method("Posit.extract", make_posit_from_bit_pattern, "extract", [
    ((3, "0111111001001111"), (0, 5, 2, 47)), 
    ((4, "0000001010101100"), (0, -5, 5, 11)),
    ((4, "0111110100"), (0, 4, 8, 1)),
    ((8, "0111110"), (0, 4, 0, 1)),
    ((8, "0000000"), (0, 0 , 0 , 0)),
    ((8, "1000000"), (1, 0, 0, 0))
])




test_method("Posit.get_value", make_posit_from_bit_pattern, "get_value", [
    ((2, "01101000"), (64)),
    ((2, "01110111"), (3072)), 
    ((2, "00001101"), (0.0014648438)),
    ((2, "10101010"), (-7)),
    ((2, "11110010"), (-0.001953125)),
    ((2, "0000000"), (0)),
    ((2, "1000000"), (Decimal("inf")))
])




# N, es , sign, scale, fraction  : es, bitpattern of result
test("construct", make_posit_and_construct, [
    ((8, 2, 0, 11, 5), make_posit_from_bit_pattern(2, "01110111")),
    ((8, 2, 0, 7, 3), make_posit_from_bit_pattern(2, "01101110")),
    ((8, 2, 0, -4, 15), make_posit_from_bit_pattern(2, "00100111")),
    ((8, 2, 0, 9, 12), make_posit_from_bit_pattern(2, "01110011")),
    ((8, 2, 0, 25, 17), make_posit_from_bit_pattern(2, "01111111")),
    ((8, 2, 0, -30, 10), make_posit_from_bit_pattern(2, "00000001")),
    ((8, 2, 1, -7, 12), make_posit_from_bit_pattern(2, "11101010")),
    ((8, 2, 1, -11, 7), make_posit_from_bit_pattern(2, "11110100")),
    ((8, 2, 1, 2, 9), make_posit_from_bit_pattern(2, "10101111"))
])
inf_posit = mul.Posit(N=8, es=2)
inf_posit.set_bit_pattern('10000000')


test("mult", mul.Posit.mult, [
    # --- Zero Property ---
        ((mul.Posit(value =0), mul.Posit(value=1)), mul.Posit(value=0)),
        ((mul.Posit(value=0), mul.Posit(value=0)), mul.Posit(value=0)),
        ((mul.Posit(value=-2.5), mul.Posit(value=0)), mul.Posit(value=0)),

        # --- Identity Property ---
        ((mul.Posit(value=1), mul.Posit(value=1)), mul.Posit(value=1)),
        ((mul.Posit(value=1), mul.Posit(value=4.5)), mul.Posit(value=4.5)),
        ((mul.Posit(value=-3), mul.Posit(value=1)), mul.Posit(value=-3)),

        # --- Sign Handling ---
        ((mul.Posit(value=2), mul.Posit(value=3)), mul.Posit(value=6)),
        ((mul.Posit(value=-2), mul.Posit(value=3)), mul.Posit(value=-6)),
        ((mul.Posit(value=2), mul.Posit(value=-3)), mul.Posit(value=-6)),
        ((mul.Posit(value=-2), mul.Posit(value=-3)), mul.Posit(value=6)),

        # --- Fractional Values ---
        ((mul.Posit(value=0.5), mul.Posit(value=0.5)), mul.Posit(value=0.25)),
        ((mul.Posit(value=0.25), mul.Posit(value=4)), mul.Posit(value=1)),
        ((mul.Posit(value=1.5), mul.Posit(value=2.5)), mul.Posit(value=3.75)),

        # --- Special Values (NaR - Not a Real) ---
        ((inf_posit, mul.Posit(value=1)), inf_posit),
        ((mul.Posit(value=0), inf_posit), inf_posit),
        ((inf_posit, inf_posit), inf_posit),
])






