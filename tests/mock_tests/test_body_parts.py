from fathomapi.api.config import Config
Config.set('FILENAMES', {'exercise_library': 'exercise_library_fathom.json',
                           'body_part_mapping': 'body_part_mapping_fathom.json'})


from models.body_parts import BodyPartFactory, BodyPartLocation, BodyPart


def test_lower_back_muscle():
    assert BodyPartFactory().is_muscle(BodyPart(BodyPartLocation(12), None))
    assert not BodyPartFactory().is_joint(BodyPart(BodyPartLocation(12), None))
    assert not BodyPartFactory().is_ligament(BodyPart(BodyPartLocation(12), None))


def test_erector_spinae_muscle():
    erector_spinae = BodyPart(BodyPartLocation(26), None)
    assert BodyPartFactory().is_muscle(erector_spinae)


def test_body_part_mapping_knee():
    knee = BodyPartFactory().get_body_part(BodyPartLocation.knee)
    assert set(knee.agonists) == {15}
    assert set(knee.synergists) == {16, 4}
    assert set(knee.stabilizers) == {11, 8}
    assert set(knee.antagonists) == {6}


def test_body_part_mapping_obliques_abdominals():
    bpf = BodyPartFactory()
    obliques = bpf.get_body_part(BodyPartLocation.obliques)
    abdominals = bpf.get_body_part(BodyPartLocation.abdominals)
    assert set(obliques.agonists) == set(abdominals.agonists)
    assert set(obliques.synergists) == set(abdominals.synergists)
    assert set(obliques.stabilizers) == set(abdominals.stabilizers)
    assert set(obliques.antagonists) == set(abdominals.antagonists)
