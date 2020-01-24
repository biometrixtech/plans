import re


def get_tags(name, tagging_dict):
    name = name.strip().lower()
    tags = []

    for tag, keywords in tagging_dict.items():
        for keyword in keywords:
            pat = r'\b'+keyword+r'\b'
            if re.search(pat, name) is not None:
                tags.append(tag)
                break
    return tags
