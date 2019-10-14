from models.soreness_base import BodyPartLocation



def test_muscle_group():
    body_part = BodyPartLocation(55)
    res = BodyPartLocation.get_muscle_group(body_part)

    assert res is not False
    assert res == BodyPartLocation.quads

def test_muscle_group_joint():
    body_part = BodyPartLocation(19)
    res = BodyPartLocation.get_muscle_group(body_part)

    assert not res

def test_muscle_group_muscle_group():
    body_part = BodyPartLocation.quads
    res = BodyPartLocation.get_muscle_group(body_part)

    assert res
    assert res == body_part