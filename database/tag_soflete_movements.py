import pandas as pd
# import numpy as np
from database.get_tags import get_tags
from database.dictionary_sources import get_all_dict
movements_pd = pd.read_csv('soflete_movements.csv')

mov_tags_dict = {}
tagless_movements = []
tagging_dict = get_all_dict()

total = 0
instructions = 0
for index, ex in movements_pd.iterrows():
    name = ex['name'].strip(" ").lower()
    tags = get_tags(name, tagging_dict)
    mov_tags_dict[ex['name']] = tags
    if len(tags) == 0:
        tagless_movements.append(name)
print(tagless_movements)
all_tags = list(tagging_dict.keys())
columns = ['name'].extend(all_tags)

tags_pd = pd.DataFrame(columns=columns)
move_dict_list = []
for name, tags in mov_tags_dict.items():
    move_dict_list.append({"name": name, "tags": tags})
    mov_dict = {"name": name}
    for tag in tags:
        mov_dict[tag] = True

    # tags_pd = tags_pd.append(pd.Series(mov_dict), ignore_index=True)
# tags_pd.to_csv('movement_tags.csv', index=False)
tags_pd_2 = pd.DataFrame(move_dict_list)
tags_pd_2.to_csv('movement_tags_2.csv', index=False)
print('here')
