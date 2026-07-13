import mul


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
        if getattr(generator(*(tests[i][0])), method)() == tests[i][1]:
            passed += 1
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




