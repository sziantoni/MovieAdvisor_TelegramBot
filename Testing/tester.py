import csv
import numpy
import spacy
import telepot
import pattern.text.en as plur
from spellchecker import SpellChecker
import re

spell = SpellChecker(distance=1)
punctuation = set("!@#$%^'&*()_+<>?:.,;")
nlp = spacy.load("en_core_web_sm")
movies_genres = []
bot = telepot.Bot("1040963180:AAGh02okW5n0I3wJf0z9EzK7Xh1uGuwis_0")
stopwords = open("../stopwords.txt").read().splitlines()


def queryConstructor(msg, Idf, language, year, no_genre, limit):
    too_much = False
    doc = nlp(msg)
    genre = ''

    for token in doc:
        if str(token.text) != str(token.lemma_) and '-' not in str(token.lemma_) and len(str(token.text)) > 6:
            msg = msg + ', ' + str(token.lemma_)

    for p in punctuation:
        if p in msg:
            msg = msg.replace(p, "")
    w = msg.lower().split(' ')
    Nwords = len(w)
    tfidf = {}
    TF = []
    plurals = []

    for k in w:
        if len(k) > 6:
            plural = plur.pluralize(k)
            if plural not in w and plural not in plurals:
                if plural[-2:] != 'ss':
                    plurals.append(plural)
    w = w + plurals

    with open('../genres.csv', 'r') as kw_3:
        csv_reader = csv.reader(kw_3, delimiter=';')
        for row in csv_reader:
            word = row[0].replace(" ", "")
            movies_genres.append(word)
    movies_genres.append('western')
    misspelled = spell.unknown(w)

    for m in misspelled:
        w.remove(m)
        w.append(spell.correction(m))

    genres = []
    selected_gnr = []
    c_gnr = 0
    uniqueWords = list(dict.fromkeys(w))
    dictionary = []
    for u in uniqueWords:
        counter = w.count(u)
        if counter != 0:
            dictionary.append((u, counter))

    for j in dictionary:
        value = j[1] / Nwords
        TF.append((j[0], value))
    kw_mean = 0
    for j in Idf:
        if j[0] in [item[0] for item in TF]:
            for i in TF:
                if i is not None and i[0] == j[0]:
                    if i[1] > 0 and len(i[0]) > 2:
                        tfidf[i[0]] = float(i[1]) * float(j[1])
                        kw_mean += float(i[1]) * float(j[1])

    keywords = sorted(tfidf.items(), key=lambda values: values[1], reverse=True)
    for word in [item for item in keywords]:
        if word[0] in stopwords or len(word[0]) <= 3:
            keywords.remove(word)

    for k in range(0, len(w) - 1):
        if w[k] in movies_genres:
            if w[k] == 'race':
                w[k] = w[k] + 'r'
            gnr = ' BIND((IF (REGEX(lcase(xsd:string(?abstract)), "^(?=.*' + w[
                k] + ').*$"), 20 , -20)) AS ?genre' + str(c_gnr) + '). '
            if w[k] not in selected_gnr:
                genres.append(gnr)
                selected_gnr.append(w[k])
                c_gnr += 1
    for h in range(0, len(genres)):
        if h == len(genres) - 1:
            genre = genre + genres[h]
        else:
            genre = genre + genres[h]
    if len(keywords) > 2:
        if genre == '':
            genre = ' BIND((IF (REGEX(lcase(xsd:string(?abstract)), "^(?=.*film).*$"), 20 , -20)) as ?genre0). '
            genres.append('film')
        scorer = ''
        for g in range(0, len(genres)):
            scorer = scorer + '?genre' + str(g) + ' + '

        keywords_support = []
        for k in keywords:
            if k[1] >= 0.05 and k[0] != 'american' and k[0] != 'americans':
                keywords_support.append(k)

        keywords = keywords_support
        keywords.sort(key=lambda tup: tup[1], reverse=True)

        if len(keywords) > 7:
            keywords = keywords[:7]

        if no_genre is True and len(keywords) > 3:
            keywords = keywords[:3]

        nounArray = []

        for chunk in doc.noun_chunks:
            text = chunk.text.lower()

            for key in [item[0] for item in keywords]:

                if key in text:

                    if text[0] == 'a' and text[1] == 'n' and text[2] == ' ':
                        text = text[3:]
                    if text[0] == 'a' and text[1] == ' ':
                        text = text[2:]
                    if text[0] == 't' and text[1] == 'h' and text[2] == 'e' and text[3] == ' ':
                        text = text[4:]
                    if len(text) - len(key) > 2:

                        if text not in nounArray:
                            text = str(text).replace(",", "")
                            if text[0] == ' ':
                                text = text[:1]
                            nounArray.append(text)
        query_second_part = ''
        count = 0
        tester = ''
        tester1 = ''
        for noun in nounArray:
            support = str(noun).replace(" ", "_")
            support = support.replace("-", "_")
            nouner = ' BIND((IF (REGEX(xsd:string(?abstract), "' + str(
                noun) + '"), 15 , -5)) AS ?' + support + 's). '
            scorer = scorer + '?' + support + 's + '
            tester = tester + ' ?' + support + 's '
            tester1 = tester1 + ' ?' + support + 's '
            query_second_part = query_second_part + nouner
        tester_counter = 1
        print('-----------------------------------------------------------------------------------------------\n')
        for k in keywords:
            print(k)
            penalties = '0'
            if float(k[1]) > 0.20:
                weight = '30'
            elif float(k[1]) > 0.18:
                weight = '25'
            elif float(k[1]) > 0.16:
                weight = '20'
            elif float(k[1]) > 0.14:
                weight = '10'
            elif float(k[1]) > 0.10:
                weight = '5'
            elif float(k[1]) > 0.08:
                weight = '3'
            elif float(k[1]) > 0.06:
                weight = '2'
            else:
                weight = '1'
            if len(k[0]) > 2 and k[0] != 'film' and k[0] != 'movie':
                binder = ' BIND((IF (REGEX(lcase(xsd:string(?abstract)), "^(?=.* ' + k[
                    0] + ' ).*$"), ' + weight + ' , ' + penalties + ')) AS ?' + k[0].replace(
                    "-", "") + '). '
                query_second_part = query_second_part + binder
                tester = tester + '?' + k[0].replace("-", "") + ' '
                tester1 = tester1 + '?' + k[0].replace("-", "") + ' ?special' + str(tester_counter) + ' '
                tester_counter += 1
                if count == len(keywords) - 1:
                    scorer = scorer + '?' + k[0].replace("-", "")
                else:
                    scorer = scorer + '?' + k[0].replace("-", "") + ' + '
                count += 1
            elif len(k[0]) <= 2:
                count += 1

        query_first_part = ' PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> ' \
                           ' PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> ' \
                           ' PREFIX dct:<http://purl.org/dc/terms/> ' \
                           ' PREFIX dbo:<http://dbpedia.org/ontology/> ' \
                           ' PREFIX dbpprop:<http://dbpedia.org/property/> ' \
                           ' PREFIX dbc:<http://dbpedia.org/resource/Category/movie:> ' \
                           ' SELECT DISTINCT ?score  ?id ?movie ?movie_title ?year1 ?abstract ?link ?list ?genre0 ' + tester1 + '  WHERE{ ' \
                           ' { SELECT DISTINCT ?score1  ?id ?movie ?movie_title ?year1 ?abstract ?link (group_concat(distinct ?subj1; separator = " ") as ?list) ?genre0 ' + tester + \
                           ' FROM <http://dbpedia.org>  WHERE{ ' \
                           ' ?movie dbo:wikiPageID ?id. ' \
                           ' ?movie rdf:type dbo:Film. ' \
                           ' ?movie rdfs:label ?movie_title ' \
                           ' FILTER langMatches(lang(?movie_title), "EN"). ' \
                           ' ?movie dbp:country ?country FILTER CONTAINS(xsd:string(?country), "' + str(
            language) + '").' \
                        ' ?movie foaf:isPrimaryTopicOf ?link  . ' \
                        ' ?movie dbo:abstract ?abstract  FILTER langMatches(lang(?abstract), "EN") ' \
                           + genre + \
                           ' ?movie  dct:subject ?subject. ' \
                           ' ?subject rdfs:label ?year. ' \
                           ' filter regex(?year, "\\\\d{4}.films"). ' \
                           ' BIND(REPLACE(xsd:string(?year), "[^\\\\b0-9\\\\b]", "") AS ?movie_year2) ' \
                           ' BIND(SUBSTR(str(?movie_year2), 0, 4) AS ?year1)  FILTER(xsd:integer(?year1) > ' + year + ') ' \
                                                                                                                      ' ?movie dct:subject ?subject1. ' \
                                                                                                                      ' ?subject1 rdfs:label ?subj1 '
        query_second_part = query_first_part + query_second_part

        if scorer != ' ':
            if scorer[len(scorer) - 2] == '+':
                scorer = scorer[:-2] + ' '
            query_second_part = query_second_part + '  BIND(( ' + scorer + ') as ?score1).  }} '
        else:
            query_second_part = query_second_part + '  BIND(( 0 as ?score1).  }} '

        s1 = 1
        final_score = ''

        count = 0
        for k in keywords:
            penalties = '0'
            if float(k[1]) > 0.20:
                weight = '30'
            elif float(k[1]) > 0.18:
                weight = '25'
            elif float(k[1]) > 0.16:
                weight = '20'
            elif float(k[1]) > 0.14:
                weight = '10'
            elif float(k[1]) > 0.10:
                weight = '5'
            elif float(k[1]) > 0.08:
                weight = '3'
            elif float(k[1]) > 0.06:
                weight = '2'
            else:
                weight = '1'
            binder = ' BIND((IF  (regex(lcase(xsd:string(?list)), "^(?=.* ' + k[
                0] + ' ).*$"),  ' + weight + ' , ' + penalties + ')) AS ?special' + str(
                s1) + ' ).  '
            query_second_part = query_second_part + binder
            if count == (len(keywords) - 1):
                final_score = final_score + '?special' + str(s1)
            else:
                final_score = final_score + '?special' + str(s1) + ' + '
            s1 += 1
            count += 1
        checker = ' BIND((IF  (regex(xsd:string(?list), "short film"),  -100 , 0)) AS ?optional1 ).  '
        checker1 = ' BIND((IF  (regex(xsd:string(?list), "short movie"),  -100 , 0)) AS ?optional2 ).  '
        checker2 = ' BIND((IF  (regex(xsd:string(?abstract), "short film"),  -100 , 0)) AS ?optional3 ).  '
        checker3 = ' BIND((IF  (regex(xsd:string(?abstract), "short movie"),  -100 , 0)) AS ?optional4 ).  '
        checker4 = ' BIND((IF  (regex(xsd:string(?abstract), "Allah Made Me Funny"),  -100 , 0)) AS ?optional5 ).  '
        query_second_part = query_second_part + checker + checker1 + checker2 + checker3 + checker4

        genres = []
        selected_gnr = []
        c_gnr = 0

        for k in range(0, len(w) - 1):
            if w[k] in movies_genres:
                if w[k] == 'race':
                    w[k] = w[k] + 'r'
                gnr = ' BIND((IF (REGEX(lcase(xsd:string(?list)), "^(?=.*' + w[
                    k] + ').*$"), 20 , -20)) AS ?genre' + str(c_gnr) + '). '
                if w[k] not in selected_gnr:
                    genres.append(gnr)
                    selected_gnr.append(w[k])
                    c_gnr += 1
                    query_second_part = query_second_part + gnr
        scorer = ''
        for g in range(0, len(genres)):
            scorer = scorer + '?genre' + str(g) + ' + '

        final_score = scorer + final_score

        if final_score == '':
            final_query = query_second_part + ' BIND((?score1 ) as ?score).  }ORDER BY desc(?score) desc(?year1) limit 5 '
        else:
            if final_score[len(final_score) - 2] == '+':
                final_score = final_score[:-2] + ' '
            final_score = ' ?optional1 + ?optional2 + ?optional3 + ?optional4 + ?optional5 + ' + final_score
            final_query = query_second_part + ' BIND((?score1 + ' + final_score + ') as ?score).  }ORDER BY desc(?score) desc(?year1) limit ' + limit + ' '
    else:
        final_query = ''
    return final_query, too_much, tester1, keywords
