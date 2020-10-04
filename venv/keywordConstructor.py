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
prohibited = ['film', 'movie', 'fims', 'movies']
nlp = spacy.load("en_core_web_sm")

def keywordGenerator(db, db_len):
    keyword_1 = open('kw1.csv', 'w', newline='')
    keyword_2 = open('kw2.csv', 'w', newline='')
    keyword_3 = open('kw3.csv', 'w', newline='')
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
        for word in bagsOfWords[y][1]:
                numOfWords[word] += 1
        dictionary[y,:]= [*numOfWords.values()]
        y += 1

    print('Dizionario fatto!')
    # TF
    def TFcomputation(bag, dictionary):
        TFcount = dict.fromkeys(bag[1], 0)
        if len(bag[1]) > 0:
            for i in range(0, len(uniqueWords)):
                if dictionary[i] > 0.0:
                    TFcount[uniqueWords[i]] = dictionary[i]/ len(bag[1])
        return TFcount

    # IDF
    def IDFcomputation():
        import math
        NDocs = len(titles)
        idfDict = dict.fromkeys(uniqueWords, 0)
        for i in range(0, len(uniqueWords)-1):
            current = dictionary[:,i]
            for x in current:
                if x > 0:
                    idfDict[uniqueWords[i]] += 1
        for word, val in idfDict.items():
            if val > 0:
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
            tfCurrent = TFcomputation(bagsOfWords[x], dictionary[x])
            TFMatrix[x][0] = titles[x]
            TFMatrix[x][1] = tfCurrent
    print('TF fatto!')
    Idf = IDFcomputation()
    print('IDF fatto!')
    del dictionary
    TFIDF_Matrix_Computation(TFMatrix, Idf)
    print('TFIDF fatto!')
    del TFMatrix, Idf
    keywords_general = []
    keywords_first = []
    keywords_second = []
    #RIVEDERE QUESTA PARTE
    writer1 = csv.writer(keyword_1, delimiter=';')
    writer2 = csv.writer(keyword_2, delimiter=';')
    writer3 = csv.writer(keyword_3, delimiter=';')
    for i in range(0, len(TFIDF_Array)):
        words = TFIDF_Array[i][1]
        for j in range(0, len(words)-1):
            if len(words[j][0]) > 3:
                if words[j][0] not in stopwords and words[j][0] not in prohibited:
                    if  words[j][1] > 0.42 and words[j] not in keywords_first and words[j] not in keywords_second and str(words[j][0]) not in keywords_general :
                            keywords_first.append(words[j])
                            writer1.writerow([words[j][0], words[j][1]])
                    elif  words[j][1] > 0.35  and words[j][1] < 0.42 and words[j] not in keywords_first and words[j] not in keywords_second and str(words[j][0]) not in keywords_general:
                            keywords_second.append(words[j])
                            writer2.writerow([words[j][0], words[j][1]])
                    elif words[j][1] > 0.3 and words[j] not in keywords_first and words[j] not in keywords_second and words[j][0] not in keywords_general:
                            keywords_general.append(words[j][0])
                            writer3.writerow([words[j][0]])


    # Lista delle 25.000 parole chiave migliori usate per descrivere i 5000 film
    keywords_first = sorted(keywords_first, key=lambda values: values[1], reverse=True)
    keywords_second = sorted(keywords_second, key=lambda values: values[1], reverse=True)
    seconds1 = time.time()
    keyword_1.close()
    keyword_2.close()
    keyword_3.close()
    print("Seconds since epoch =", seconds1-seconds)
    return keywords_first, keywords_second, keywords_general

