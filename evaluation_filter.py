import numpy as np
import pandas as pd
import re
import random
from matplotlib import pyplot as plt


def count_filter(data, filter_list):
    counter = 0
    for d in data:
        accepted = True
        for f in filter_list:
            accepted = accepted and f(str(d))
        if accepted:
            counter += 1
    return counter


def create_words(words, length):
    output = []
    for i in range(length):
        word_amount = random.randint(1, 5)
        words_tmp = []
        for j in range(word_amount):
            words_tmp.append(str(random.choice(words)))
        if random.random() < 0.2:
            words_tmp.append(".")
        if random.random() < 0.2:
            words_tmp.append(".")
        output.append(' '.join(words_tmp))
    return output


def is_valid_length(data):
    return len(data) > 30


def is_valid_punctuation(data):
    punctuation_matches = re.findall(r'[.!?]', data)
    if not punctuation_matches:
        return False
    return len(punctuation_matches) >= 1


def is_valid_word_count(data):
    words = data.split()
    return len(words) >= 4


path_sentences = "./data/deu_news_2022_100K-sentences.txt"
path_words = "./data/deu_news_2022_100K-words.txt"

df_sentences = pd.read_csv(path_sentences, delimiter='\t', names=["index", "data"])
df_words = pd.read_csv(path_words, delimiter='\t', names=["index", "data", "id"])

sentences_list = list(df_sentences["data"])
words_list_tmp = list(df_words["data"])
words_list = create_words(words_list_tmp, 100_000)

sentences_counter = count_filter(sentences_list, [is_valid_punctuation, is_valid_length])
words_counter = count_filter(words_list, [is_valid_punctuation, is_valid_length])

test_cases_sentences = [
    (count_filter(sentences_list, [is_valid_punctuation]), "Satzzeichen"),
    (count_filter(sentences_list, [is_valid_length]), "Länge"),
    (count_filter(sentences_list, [is_valid_word_count]), "Wortanzahl"),
    (count_filter(sentences_list, [is_valid_punctuation, is_valid_length]), "Satzzeichen + Länge"),
    (count_filter(sentences_list, [is_valid_punctuation, is_valid_word_count]), "Satzzeichen + Wortanzahl"),
    (count_filter(sentences_list, [is_valid_length, is_valid_word_count]), "Länge + Wortanzahl"),
    (count_filter(sentences_list, [is_valid_punctuation, is_valid_length, is_valid_word_count]), "Satzzeichen + Länge + Wortanzahl"),
]

test_cases_words = [
    (count_filter(words_list, [is_valid_punctuation]), "Satzzeichen"),
    (count_filter(words_list, [is_valid_length]), "Länge"),
    (count_filter(words_list, [is_valid_word_count]), "Wortanzahl"),
    (count_filter(words_list, [is_valid_punctuation, is_valid_length]), "Satzzeichen + Länge"),
    (count_filter(words_list, [is_valid_punctuation, is_valid_word_count]), "Satzzeichen + Wortanzahl"),
    (count_filter(words_list, [is_valid_length, is_valid_word_count]), "Länge + Wortanzahl"),
    (count_filter(words_list, [is_valid_punctuation, is_valid_length, is_valid_word_count]), "Satzzeichen + Länge + Wortanzahl"),
]

for test_case in test_cases_sentences:
    print(test_case[0] / len(sentences_list))

print("------------------")

for test_case in test_cases_words:
    print((len(words_list) - test_case[0]) / len(words_list))

width = 0.3
spacing = 1

labels = [test_case[1] for test_case in test_cases_sentences]

values_sentences = [test_case[0] / len(sentences_list) for test_case in test_cases_sentences]
values_words = [(len(words_list) - test_case[0]) / len(words_list) for test_case in test_cases_words]

x_pos = np.arange(len(labels))

plt.bar(x_pos * spacing - width/2, values_sentences, width, label='Relevante Informationen')
plt.bar(x_pos * spacing + width/2, values_words, width, label='Irrelevante Informationen')

plt.xlabel('Filter')
plt.ylabel('Effizienz')
plt.title('Filtereffizienz')
plt.xticks(x_pos * spacing, labels, fontsize=7, rotation='vertical')
plt.legend()
plt.tight_layout()

plt.show()
