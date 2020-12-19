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

whitelist = set('abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -')
prohibited = ['film', 'movie', 'films', 'movies']
nlp = spacy.load("en_core_web_sm")

def cleaning(doc):
    txt = [token.lemma_ for token in doc]
    if len(txt) > 2:
        return ' '.join(txt)


# IDF
def IDFcomputation(titles,uniqueWords, bagOfWords):
    import math
    NDocs = 17477
    idfDict = dict.fromkeys(uniqueWords, 0)
    index = 0
    c = False
    for j in bagOfWords:
        for i in j[1]:
            if i in uniqueWords:
                idfDict[i] += 1
    for t, v in idfDict.items():
        if v > 0:
            idfDict[t] = math.log10(NDocs / float(v))
    return idfDict

def keywordGenerator(db, db_len):
    keyword_6 = open('keywords.csv', 'w', newline='')
    seconds = time.time()
    bags = numpy.empty(shape=(db_len, 2), dtype=object)
    titles = []
    y = 0
    for x in db[0]:
        bags[y][0] = str(x)
        titles.append(str(x))
        y += 1
    y = 0
    for x in db[1]:
        text = str(x).lower()
        plot = text
        plot = ''.join(filter(whitelist.__contains__, plot))
        doc = nlp(plot)
        plot = cleaning(doc)
        if  isinstance(plot, str):
            plot = plot.split(' ')
        if plot is None:
            ciao = 1
        bags[y][1] = list(set(plot))
        y += 1
    print('Bag of word fatto!')
    uniqueWords = bags[0][1]

    for x in range(1, len(bags)):
        if bags[x][1] != None:
            uniqueWords = set(uniqueWords).union(set(bags[x][1]))

    # creo il dizionario con le occorrenze di ogni parola
    uniqueWords = list(uniqueWords)
    print('Unique word fatto!')
    list_of_words = []
    Idf = IDFcomputation(titles, uniqueWords, bags)

    keyword_1 = open('ide_list.csv', 'w', newline='')
    writer1 = csv.writer(keyword_1, delimiter=';')

    for j, v in Idf.items():
        writer1.writerow((j,v))

    return  Idf



db = pd.read_csv(r"C:\Users\Stefano\Desktop\databaseFilmPlotWikipedia.csv", sep=';', header=None)
idf = keywordGenerator(db, 17477)