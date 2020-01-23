import pandas as pd
import numpy as np
from database.cooccurence import generate_co_occurrence_matrix, get_list_from_name

import itertools

common_words = ['all', 'just', 'being', 'over', 'both', 'through', 'yourselves', 'its', 'before', 'herself', 'had', 'should', 'to', 'only', 'under', 'ours', 'has', 'do', 'them', 'his', 'very', 'they', 'not', 'during', 'now', 'him', 'nor', 'did', 'this', 'she', 'each', 'further', 'where', 'few', 'because', 'doing', 'some', 'are', 'our', 'ourselves', 'out', 'what', 'for', 'while', 'does', 'above', 'between', 't', 'be', 'we', 'who', 'were', 'here', 'hers', 'by', 'on', 'about', 'of', 'against', 's', 'or', 'own', 'into', 'yourself', 'down', 'your', 'from', 'her', 'their', 'there', 'been', 'whom', 'too', 'themselves', 'was', 'until', 'more', 'himself', 'that', 'but', 'don', 'with', 'than', 'those', 'he', 'me', 'myself', 'these', 'up', 'will', 'below', 'can', 'theirs', 'my', 'and', 'then', 'is', 'am', 'it', 'an', 'as', 'itself', 'at', 'have', 'in', 'any', 'if', 'again', 'no', 'when', 'same', 'how', 'other', 'which', 'you', 'after', 'most', 'such', 'why', 'a', 'off', 'i', 'yours', 'so', 'the', 'having', 'once']

words_dict = {}
movements_pd = pd.read_csv('soflete_movements.csv')

total = 0
instructions = 0
for index, ex in movements_pd.iterrows():
    total += 1
    if ex['instructions'] != "" and ex['instructions'] is not np.nan:
        instructions += 1
    name = ex['name'].strip(" ").lower()
    ex_words = get_list_from_name(name)
    for word in ex_words:
        if word in words_dict.keys():
            words_dict[word]['movements'].append(ex.id)
        else:
            words_dict[word] = {'word': word, 'movements': [ex.id]}

for word in words_dict.values():
    word['total'] = len(word['movements'])
    word['movement_counts'] = len(set(word['movements']))
    del word['movements']
df_values = list(words_dict.values())


count_pd = pd.DataFrame(df_values)
count_pd.sort_values(by='total', inplace=True, ascending=False)
count_pd.to_csv('word_frequencies_name.csv', index=False)
print('completed frequency analysis')

text_data = []
for index, ex in movements_pd.iterrows():
    name = ex['name'].strip(" ").lower()
    ex_words = get_list_from_name(name)
    text_data.append(ex_words)

# Create one list using many lists
data = list(itertools.chain.from_iterable(text_data))
words = list(count_pd.word.values)
matrix, vocab_index = generate_co_occurrence_matrix(data, text_data)

data_matrix = pd.DataFrame(matrix, index=vocab_index,
                           columns=vocab_index)

data_matrix = data_matrix[words]
data_matrix = data_matrix.reindex(words)
upper = pd.DataFrame(np.triu(data_matrix.values),
                     index=words,
                     columns=words)
upper.to_csv('cooccurence_matrix.csv')
print('completed co-occurence')
