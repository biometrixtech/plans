from models.body import Body


def test_load_body():

    body = Body()

    body.mark_tight(5)

    for b, body_part in body.body_parts.items():

        if body_part is not None and body_part.underactive_risk_count > 0:
            h=0

    assert len(body.body_parts) > 0

