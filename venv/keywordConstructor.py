import numpy
import time
import urllib.error
import urllib.request
from pprint import pprint
import pandas as pd
import spacy
import time
import csv

stopwords = open("stopwords.txt").read().splitlines()
whitelist = set('abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 -')
prohibited = ['film', 'movie', 'films', 'movies']
nlp = spacy.load("en_core_web_sm")


# IDF
def IDFcomputation(titles,uniqueWords, dictionary):
    import math
    NDocs = len(titles)
    idfDict = dict.fromkeys(uniqueWords, 0)
    for i in range(0, len(uniqueWords) - 1):
        current = dictionary[:, i]
        ciao = 1
        for x in current:
            if x != None:
                if x > 0:
                    idfDict[uniqueWords[i]] += 1
    for word, val in idfDict.items():
        if val > 0:
            idfDict[word] = math.log(NDocs / float(val))
    return idfDict

def keywordGenerator(db, db_len):
    keyword_6 = open('keywords.csv', 'w', newline='')
    seconds = time.time()
    bagsOfWords = numpy.empty(shape=(db_len, 2), dtype=object)
    titles = []
    y = 0
    for x in db[0]:
        bagsOfWords[y][0] = str(x)
        titles.append(str(x))
        y += 1
    y = 0
    for x in db[1]:
        text = str(x).lower()
        plot = text
        plot = ''.join(filter(whitelist.__contains__, plot))
        plot = plot.split(' ')
        for p in plot:
            if len(p) < 3:
                plot.remove(p)
        bagsOfWords[y][1] = plot
        y += 1
    print('Bag of word fatto!')
    uniqueWords = bagsOfWords[0][1]

    for x in range(1, len(bagsOfWords)):
        if bagsOfWords[x][1] != None:
            uniqueWords = set(uniqueWords).union(set(bagsOfWords[x][1]))

    # creo il dizionario con le occorrenze di ogni parola
    uniqueWords = list(uniqueWords)
    print('Unique word fatto!')
    dictionary = numpy.empty(shape=(db_len, len(uniqueWords)), dtype=object)
    y=0
    for x in range(0, len(bagsOfWords)):
        numOfWords = dict.fromkeys(uniqueWords, 0)
        numbers = []
        if bagsOfWords[y][1] != None:
            for word in bagsOfWords[y][1]:
                if word != '':
                    numOfWords[word] += 1
            dictionary[y,:]= [*numOfWords.values()]
        y += 1

    Idf = IDFcomputation(titles, uniqueWords, dictionary)
    keyword_1 = open('kw1.csv', 'w', newline='')
    writer1 = csv.writer(keyword_1, delimiter=';')
    for j, v in Idf.items():
        writer1.writerow((j,v))

    return  Idf



