import re, string


def get_tags(name, tagging_dict):
    name = name.strip().lower()
    name = name.translate(str.maketrans('', '', '!"#$%&\'()*+,.:;<=>?@[\\]^_`{|}~'))
    tags = []

    for tag, keywords in tagging_dict.items():
        for keyword in keywords:
            pat = r'\b'+keyword+r'\b'
            if re.search(pat, name) is not None:
                tags.append(tag)
                break
    # if len(tags) == 0:
    #     print(name)
    return tags
