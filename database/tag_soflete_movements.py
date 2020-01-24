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
print('HERE')
