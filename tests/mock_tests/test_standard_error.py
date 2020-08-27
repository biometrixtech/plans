from models.training_volume import StandardErrorRange, Assignment


def test_integer_deserialise():

    input_dict = {"old_load_value": 50}
    standard_error_range = StandardErrorRange.json_deserialise(input_dict.get('old_load_value'))

    assert 50 == standard_error_range.observed_value


def test_object_deserialise():

    error_range = StandardErrorRange()
    error_range.observed_value = 78
    error_range_json = error_range.json_serialise()
    input_dict = {"new_load_value": error_range_json}

    standard_error_range = StandardErrorRange.json_deserialise(input_dict.get('new_load_value'))

    assert 78 == standard_error_range.observed_value


def test_object_deserialise_none():

    input_dict = {"new_load_value": None}

    standard_error_range = StandardErrorRange.json_deserialise(input_dict.get('new_load_value'))

    assert None is standard_error_range.observed_value


def test_get_min_from_error_range_list_1():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.7, upper_bound=2)

    result = StandardErrorRange.get_min_from_error_range_list([ser1, ser2])

    assert result == .1


def test_get_min_from_error_range_list_2():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(observed_value=.3)

    result = StandardErrorRange.get_min_from_error_range_list([ser1, ser2])

    assert result == .3


def test_get_max_from_error_range_list_1():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.7, upper_bound=2)

    result = StandardErrorRange.get_max_from_error_range_list([ser1, ser2])

    assert result == 2


def test_get_max_from_error_range_list_2():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(observed_value=5)

    result = StandardErrorRange.get_max_from_error_range_list([ser1, ser2])

    assert result == 5


def test_get_average_from_error_range_list_1():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.7, upper_bound=2)
    result = StandardErrorRange.get_average_from_error_range_list([ser1, ser2])

    assert result.lower_bound < result.observed_value < result.upper_bound


def test_get_average_from_error_range_list_2():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.7, upper_bound=2)
    result = StandardErrorRange.get_average_from_error_range_list([ser1, ser2])

    assert result.lower_bound < result.observed_value < result.upper_bound


def test_get_average_from_error_range_list_3():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.7, upper_bound=2)
    result = StandardErrorRange.get_average_from_error_range_list([ser1, ser2])

    assert result.lower_bound < result.observed_value < result.upper_bound


def test_get_average_from_error_range_list_4():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(observed_value=5)
    result = StandardErrorRange.get_average_from_error_range_list([ser1, ser2])

    assert result.lower_bound < result.observed_value < result.upper_bound


def test_get_average_from_error_range_list_5():
    ser1 = StandardErrorRange(observed_value=.7)
    ser2 = StandardErrorRange(observed_value=5)
    result = StandardErrorRange.get_average_from_error_range_list([ser1, ser2])

    assert result.lower_bound == result.observed_value == result.upper_bound


def test_get_average_from_error_range_list_6():
    ser1 = StandardErrorRange(lower_bound=.5, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, upper_bound=2)
    result = StandardErrorRange.get_average_from_error_range_list([ser1, ser2])

    assert result.lower_bound < result.observed_value < result.upper_bound


def test_get_average_from_error_range_list_7():
    ser1 = StandardErrorRange(lower_bound=.5, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.7, upper_bound=2)
    result = StandardErrorRange.get_average_from_error_range_list([ser1, ser2])

    assert result.lower_bound < result.observed_value < result.upper_bound


def test_get_stddev_from_error_range_list_1():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(observed_value=5)
    result = StandardErrorRange.get_stddev_from_error_range_list([ser1, ser2])

    assert result.lower_bound is not None
    assert result.upper_bound is not None
    assert result.observed_value is not None


def test_get_stddev_from_error_range_list_2():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.5, upper_bound=1.1)
    ser3 = StandardErrorRange(observed_value=5)
    result = StandardErrorRange.get_stddev_from_error_range_list([ser1, ser2, ser3])

    assert result.lower_bound is not None
    assert result.upper_bound is not None
    assert result.observed_value is not None


