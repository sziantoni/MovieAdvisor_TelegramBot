import numpy
import time
import urllib.error
import urllib.request
from pprint import pprint
import pandas as pd

stopwords = open("stopwords.txt").read().splitlines()
whitelist = set('abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ')

def keywordGenerator(db):
    bagsOfWords = numpy.empty(shape=(5000, 2), dtype=object)
    titles = []
    y = 0
    for x in db[0]:
        bagsOfWords[y][0] = str(x)
        titles.append(str(x))
        y += 1
    y = 0
    for x in db[1]:
        plot = str(x)
        plot = ''.join(filter(whitelist.__contains__, plot))
        bagsOfWords[y][1] = plot.lower().split(' ')
        y += 1

    uniqueWords = bagsOfWords[0][1]

    for x in range(1, len(bagsOfWords)):
        uniqueWords = set(uniqueWords).union(set(bagsOfWords[x][1]))

    # creo il dizionario con le occorrenze di ogni parola

    dictionary = numpy.empty(shape=(5000, 2), dtype=object)

    y = 0
    for x in range(0, len(bagsOfWords)):
        numOfWords = dict.fromkeys(uniqueWords, 0)
        for word in bagsOfWords[y][1]:
            numOfWords[word] += 1
        dictionary[y][0] = titles[y]
        dictionary[y][1] = numOfWords
        y += 1

    # calcolo di tf-idf

    # TF
    def TFcomputation(words, bag):
        TFcount = {}
        bagCount = len(bag)
        for word in words:
            TFcount[word] = words[word] / len(bag)
        return TFcount

    # IDF
    def IDFcomputation(documents):
        import math
        NDocs = len(documents)
        idfDict = dict.fromkeys(documents[0].keys(), 0)
        for document in documents:
            for word, val in document.items():
                if val > 0:
                    idfDict[word] += 1

        for word, val in idfDict.items():
            idfDict[word] = math.log(NDocs / float(val))
        return idfDict

    TFIDF_Array = numpy.empty(shape=(5000, 2), dtype=object)

    # TF-IDF
    def TFIDF_Matrix_Computation(TFMatrix, Idf):
        y = 0
        for i in TFMatrix[:, 1]:
            tfidf = {}
            for word, val in i.items():
                if val > 0:
                    tfidf[word] = val * Idf[word]
                else:
                    tfidf[word] = 0
            TFIDF_Array[y][0] = titles[y]
            TFIDF_Array[y][1] = sorted(tfidf.items(), key=lambda values: values[1], reverse=True)
            y += 1

    TFMatrix = numpy.empty(shape=(5000, 2), dtype=object)

    for x in range(0, len(bagsOfWords)):
        tfCurrent = TFcomputation(dictionary[x][1], bagsOfWords[x])
        TFMatrix[x][0] = titles[x]
        TFMatrix[x][1] = tfCurrent

    Idf = IDFcomputation(dictionary[:, 1])

    TFIDF_Matrix_Computation(TFMatrix, Idf)

    keywords = []

    for i in range(0, len(TFIDF_Array)):
        words = TFIDF_Array[i][1]
        for j in range(0, 8):
            if len(words[j][0]) > 2:
                if words[j][0] not in stopwords:
                    keywords.append(words[j][0])
                else:
                    j -= 1
            else:
                j -= 1

    # Lista delle 25.000 parole chiave migliori usate per descrivere i 5000 film
    keywords = sorted(list(dict.fromkeys(keywords)))
    keywords.append("love")
    keywords.append("lovestory")
    keywords.append("love story")
    return keywords

