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
        print("\033[1;31mTest {} failed: \033[0;37mInput: {}. Expected: {}. Actual: {}.".format(i, tests[i][0], func(*tests[i][0]), tests[i][1]))


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



test("removeTrailingZeroes", mul.removeTrailingZeros, [
    ((int("111000000", 2),), int("111", 2)),
    ((int("111000100", 2),), int("1110001", 2))
])



test_method("Posit.extract", make_posit_from_bit_pattern, "extract", [
    ((3, "0111111001001111"), (0, 5, 2, 47)), 
    ((4, "0000001010101100"), (0, -5, 5, 11)),
    ((4, "0111110100"), (0, 4, 8, 1)),
    ((8, "0111110"), (0, 4, 0, 1)),
    ((8, "0000000"), None),
    ((8, "1000000"), None)
])



ex_1 = make_posit_from_bit_pattern(2, "00000000")
ex_2 = make_posit_from_bit_pattern(2, "00000000")
ex_3 = make_posit_from_bit_pattern(2, "00000000")
posit_builder_tests = [
    ((0, 0, 0), ex_1),
    ((1, -1, 2), ex_2),
    ((0, 4, 1), ex_3),
]

builder = mul.Posit(8, 2)



test_method("Posit.get_value", make_posit_from_bit_pattern, "get_value", [
    ((2, "01101000"), (64)),
    ((2, "01110111"), (3072)), 
    ((2, "00001101"), (0.0014648438)),
    ((2, "10101010"), (-7)),
    ((2, "11110010"), (-0.001953125)),
    ((2, "0000000"), (0)),
    ((2, "1000000"), (Decimal("inf")))
])

test("construct", builder.construct, posit_builder_tests)





