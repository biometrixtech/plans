from fathomapi.api.config import Config
Config.set('PROVIDER_INFO', {'exercise_library_filename': 'exercise_library_fathom.json',
                             'body_part_mapping_filename': 'body_part_mapping_fathom.json'})

from models.soreness_base import BodyPartLocation
from models.body_parts import BodyPartFactory


def test_muscle_group():
    body_part = BodyPartLocation(55)
    res = BodyPartLocation.get_muscle_group(body_part)

    assert res == BodyPartLocation.quads


def test_muscle_group_joint():
    body_part = BodyPartLocation(19)
    res = BodyPartLocation.get_muscle_group(body_part)

    assert not res


def test_muscle_group_muscle_group():
    body_part = BodyPartLocation.quads
    res = BodyPartLocation.get_muscle_group(body_part)
    assert res == body_part


def test_get_muscles_in_group():
    body_part = BodyPartLocation.quads
    res = BodyPartLocation.get_muscles_for_group(body_part)
    assert res
    assert len(res) == 4


def test_get_muscles_in_group_joint():
    body_part = BodyPartLocation.knee
    res = BodyPartLocation.get_muscles_for_group(body_part)
    assert not res


def test_get_muscles_in_group_muscle():
    body_part = BodyPartLocation.gluteus_medius_anterior_fibers
    res = BodyPartLocation.get_muscles_for_group(body_part)
    assert not res


def test_multiple_muscles_same_group():
    body_part_1 = BodyPartLocation(45)
    body_part_2 = BodyPartLocation(46)
    group1 = BodyPartLocation.get_muscle_group(body_part_1)
    group2 = BodyPartLocation.get_muscle_group(body_part_2)
    assert group1 == group2
    assert group1 == BodyPartLocation.hamstrings


def test_different_body_parts():
    bpf = BodyPartFactory()

    # joint
    assert bpf.is_joint(BodyPartLocation.knee)
    assert not bpf.is_ligament(BodyPartLocation.knee)
    assert not bpf.is_muscle(BodyPartLocation.knee)

    # ligament
    assert not bpf.is_joint(BodyPartLocation.it_band)
    assert bpf.is_ligament(BodyPartLocation.it_band)
    assert not bpf.is_muscle(BodyPartLocation.it_band)

    # muscle group
    assert not bpf.is_joint(BodyPartLocation.quads)
    assert not bpf.is_ligament(BodyPartLocation.quads)
    assert bpf.is_muscle(BodyPartLocation.quads)

    # muscle
    assert not bpf.is_joint(BodyPartLocation.vastus_lateralis)
    assert not bpf.is_ligament(BodyPartLocation.vastus_lateralis)
    assert bpf.is_muscle(BodyPartLocation.vastus_lateralis)

    # muscle group without muscles defined
    assert not bpf.is_joint(BodyPartLocation.biceps)
    assert not bpf.is_ligament(BodyPartLocation.biceps)
    assert bpf.is_muscle(BodyPartLocation.biceps)
