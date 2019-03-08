def extend_with_nones(existing_list, number_of_nones):
    none_list = []

    for x in range(0, number_of_nones):
        none_list.append(None)

    existing_list.extend(none_list)

    return existing_list

def pre_pad_with_nones(existing_list, total_days=35):
    if len(existing_list) > total_days:
        raise ValueError('History is too long')
    elif len(existing_list) == total_days:
        return existing_list
    else:
        nones = [None] * (total_days - len(existing_list))
        nones.extend(existing_list)
        return nones



def create_body_part_history(history, body_part, side, pain):
    return {"severity": history,
            "pain": pain,
            "body_part": body_part,
            "side": side}

def persistent2_question():
    return pre_pad_with_nones(extend_with_nones([1, None, 2, None, 3, None, 2, None, None, None, 3, None, None, 3, 3, None, 2], 15))

def acute_pain_no_question():
    return pre_pad_with_nones([1, None, 2, None, 3, None, 2, None])