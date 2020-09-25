import numpy
import time
import urllib.error
import urllib.request
from pprint import pprint
import pandas as pd
import spacy

stopwords = open("stopwords.txt").read().splitlines()
whitelist = set('abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 -')
prohibited = ['film', 'movie']
nlp = spacy.load("en_core_web_sm")

def keywordGenerator(db, db_len):
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
    print('Unique word fatto!')
    dictionary = numpy.empty(shape=(db_len, 2), dtype=object)

    y = 0
    for x in range(0, len(bagsOfWords)):
        numOfWords = dict.fromkeys(uniqueWords, 0)
        for word in bagsOfWords[y][1]:
                numOfWords[word] += 1
        dictionary[y][0] = titles[y]
        dictionary[y][1] = numOfWords
        y += 1

    # calcolo di tf-idf
    print('Dizionario fatto!')
    # TF
    def TFcomputation(words, bag):
        TFcount = {}
        bagCount = len(bag)
        if len(bag) > 0:
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

    TFIDF_Array = numpy.empty(shape=(db_len, 2), dtype=object)

    # TF-IDF
    def TFIDF_Matrix_Computation(TFMatrix, Idf):
        y = 0
        for i in TFMatrix[:, 1]:
            tfidf = {}
            for word, val in i.items():
                if val > 0 and len(word)>2:
                    tfidf[word] = val * Idf[word]
            TFIDF_Array[y][0] = titles[y]
            TFIDF_Array[y][1] = sorted(tfidf.items(), key=lambda values: values[1], reverse=True)
            y += 1

    TFMatrix = numpy.empty(shape=(db_len, 2), dtype=object)

    for x in range(0, len(bagsOfWords)):
        if bagsOfWords[x][1] != None:
            tfCurrent = TFcomputation(dictionary[x][1], bagsOfWords[x])
            TFMatrix[x][0] = titles[x]
            TFMatrix[x][1] = tfCurrent
    print('TF fatto!')
    Idf = IDFcomputation(dictionary[:, 1])
    print('IDF fatto!')
    del dictionary
    TFIDF_Matrix_Computation(TFMatrix, Idf)
    print('TFIDF fatto!')
    del TFMatrix, Idf
    keywords_general = []
    keywords_first = []
    keywords_second = []
    for i in range(0, len(TFIDF_Array)):
        words = TFIDF_Array[i][1]
        limit = 0
        if len(words) > 10:
            limit = 8
        elif len(words) > 4:
            limit = len(words) - 3
        else:
            limit = len(words)
        for j in range(0, limit):
            if len(words[j][0]) > 3:
                if words[j][0] not in stopwords and words[j][0] not in prohibited:
                    if ("ing" not in str(words[j][0])) and  words[j][1] > 4.5 and words[j] not in keywords_first and words[j] not in keywords_second and str(words[j][0]) not in keywords_general :
                            keywords_first.append(words[j])
                    elif "ing" not in str(words[j][0]) and words[j][1] > 3.7  and words[j][1] < 4.5 and words[j] not in keywords_first and words[j] not in keywords_second and str(words[j][0]) not in keywords_general:
                            keywords_second.append(words[j])
                    elif words[j][1] > 2 and words[j] not in keywords_first and words[j] not in keywords_second and words[j][0] not in keywords_general:
                            keywords_general.append(words[j][0])
                    else:
                        j -= 1
                else:
                    j -= 1
            else:
                j -= 1

    # Lista delle 25.000 parole chiave migliori usate per descrivere i 5000 film
    keywords_first.append(("love", 7.0))
    keywords_second.append("lovestory")
    keywords_general.append("love story")
    return keywords_first, keywords_second, keywords_general

