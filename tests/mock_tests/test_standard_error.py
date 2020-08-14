from models.training_volume import StandardErrorRange


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
