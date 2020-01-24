import numpy as np
# import nltk
# from nltk import bigrams
import itertools
# import pandas as pd

common_words = ['all', 'just', 'being', 'over', 'both', 'through', 'yourselves', 'its', 'before', 'herself', 'had', 'should', 'to', 'only', 'under', 'ours', 'has', 'do', 'them', 'his', 'very', 'they', 'not', 'during', 'now', 'him', 'nor', 'did', 'this', 'she', 'each', 'further', 'where', 'few', 'because', 'doing', 'some', 'are', 'our', 'ourselves', 'out', 'what', 'for', 'while', 'does', 'above', 'between', 't', 'be', 'we', 'who', 'were', 'here', 'hers', 'by', 'on', 'about', 'of', 'against', 's', 'or', 'own', 'into', 'yourself', 'down', 'your', 'from', 'her', 'their', 'there', 'been', 'whom', 'too', 'themselves', 'was', 'until', 'more', 'himself', 'that', 'but', 'don', 'with', 'than', 'those', 'he', 'me', 'myself', 'these', 'up', 'will', 'below', 'can', 'theirs', 'my', 'and', 'then', 'is', 'am', 'it', 'an', 'as', 'itself', 'at', 'have', 'in', 'any', 'if', 'again', 'no', 'when', 'same', 'how', 'other', 'which', 'you', 'after', 'most', 'such', 'why', 'a', 'off', 'i', 'yours', 'so', 'the', 'having', 'once']


def generate_co_occurrence_matrix(corpus, text_data):
    vocab = set(corpus)
    vocab = list(vocab)
    vocab_index = {word: i for i, word in enumerate(vocab)}

    # Create bigrams from all words in corpus
    # bi_grams = list(bigrams(corpus))

    bigram_freq_dict = {}
    for name in text_data:
        name_bigrams = list(itertools.combinations(name, 2))
        for bi_gram in name_bigrams:
            bi_gram = tuple(sorted(bi_gram))
            if bi_gram[0] != bi_gram[1]:
                if bi_gram in bigram_freq_dict.keys():
                    bigram_freq_dict[bi_gram] += 1
                else:
                    bigram_freq_dict[bi_gram] = 1

    # Frequency distribution of bigrams ((word1, word2), num_occurrences)
    # bigram_freq = nltk.FreqDist(bi_grams).most_common(len(bi_grams))

    bigram_freq = [(key, value) for key, value in bigram_freq_dict.items()]
    # Initialise co-occurrence matrix
    # co_occurrence_matrix[current][previous]
    co_occurrence_matrix = np.zeros((len(vocab), len(vocab)))

    # Loop through the bigrams taking the current and previous word,
    # and the number of occurrences of the bigram.
    for bigram in bigram_freq:
        current = bigram[0][1]
        previous = bigram[0][0]
        count = bigram[1]
        pos_current = vocab_index[current]
        pos_previous = vocab_index[previous]
        co_occurrence_matrix[pos_current][pos_previous] = count
        co_occurrence_matrix[pos_previous][pos_current] = count

    co_occurrence_matrix = np.matrix(co_occurrence_matrix)

    # return the matrix and the index
    return co_occurrence_matrix, vocab_index


def cleanup_word(word):
    word = word.lower()
    if word[-1] == 's':
        if word not in ['press', 'across', 'legless', 'bench-press']:
            word = word[0:-1]
    if word == 'bb':
        word = 'barbell'
    if word == 'kb':
        word = 'kettlebell'
    if word == 'db':
        word = 'dumbbell'
    # if word == 'lunges':
    #     word = 'lunge'
    # if word == 'squats':
    #     word = 'squat'
    # if word == 'squats':
    #     word = 'squat'
    # if word == 'pulls':
    #     word = 'pull'
    if word == 'w/':
        word = 'with'
    # if word == 'push-ups':
    #     word = 'push-up'
    # if word == 'pull-ups':
    #     word = 'pull-up'
    # if word == 'curls':
    #     word = 'curl'
    # if word == 'deadlifts':
    #     word = 'deadlift'
    # if word == 'extensions':
    #     word = 'extension'
    # if word == 'step-ups':
    #     word = 'step-up'
    # if word == 'get-ups':
    #     word = 'get-up'
    # if word == 'hands':
    #     word = 'hand'

    return word


def get_list_from_name(name):
    name = name.replace("  ", " ")
    name = name.replace("push ups", "push-up")
    name = name.replace("push up", "push-up")
    name = name.replace("pull ups", "pull-up")
    name = name.replace("pull up", "pull-up")
    name = name.replace("step ups", "step-up")
    name = name.replace("step up", "step-up")
    name = name.replace("get ups", "get-up")
    name = name.replace("get up", "get-up")
    ex_words = set(name.split(" "))
    ex_words = list(ex_words - set(common_words))
    ex_words_out = []
    for word in ex_words:
        word = cleanup_word(word)
        ex_words_out.append(word)
    return ex_words_out