def test_add_1():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.5, upper_bound=1.1)
    ser1.add(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_add_2():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(observed_value=.5)
    ser1.add(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_add_3():
    ser1 = StandardErrorRange(observed_value=.7)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.5, upper_bound=1.1)
    ser1.add(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_add_4():
    ser1 = StandardErrorRange(observed_value=.7)
    ser2 = StandardErrorRange(observed_value=.5)
    ser1.add(ser2)

    assert ser1.lower_bound == 1.2
    assert ser1.upper_bound == 1.2
    assert ser1.observed_value == 1.2


def test_add_5():
    ser1 = StandardErrorRange(observed_value=.7)
    ser2 = StandardErrorRange(lower_bound=.1, upper_bound=1.1)
    ser1.add(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_add_6():
    ser1 = StandardErrorRange(lower_bound=.1, upper_bound=1.1)
    ser2 = StandardErrorRange(lower_bound=.1, upper_bound=1.1)
    ser1.add(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_get_sum_from_error_range_list_1():
    ser1 = StandardErrorRange(lower_bound=.1, upper_bound=1.1)
    ser2 = StandardErrorRange(lower_bound=.1, upper_bound=1.1)
    result = StandardErrorRange.get_sum_from_error_range_list([ser1, ser2])
    result2 = ser1.plagiarize()
    result2.add(ser2)

    assert result.lower_bound < result.observed_value < result.upper_bound
    assert result.lower_bound == result2.lower_bound
    assert result.observed_value == result2.observed_value
    assert result.upper_bound == result2.upper_bound


def test_get_sum_from_error_range_list_2():
    ser1 = StandardErrorRange(lower_bound=.1, upper_bound=1.1)
    ser2 = StandardErrorRange(observed_value=5)
    result = StandardErrorRange.get_sum_from_error_range_list([ser1, ser2])
    result2 = ser1.plagiarize()
    result2.add(ser2)

    assert result.lower_bound < result.observed_value < result.upper_bound
    assert result.lower_bound == result2.lower_bound
    assert result.observed_value == result2.observed_value
    assert result.upper_bound == result2.upper_bound


def test_get_sum_from_error_range_list_3():
    ser1 = StandardErrorRange(observed_value=2)
    ser2 = StandardErrorRange(observed_value=5)
    result = StandardErrorRange.get_sum_from_error_range_list([ser1, ser2])
    result2 = ser1.plagiarize()
    result2.add(ser2)

    assert result.lower_bound == result.observed_value == result.upper_bound
    assert result.lower_bound == result2.lower_bound
    assert result.observed_value == result2.observed_value
    assert result.upper_bound == result2.upper_bound


def test_get_sum_from_error_range_list_4():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.5, upper_bound=1.1)
    result = StandardErrorRange.get_sum_from_error_range_list([ser1, ser2])
    result2 = ser1.plagiarize()
    result2.add(ser2)

    assert result.lower_bound < result.observed_value < result.upper_bound
    assert result.lower_bound == result2.lower_bound
    assert result.observed_value == result2.observed_value
    assert result.upper_bound == result2.upper_bound


def test_subtract_1():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.5, upper_bound=1.1)
    ser1.subtract(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_subtract_2():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(observed_value=.5)
    ser1.subtract(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_subtract_3():
    ser1 = StandardErrorRange(observed_value=.7)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.5, upper_bound=1.1)
    ser1.subtract(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_subtract_4():
    ser1 = StandardErrorRange(observed_value=.7)
    ser2 = StandardErrorRange(observed_value=.5)
    ser1.subtract(ser2)

    assert ser1.lower_bound == ser1.observed_value == ser1.upper_bound


def test_subtract_5():
    ser1 = StandardErrorRange(observed_value=.7)
    ser2 = StandardErrorRange(lower_bound=.1, upper_bound=1.1)
    ser1.subtract(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_subtract_6():
    ser1 = StandardErrorRange(lower_bound=.1, upper_bound=1.1)
    ser2 = StandardErrorRange(lower_bound=.1, upper_bound=1.1)
    ser1.subtract(ser2)

    assert ser1.lower_bound == ser1.observed_value == ser1.upper_bound


def test_multiply_1():
    scalar = 1
    ser = StandardErrorRange(lower_bound=.1, upper_bound=1.1)
    ser.multiply(scalar)

    assert ser.lower_bound == .1
    assert ser.upper_bound == 1.1
    assert ser.observed_value is None


def test_multiply_2():
    scalar = 2.5
    ser = StandardErrorRange(lower_bound=.1, observed_value= .7,upper_bound=1.1)
    ser.multiply(scalar)

    assert ser.lower_bound == .25
    assert ser.upper_bound == 2.5 * 1.1
    assert ser.observed_value == 2.5 * .7


def test_multiply_3():
    scalar = .5
    ser = StandardErrorRange(observed_value=1.6)
    ser.multiply(scalar)

    assert ser.lower_bound is None
    assert ser.upper_bound is None
    assert ser.observed_value == .8


def test_multiply_4():
    scalar = 1
    ser = StandardErrorRange(lower_bound=.1, upper_bound=1.1)
    ser.multiply(scalar)

    assert ser.lower_bound == .1
    assert ser.upper_bound == 1.1
    assert ser.observed_value is None

def test_multiply_range_1():
    ser1 = StandardErrorRange(lower_bound=.5, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.7, upper_bound=2)
    ser1.multiply_range(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_multiply_range_2():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, upper_bound=2)
    ser1.multiply_range(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_multiply_range_3():
    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.7, upper_bound=2)
    ser1.multiply_range(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_multiply_range_4():
    ser1 = StandardErrorRange(lower_bound=.5, upper_bound=.9)
    ser2 = StandardErrorRange(observed_value=5)
    ser1.multiply_range(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_multiply_range_5():
    ser1 = StandardErrorRange(observed_value=.7)
    ser2 = StandardErrorRange(observed_value=5)
    ser1.multiply_range(ser2)

    assert ser1.observed_value is not None
    assert ser1.lower_bound is not None
    assert ser1.upper_bound is not None


def test_multiply_range_6():
    ser1 = StandardErrorRange(lower_bound=.5, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, upper_bound=2)
    ser1.multiply_range(ser2)

    assert ser1.lower_bound < ser1.upper_bound
    assert ser1.observed_value is not None


def test_multiply_range_7():
    ser1 = StandardErrorRange(observed_value=.5)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.7, upper_bound=2)
    ser1.multiply_range(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_divide_1():
    scalar = 1
    ser = StandardErrorRange(lower_bound=.1, observed_value=1.2,upper_bound=2)
    ser.divide(scalar)

    assert ser.lower_bound < ser.observed_value < ser.upper_bound


def test_divide_2():
    scalar = .1
    ser = StandardErrorRange(lower_bound=.1, observed_value=1.2,upper_bound=2)
    ser.divide(scalar)

    assert ser.lower_bound < ser.observed_value < ser.upper_bound


def test_divide_3():
    scalar = 1.2
    ser = StandardErrorRange(lower_bound=.1, observed_value=1.2,upper_bound=2)
    ser.divide(scalar)

    assert ser.lower_bound < ser.observed_value < ser.upper_bound


def test_divide_4():
    scalar = 2
    ser = StandardErrorRange(observed_value=1.2)
    ser.divide(scalar)

    assert ser.observed_value is not None
    assert ser.lower_bound is None
    assert ser.upper_bound is None


def test_divide_5():
    scalar = 2.5
    ser = StandardErrorRange(lower_bound=.1, upper_bound=2)
    ser.divide(scalar)

    assert ser.lower_bound < ser.upper_bound
    assert ser.observed_value is None


def test_divide_range_1():

    ser1 = StandardErrorRange(lower_bound=.5, observed_value=.7, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.7, upper_bound=2)
    ser1.divide_range(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_divide_range_2():

    ser1 = StandardErrorRange(lower_bound=.5, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1,upper_bound=2)
    ser1.divide_range(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_divide_range_3():

    ser1 = StandardErrorRange(lower_bound=.5, upper_bound=.9)
    ser2 = StandardErrorRange(observed_value=.7)
    ser1.divide_range(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_divide_range_4():

    ser1 = StandardErrorRange(lower_bound=.5, upper_bound=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.7, upper_bound=2)
    ser1.divide_range(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_divide_range_5():

    ser1 = StandardErrorRange(observed_value=.9)
    ser2 = StandardErrorRange(lower_bound=.1, observed_value=.7, upper_bound=2)
    ser1.divide_range(ser2)

    assert ser1.lower_bound < ser1.observed_value < ser1.upper_bound


def test_divide_range_6():

    ser1 = StandardErrorRange(observed_value=.9)
    ser2 = StandardErrorRange(observed_value=.7)
    ser1.divide_range(ser2)

    assert ser1.lower_bound == ser1.observed_value == ser1.upper_bound
