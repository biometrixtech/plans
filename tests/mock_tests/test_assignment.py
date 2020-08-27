from training_volume import Assignment, StandardErrorRange


def test_lowest_value_min_max_present():
    a = Assignment(min_value=.1, max_value=.3)
    assert a.lowest_value() == .1


def test_lowest_value_only_assigned_value():
    a = Assignment(assigned_value=.1)
    assert a.lowest_value() == .1



def test_highest_value_min_max_present():
    a = Assignment(min_value=.1, max_value=.3)
    assert a.highest_value() == .3


def test_highest_value_only_assigned_value():
    a = Assignment(assigned_value=.1)
    assert a.highest_value() == .1


def test_fix_min_max_max_lower():
    a = Assignment(min_value=.2, max_value=.1)
    a.fix_min_max()
    assert a.min_value < a.max_value


def test_fix_min_max_max_higher():
    a = Assignment(min_value=.1, max_value=.2)
    a.fix_min_max()
    assert a.min_value < a.max_value


def test_plagiarize():
    a = Assignment(min_value=.1, max_value=.2, assigned_value=.15, assignment_level='high', assignment_type='a')
    b = a.plagiarize()

    assert a.json_serialise() == b.json_serialise()


def test_divide_scalar_assignment_min_max_1():
    scalar = 2
    assignment = Assignment(min_value=1, max_value=1.5)
    result = Assignment.divide_scalar_assignment(scalar, assignment)

    assert result.min_value < result.max_value


def test_divide_scalar_assignment_min_max_2():
    scalar = .5
    assignment = Assignment(min_value=1, max_value=1.5)
    result = Assignment.divide_scalar_assignment(scalar, assignment)

    assert result.min_value < result.max_value


def test_divide_scalar_assignment_min_max_3():
    scalar = 1.5
    assignment = Assignment(min_value=1, max_value=1.5)
    result = Assignment.divide_scalar_assignment(scalar, assignment)

    assert result.min_value < result.max_value


def test_divide_scalar_assignment_min_max_4():
    scalar = 1
    assignment = Assignment(min_value=1, max_value=1.5)
    result = Assignment.divide_scalar_assignment(scalar, assignment)

    assert result.min_value < result.max_value


def test_divide_scalar_assignment_assigned_1():
    scalar = 1
    assignment = Assignment(assigned_value=1)
    result = Assignment.divide_scalar_assignment(scalar, assignment)

    assert result.assigned_value == 1
    assert result.min_value is None
    assert result.max_value is None


def test_divide_scalar_assignment_assigned_2():
    scalar = .001
    assignment = Assignment(assigned_value=1)
    result = Assignment.divide_scalar_assignment(scalar, assignment)

    assert result.assigned_value == .001
    assert result.min_value is None
    assert result.max_value is None


def test_divide_scalar_assignment_assigned_3():
    scalar = 1000
    assignment = Assignment(assigned_value=10)
    result = Assignment.divide_scalar_assignment(scalar, assignment)

    assert result.assigned_value == 100
    assert result.min_value is None
    assert result.max_value is None


def test_divide_assignment_by_scalar_min_max_1():
    scalar = .5
    assignment = Assignment(min_value=1, max_value=1.5)
    result = Assignment.divide_assignment_by_scalar(assignment, scalar)

    assert result.min_value < result.max_value


def test_divide_assignment_by_scalar_min_max_2():
    scalar = 1.5
    assignment = Assignment(min_value=1, max_value=1.5)
    result = Assignment.divide_assignment_by_scalar(assignment, scalar)

    assert result.min_value < result.max_value


def test_divide_assignment_by_scalar_min_max_3():
    scalar = 1
    assignment = Assignment(min_value=1, max_value=1.5)
    result = Assignment.divide_assignment_by_scalar(assignment, scalar)

    assert result.min_value < result.max_value


def test_divide_assignment_by_scalar_min_max_4():
    scalar = 2
    assignment = Assignment(min_value=1, max_value=1.5)
    result = Assignment.divide_assignment_by_scalar(assignment, scalar)

    assert result.min_value < result.max_value


def test_divide_assignment_by_scalar_min_max_5():
    scalar = 1.1
    assignment = Assignment(min_value=1, max_value=1.5)
    result = Assignment.divide_assignment_by_scalar(assignment, scalar)

    assert result.min_value < result.max_value


