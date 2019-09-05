from models.body import Body


def test_load_body():

    body = Body()

    body.mark_sore(5)
    body.mark_sore(6)

    parts = []

    for b, body_part in body.body_parts.items():

        if (body_part.underactive_count > 0 or body_part.overactive_count > 0 or
            body_part.weakness_count > 0 or body_part.possible_soreness_source_count > 0):
            parts.append(body_part)

    assert len(body.body_parts) > 0

