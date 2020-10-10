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
            ciao = 1
            for x in current:
                if x != None:
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
            if i != None:
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
    keyword_1 = open('kw1.csv', 'w', newline='')
    keyword_2 = open('kw2.csv', 'w', newline='')
    keyword_3 = open('kw3.csv', 'w', newline='')
    writer1 = csv.writer(keyword_1, delimiter=';')
    writer2 = csv.writer(keyword_2, delimiter=';')
    writer3 = csv.writer(keyword_3, delimiter=';')
    writer6 = csv.writer(keyword_6, delimiter=';')
    keywords_first, keywords_second, keywords_general = [], [], []

    for u in uniqueWords:
        current = 0
        min = 0
        max = 0
        accumulator = 0
        count = 0
        controller = False
        for p in prohibited:
            if p in u:
                controller= True
        if controller == False:
            for i in range(0, len(TFIDF_Array) - 1):
                words = TFIDF_Array[i][1]
                if words != None:
                    for word in words:
                        if word[0] == u:
                            accumulator += word[1]
                            count += 1
                            current = word[1]
                            if current < min or min == 0:
                                min = current
                            if current > max:
                                max = current
            if min != 0 and max != 0 and count!= 0:
                tot = accumulator / count
                value = 0
                if max == min == tot:
                    value = (max)/1.5
                else:
                    value = (max + min + tot)/2
                writer6.writerow([u,min,max,tot,value])
                if value > 0.39 and len(u) > 3 :
                    keywords_first.append((u, value))
                if value > 0.27 and value < 0.39 and len(u) > 3:
                    keywords_second.append((u, value))
                if value > 0.23 and value < 0.27 and len(u) > 3:
                    keywords_general.append(u)

    keyword_6.close()

    for k in keywords_first:
        writer1.writerow([k[0], k[1]])
    for i in keywords_second:
        writer2.writerow([i[0], i[1]])
    for j in keywords_general:
        writer3.writerow([j])
    print("Keyword Scritte")
    keyword_1.close()
    keyword_2.close()
    keyword_3.close()
    print("Keyword Inserite")

    return keywords_first, keywords_second, keywords_general