def test_divide_assignment_by_scalar_assigned_1():
    scalar = 1
    assignment = Assignment(assigned_value=1)
    result = Assignment.divide_assignment_by_scalar(assignment, scalar)

    assert result.assigned_value == 1
    assert result.min_value is None
    assert result.max_value is None


def test_divide_assignment_by_scalar_assigned_2():
    scalar = .1
    assignment = Assignment(assigned_value=1)
    result = Assignment.divide_assignment_by_scalar(assignment, scalar)

    assert result.assigned_value == 10
    assert result.min_value is None
    assert result.max_value is None


def test_divide_assignment_by_scalar_assigned_3():
    scalar = 1000
    assignment = Assignment(assigned_value=10)
    result = Assignment.divide_assignment_by_scalar(assignment, scalar)

    assert result.assigned_value == .01
    assert result.min_value is None
    assert result.max_value is None


def test_multiply_assignment_by_scalar_min_max_1():
    scalar = .5
    assignment = Assignment(min_value=1.1, max_value=1.5)
    result = Assignment.multiply_assignment_by_scalar(assignment, scalar)

    assert result.min_value < result.max_value


def test_multiply_assignment_by_scalar_min_max_2():
    scalar = 1.1
    assignment = Assignment(min_value=1.1, max_value=1.5)
    result = Assignment.multiply_assignment_by_scalar(assignment, scalar)

    assert result.min_value < result.max_value


def test_multiply_assignment_by_scalar_min_max_3():
    scalar = 1.5
    assignment = Assignment(min_value=1.1, max_value=1.5)
    result = Assignment.multiply_assignment_by_scalar(assignment, scalar)

    assert result.min_value < result.max_value


def test_multiply_assignment_by_scalar_min_max_4():
    scalar = 1.2
    assignment = Assignment(min_value=1.1, max_value=1.5)
    result = Assignment.multiply_assignment_by_scalar(assignment, scalar)

    assert result.min_value < result.max_value


def test_multiply_assignment_by_scalar_min_max_5():
    scalar = 2
    assignment = Assignment(min_value=1.1, max_value=1.5)
    result = Assignment.multiply_assignment_by_scalar(assignment, scalar)

    assert result.min_value < result.max_value


def test_multiply_assignment_by_scalar_assigned_1():
    scalar = 2
    assignment = Assignment(assigned_value=1.1)
    result = Assignment.multiply_assignment_by_scalar(assignment, scalar)

    assert result.assigned_value == 2.2
    assert result.min_value is None
    assert result.max_value is None


def test_multiply_assignment_by_scalar_assigned_2():
    scalar = .2
    assignment = Assignment(assigned_value=1.1)
    result = Assignment.multiply_assignment_by_scalar(assignment, scalar)

    assert result.assigned_value == 1.1 * .2
    assert result.min_value is None
    assert result.max_value is None


def test_multiply_assignment_by_scalar_assigned_3():
    scalar = 1
    assignment = Assignment(assigned_value=1.1)
    result = Assignment.multiply_assignment_by_scalar(assignment, scalar)

    assert result.assigned_value == 1.1
    assert result.min_value is None
    assert result.max_value is None


def test_divide_assignments_both_min_max_1():
    a = Assignment(min_value=.5, max_value=5)
    b = Assignment(min_value=1.5, max_value=1.6)
    result = Assignment.divide_assignments(a, b)

    assert result.min_value < result.max_value
    assert result.assigned_value is None


def test_divide_assignments_both_min_max_2():
    a = Assignment(min_value=.5, max_value=.6)
    b = Assignment(min_value=1.5, max_value=1.6)
    result = Assignment.divide_assignments(b, a)

    assert result.min_value < result.max_value
    assert result.assigned_value is None


def test_divide_assignments_dividend_assigned_divisor_min_max_1():
    a = Assignment(assigned_value=2)
    b = Assignment(min_value=1.5, max_value=1.6)
    result = Assignment.divide_assignments(a, b)

    assert result.min_value < result.max_value
    assert result.assigned_value is None


def test_divide_assignments_dividend_assigned_divisor_min_max_2():
    a = Assignment(assigned_value=.5)
    b = Assignment(min_value=1.5, max_value=1.6)
    result = Assignment.divide_assignments(a, b)

    assert result.min_value < result.max_value
    assert result.assigned_value is None


