from body_parts import BodyPartFactory, BodyPartLocation, BodyPart


def test_lower_back_muscle():
    assert BodyPartFactory().is_muscle(BodyPart(BodyPartLocation(12), None))
    assert not BodyPartFactory().is_joint(BodyPart(BodyPartLocation(12), None))
    assert not BodyPartFactory().is_ligament(BodyPart(BodyPartLocation(12), None))


def test_erector_spinae_muscle():
    erector_spinae = BodyPart(BodyPartLocation(26), None)
    assert BodyPartFactory().is_muscle(erector_spinae)
