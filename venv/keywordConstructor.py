import numpy
import time
import urllib.error
import urllib.request
from pprint import pprint
import pandas as pd
import spacy
import time
import csv
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
whitelist = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ- ')
prohibited = ['film', 'movie', 'films', 'movies']
nlp = spacy.load("en_core_web_sm")

def cleaning(doc):
    txt = [token.text for token in doc if len(token.text) > 2]
    return txt

# IDF
def IDFcomputation(titles,uniqueWords, bagOfWords, NDocs):
    import math
    idfDict = dict.fromkeys(uniqueWords, 0)
    index = 0
    c = False
    for j in bagOfWords:
        for i in j[1].keys():
            if i in uniqueWords:
                idfDict[i] += 1
    to_delete = []
    for t, v in idfDict.items():
        if v > 15:
            idfDict[t] = math.log10(NDocs / float(v))
        else:
            to_delete.append(t)
    for d in to_delete:
        del idfDict[d]
    return idfDict

def keywordGenerator(db, db_len):
    seconds = time.time()
    vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 1), token_pattern=r'[A-Za-z]*-?[A-Za-z]*', stop_words=None, lowercase=False)
    analyzer = vectorizer.build_analyzer()
    bags = numpy.empty(shape=(db_len, 2), dtype=object)
    titles = []
    y = 0
    for x in db[0]:
        bags[y][0] = str(x)
        titles.append(str(x))
        y += 1
    y = 0
    for x in db[1]:
        text = str(x)
        plot = analyzer(text)
        plot = [i.lower() for i in plot if i != '' and len(i) > 2]
        word_freq = Counter([token for token in plot])
        bags[y][1] = word_freq
        y += 1
    print('Bag of word fatto!')
    uniqueWords = bags[0][1].keys()

    for x in range(1, len(bags)):
        if bags[x][1] != None:
            uniqueWords = set(uniqueWords).union(bags[x][1].keys())

    # creo il dizionario con le occorrenze di ogni parola
    uniqueWords = list(uniqueWords)
    print('Unique word fatto!')
    list_of_words = []
    Idf = IDFcomputation(titles, uniqueWords, bags, db_len)

    keyword_1 = open('idf_list2.csv', 'w', newline='')
    writer1 = csv.writer(keyword_1, delimiter=';')

    for j, v in Idf.items():
        writer1.writerow((j,v))

    print('Idf Generated')

    return  Idf



db = pd.read_csv(r"C:\Users\Stefano\Desktop\databaseFilmPlotWikipedia.csv", sep=';', header=None)
idf = keywordGenerator(db, 17477)

