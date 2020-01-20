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


def test_lower_body():
    lower_body = BodyPartFactory().get_body_part(BodyPartLocation.lower_body)
    assert len(lower_body.dynamic_stretch_exercises) == 4
    assert len(lower_body.dynamic_integrate_exercises) == 4
    assert len(lower_body.static_integrate_exercises) == 1
    assert len(lower_body.inhibit_exercises) == len(lower_body.static_stretch_exercises) == len(lower_body.active_stretch_exercises) == len(lower_body.isolated_activate_exercises) == 0

    lower_body_no_sample = BodyPartFactory().get_body_part(BodyPartLocation.lower_body, False)
    assert len(lower_body_no_sample.dynamic_stretch_exercises) == len(lower_body.dynamic_stretch_exercises)
    assert len(lower_body_no_sample.dynamic_integrate_exercises) == len(lower_body.dynamic_integrate_exercises)
    assert len(lower_body_no_sample.static_integrate_exercises) == len(lower_body.static_integrate_exercises)


def test_glutes():
    glutes = BodyPartFactory().get_body_part(BodyPartLocation.glutes, False)
    assert len(glutes.inhibit_exercises) == 1
    assert len(glutes.static_stretch_exercises) == 6
    assert len(glutes.active_stretch_exercises) == 3
    assert len(glutes.dynamic_stretch_exercises) == 3
    assert len(glutes.isolated_activate_exercises) == 7
    assert len(glutes.static_integrate_exercises) == 0
    assert len(glutes.dynamic_integrate_exercises) == 0


def test_glutes_sample():
    glutes = BodyPartFactory().get_body_part(BodyPartLocation.glutes)
    assert len(glutes.inhibit_exercises) == 1
    assert len(glutes.static_stretch_exercises) == 1
    assert len(glutes.active_stretch_exercises) == 1
    assert len(glutes.dynamic_stretch_exercises) == 1
    assert len(glutes.isolated_activate_exercises) == 1
    assert len(glutes.static_integrate_exercises) == 0
    assert len(glutes.dynamic_integrate_exercises) == 0
