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

def persistent2_no_question():
    return pre_pad_with_nones(extend_with_nones([1, None, 2, None, 3, None, 2, None, None, None, 3, None, None, 3, 3, None, 2], 7))

def acute_pain_question():
    return pre_pad_with_nones([None, None, 2, None, 3, None, 2, None, None, None, None])

def acute_pain_no_question():
    return pre_pad_with_nones([1, None, 2, None, 3, None, 2, None])

def two_days_soreness():
    return [1, 2]

def persistent_soreness_question():
    return pre_pad_with_nones(extend_with_nones([1, None, None, 2, None, None, 3, None, None, 2, None], 15))

def persistent_soreness_no_question():
    return pre_pad_with_nones([1, None, None, 2, None, None, 3, None, None, 2, None])

def persistent_pain_question():
    return pre_pad_with_nones(extend_with_nones([3, None, 3, None, None, 3, 3, None, 3, None, None, 2, None, None, None, None, None, None, None, 2], 15))

def persistent_pain_no_question():
    return pre_pad_with_nones([3, None, 3, None, None, 3, 3, None, 3, None, None, 2, None, None, None, None, None, None, None, 2])

def new_persistent_pain_no_question():
    return [3, None, 3, None, None, 3, 3, None, 3, None, None, 2, None, None, None, None, None, None, None, 2]

def persistent_soreness_no_question_25_days():
    return pre_pad_with_nones([1, None, None, 2, None, None, 3, None, None, 2, None, None, 3, None, None, 3, 2, None, None, 2, None, None, 3, None, 3])

def persistent_soreness_no_question_29_days():
    return pre_pad_with_nones([1, None, None, 2, None, None, 3, None, None, 2, None, None, 3, None, None, 3, 2, None, None, 2, None, None, 3, None, 3, None, 2, None, 2])

def persistent_soreness_no_question_31_days():
    return pre_pad_with_nones([1, None, None, 2, None, None, 3, None, None, 2, None, None, 3, None, None, 3, 2, None, None, 2, None, None, 3, None, 3, None, 2, None, 2, None, 2])