def test_divide_assignments_dividend_min_max_divisor_assigned_1():
    a = Assignment(assigned_value=2)
    b = Assignment(min_value=1.5, max_value=1.6)
    result = Assignment.divide_assignments(b, a)

    assert result.min_value < result.max_value
    assert result.assigned_value is None


def test_divide_assignments_dividend_min_max_divisor_assigned_2():
    a = Assignment(assigned_value=.5)
    b = Assignment(min_value=1.5, max_value=1.6)
    result = Assignment.divide_assignments(b, a)

    assert result.min_value < result.max_value
    assert result.assigned_value is None


def test_divide_assignments_both_assigned_1():
    a = Assignment(assigned_value=5)
    b = Assignment(assigned_value=.5)
    result = Assignment.divide_assignments(a, b)

    assert result.assigned_value == 10
    assert result.min_value is None
    assert result.max_value is None


def test_divide_assignments_both_assigned_2():
    a = Assignment(assigned_value=.1)
    b = Assignment(assigned_value=5)
    result = Assignment.divide_assignments(a, b)

    assert result.assigned_value == .02
    assert result.min_value is None
    assert result.max_value is None


def test_multiply_assignments_both_min_max():
    a = Assignment(min_value=1.5, max_value=1.6)
    b = Assignment(min_value=.5, max_value=3.5)
    result = Assignment.multiply_assignments(a, b)

    assert result.min_value < result.max_value
    assert result.assigned_value is None


def test_multiply_assignments_one_assigned_one_min_max():
    a = Assignment(assigned_value=10)
    b = Assignment(min_value=.5, max_value=3.5)
    result = Assignment.multiply_assignments(a, b)

    assert result.min_value < result.max_value
    assert result.assigned_value is None


def test_add_value_min_max():
    a = Assignment(min_value=.5, max_value=3.5)
    a.add_value(.5)

    assert 1 == a.min_value < a.max_value == 4
    assert a.assigned_value is None


def test_add_value_assigned():
    a = Assignment(assigned_value=.5)
    a.add_value(.5)

    assert a.assigned_value == 1
    assert a.min_value is None
    assert a.max_value is None


def test_add_value_all_none():
    a = Assignment()
    a.add_value(.5)

    assert a.assigned_value == .5
    assert a.min_value is None
    assert a.max_value is None


def test_multiply_range_by_assignment_1():
    a = Assignment(min_value=1.1, max_value=1.5)
    er = StandardErrorRange(lower_bound=.5, upper_bound=.9, observed_value=.7)

    result = Assignment.multiply_range_by_assignment(er, a)

    assert result.lower_bound is not None
    assert result.upper_bound is not None
    assert result.observed_value is not None

    assert result.lower_bound < result.observed_value < result.upper_bound


def test_multiply_range_by_assignment_2():
    a = Assignment(min_value=1.1, max_value=1.5)
    er = StandardErrorRange(lower_bound=.5, upper_bound=.9)

    result = Assignment.multiply_range_by_assignment(er, a)

    assert result.lower_bound is not None
    assert result.upper_bound is not None
    assert result.observed_value is None

    assert result.lower_bound < result.upper_bound



def test_multiply_range_by_assignment_3():
    a = Assignment(assigned_value=1.1)
    er = StandardErrorRange(lower_bound=.5, upper_bound=.9)

    result = Assignment.multiply_range_by_assignment(er, a)

    assert result.lower_bound is not None
    assert result.upper_bound is not None
    assert result.observed_value is None

    assert result.lower_bound < result.upper_bound



def test_multiply_range_by_assignment_4():
    a = Assignment(assigned_value=1.1)
    er = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)

    result = Assignment.multiply_range_by_assignment(er, a)

    assert result.lower_bound is not None
    assert result.upper_bound is not None
    assert result.observed_value is not None

    assert result.lower_bound < result.observed_value < result.upper_bound



def test_multiply_range_by_assignment_5():
    a = Assignment(assigned_value=1.1)
    er = StandardErrorRange(observed_value=.7)

    result = Assignment.multiply_range_by_assignment(er, a)

    assert result.lower_bound is None
    assert result.upper_bound is None
    assert result.observed_value is not None

    assert result.observed_value == 1.1 * .7
