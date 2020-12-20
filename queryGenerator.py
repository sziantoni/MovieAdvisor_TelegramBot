import csv

import inflection
import spacy
import telepot
from gensim.models import Word2Vec
from spellchecker import SpellChecker

spell = SpellChecker(distance=1)
punctuation = set("!@#$%^'&*()_+<>?:.,;")
nlp = spacy.load("en_core_web_sm")
movies_genres = []
bot = telepot.Bot("1040963180:AAGh02okW5n0I3wJf0z9EzK7Xh1uGuwis_0")
stopwords = open("stopwords.txt").read().splitlines()
w2v_model = Word2Vec.load("C:/Users/Stefano/PycharmProjects/botTelegram/venv/word2vec.model")


def defineGenres(w, keywords):
    genres = []
    selected_gnr = []
    gnr_keyword = []
    gnr_score = ''
    c_gnr = 0
    for k in range(0, len(w)):
        doc = nlp(w[k])
        s = ''
        for t in doc:
            s = str(t.lemma_)
        if w[k] in movies_genres and c_gnr < 3 or s in movies_genres:
            if w[k] not in selected_gnr:
                selected_gnr.append(w[k])
                gnr_score = gnr_score + ' ?genre' + str(c_gnr)
                c_gnr += 1
        elif w[k] == 'science' and w[k + 1] == 'fiction' and c_gnr < 3:
            genre_s = w[k] + '.' + w[k + 1]
            if w[k] not in selected_gnr:
                selected_gnr.append(genre_s)
                gnr_score = gnr_score + ' ?genre' + str(c_gnr)
                c_gnr += 1

    for s in selected_gnr:
        if s == 'science.fiction':
            w.remove('science')
            w.remove('fiction')
        else:
            w.remove(s)

    for g in selected_gnr:
        for k in keywords:
            if k[0] == g:
                gnr_keyword.append(k)
            elif g == 'science.fiction' and k[0] == 'science':
                gnr_keyword.append(('science.fiction', k[1]))
                g1 = 'science'
                g2 = 'fiction'
                for i in keywords:
                    if i[0] == g1:
                        keywords.remove(i)
                for i in keywords:
                    if i[0] == g2:
                        keywords.remove(i)

    return w, genres, selected_gnr, gnr_score, gnr_keyword


def defineGenres_subject(w, query_second_part, gnr_score):
    genres = []
    selected_gnr = []
    c_gnr = 0

    for k in gnr_score:
        if len(gnr_score) == 1:
            weight = int(k[1] * 0)
            penalties = -int(k[1] * 150)
        elif len(gnr_score) == 2:
            weight = int(k[1] * 0)
            penalties = -int(k[1] * 120)
        elif len(gnr_score) > 2:
            weight = int(k[1] * 0)
            penalties = -int(k[1] * 100)
        gnr = ' BIND((IF (REGEX(lcase(xsd:string(?list)), "\\\\W' + str(k[0]) + '\\\\W"), ' + str(weight) + \
              ' , ' + str(penalties) + ')) AS ?genre' + str(c_gnr) + '). '
        if k not in selected_gnr:
            genres.append(gnr)
            selected_gnr.append(k)
            c_gnr += 1
            query_second_part = query_second_part + gnr
    return w, genres, selected_gnr, query_second_part


def tfidf_(msg, Idf):
    w = []
    for p in punctuation:
        if p in msg:
            msg = msg.replace(p, " ")
    doc = nlp(msg)
    c = msg.lower().split(' ')
    Nwords = len(c)
    ck = [i[0] for i in Idf]
    for token in doc:
        tk = str(spell.correction(token.text)).lower()
        if tk not in ck:
            new_tk = inflection.singularize(tk)
            if new_tk in ck:
                w.append(new_tk.lower())
            elif str(token.lemma_) in ck:
                w.append(str(token.lemma_))
        else:
            w.append(tk)

    tfidf = {}
    TF = []

    with open('C:/Users/Stefano/PycharmProjects/botTelegram/Testing/genres.csv', 'r') as kw_3:
        csv_reader = csv.reader(kw_3, delimiter=';')
        for row in csv_reader:
            word = row[0].replace(" ", "")
            movies_genres.append(word)
    movies_genres.append('western')

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
    return keywords, w, Nwords, doc, tfidf


def keyword_filter(keywords, Nwords, no_genre, w, genre):
    scorer = ''
    for word in keywords:
        if word[0] in stopwords or len(word[0]) <= 2:
            keywords.remove(word)

    w, genres, selected_genres, gnr_score, gnr_keyword = defineGenres(w, keywords)
    mean = 0
    if len(keywords) >= 1:
        keywords_support = []
        for k in keywords:
            mean += k[1]
        mean = mean / len(keywords)
        for k in keywords:
            d = nlp(k[0])
            flag = True
            for token in d:
                if not token.is_stop:
                    flag = True
                else:
                    flag = False
            if (k[1] >= mean or k[1] > 0.08) and k[0] not in movies_genres and flag:
                keywords_support.append(k)
        keywords = keywords_support
        keywords.sort(key=lambda tup: tup[1], reverse=True)

        if len(keywords) > Nwords / 3 or len(keywords) > 5:
            keywords = keywords[:int(Nwords / 3)]
            if len(keywords) > 5:
                keywords = keywords[:5]

        if no_genre is True and len(keywords) > 3:
            keywords = keywords[:3]

        if len(keywords) == 0:
            if len(selected_genres) > 0:
                if selected_genres[0] != 'science.fiction':
                    keywords.append((selected_genres[0], 0))
                elif len(selected_genres) > 1:
                    keywords.append((selected_genres[1], 0))
                else:
                    keywords.append(('movie', 0))

    return keywords, genre, scorer, selected_genres, gnr_score, gnr_keyword, mean


def top_keyword(keywords, english_dictionary):
    top_kw = []
    remove = []
    support = keywords.copy()
    for s in support:
        if s[0] in movies_genres:
            support.remove(s)

    if support[0][0] in english_dictionary and support[0][0] not in stopwords and support[0][
        0] not in movies_genres and support[0][0] != 'science' and support[0][0] != 'fiction':
        top_kw = support[0]
        remove = top_kw
    elif str(support[0][0][0].upper() + support[0][0][1:len(support[0][0])]) in english_dictionary and \
            support[0][0] not in stopwords and keywords[0][0] not in movies_genres and support[0][0] != 'science' and \
            support[0][0] != 'fiction':
        top_kw = (str(support[0][0][0].upper() + support[0][0][1:len(support[0][0])]), support[0][1])
        remove = support[0]

    if remove:
        keywords.remove(remove)
    else:
        top_kw = ('movie', 0.0)
    return top_kw, keywords


def bigrams(doc, keywords, query_second_part, scorer):
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
                        check = text.split(' ')
                        if len(check) == 2 and 'movie' not in text and 'film' not in text:
                            nounArray.append(text)
    new_noun = ' '
    for noun in nounArray:
        support = str(noun).replace(" ", "_")
        support = support.replace("-", "_")
        new_noun = ' BIND((IF (REGEX(lca' \
                   'se(xsd:string(?abstract)), "' + str(noun) + \
                   '"), 20 , 0)) AS ?' + support + 's). '
        scorer = scorer + '?' + support + 's + '
        query_second_part = query_second_part + new_noun

    return query_second_part, nounArray, scorer


def abstract_keyword(keywords, query_second_part, scorer, mean):
    index = 0
    word_vector = w2v_model.wv
    count = 0
    similar_word = []
    max_number_of_kw = len(keywords)
    for k in keywords:
        penalties = 0
        weight = int(k[1] * 100)
        check = [kw[0] for kw in keywords]
        if k[0] in word_vector.vocab and k[1] > (mean + 0.02):
            similar = w2v_model.wv.most_similar(positive=[k[0]])
        else:
            similar = []
        if len(k[0]) > 2 and k[0] != 'film' and k[0] != 'movie':
            if len(similar) > 0 and similar[0][0] not in similar_word and similar[0][0] != 'film' and similar[0][
                0] != 'movie' and similar[0][0] not in movies_genres and max_number_of_kw < 8 and similar[0][0] \
                    not in check:
                binder = ' BIND((IF (REGEX(lcase(xsd:string(?abstract)), "\\\\W' + k[0] + '\\\\W"), ' + str(
                    weight) + ' , ' + str(penalties) + ')) AS ?' + k[
                             0].replace(
                    "-", "") + '). '
                binder_similar = ' BIND((IF (REGEX(lcase(xsd:string(?abstract)), "\\\\W' + similar[0][
                    0] + '\\\\W"), ' + str(int(weight / 2)) + ' , ' + str(penalties) + ')) AS ?' + similar[
                                     0][0].replace(
                    "-", "") + '). '
                query_second_part = query_second_part + binder + binder_similar
                similar_word.append(similar[0][0])
                max_number_of_kw += 1
                if count == len(keywords) - 1:
                    scorer = scorer + '?' + k[0].replace("-", "") + '+ ?' + similar[0][0].replace('-', "")
                else:
                    scorer = scorer + '?' + k[0].replace("-", "") + ' + ?' + similar[0][0].replace('-', "") + '+'
                count += 1
            else:
                binder = ' BIND((IF (REGEX(lcase(xsd:string(?abstract)), "\\\\W' + k[
                    0].replace("-", "\\\\W") + '\\\\W"), ' + str(weight) + ' , ' + str(penalties) + ')) AS ?' + k[
                             0].replace(
                    "-", "") + '). '
                query_second_part = query_second_part + binder
                if count == len(keywords) - 1:
                    scorer = scorer + '?' + k[0].replace("-", "")
                else:
                    scorer = scorer + '?' + k[0].replace("-", "") + ' + '
                count += 1
        elif len(k[0]) <= 2:
            count += 1
        index += 1
    return query_second_part, scorer


def subject_keyword(keywords, query_second_part):
    s1 = 1
    final_score = ''
    index = 0
    count = 0

    for k in keywords:
        weight = int(k[1] * 170)
        binder = ' BIND((IF  (regex(lcase(xsd:string(?list)), "\\\\W' + k[
            0].replace('-', '\\\\W') + '\\\\W"),  ' + str(weight) + ' , 0)) AS ?special' + str(
            s1) + ' ).  '
        query_second_part = query_second_part + binder
        if count == (len(keywords) - 1):
            final_score = final_score + '?special' + str(s1)
        else:
            final_score = final_score + '?special' + str(s1) + ' + '
        s1 += 1
        index += 1
        count += 1

    checker = ' BIND((IF  (regex(xsd:string(?list), "short film"),  -100 , 0)) AS ?optional1 ).  '
    checker1 = ' BIND((IF  (regex(xsd:string(?list), "short movie"),  -100 , 0)) AS ?optional2 ).  '
    checker2 = ' BIND((IF  (regex(xsd:string(?abstract), "short film"),  -100 , 0)) AS ?optional3 ).  '
    checker3 = ' BIND((IF  (regex(xsd:string(?abstract), "short movie"),  -100 , 0)) AS ?optional4 ).  '
    checker4 = ' BIND((IF  (regex(xsd:string(?abstract), "Allah Made Me Funny"),  -100 , 0)) AS ?optional5 ).  '
    query_second_part = query_second_part + checker + checker1 + checker2 + checker3 + checker4
    return query_second_part, final_score


def queryConstructor(msg, Idf, language, year, no_genre, limit, english_dictionary):
    too_much = False
    genre = ''
    keywords, w, Nwords, doc, tfidf = tfidf_(msg, Idf)

    top_kw, keywords = top_keyword(keywords, english_dictionary)

    keywords, genre, scorer, selected_genres, gnr_score, kw_gnr, mean = keyword_filter(keywords, Nwords, no_genre, w,
                                                                                       genre)

    if len(keywords) >= 1:
        query_second_part = ''

        query_second_part, nounArray, scorer = bigrams(doc, keywords, query_second_part, scorer)

        query_second_part, scorer = abstract_keyword(keywords, query_second_part, scorer, mean)

        query_first_part = ' PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> ' \
                           ' PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> ' \
                           ' PREFIX dct:<http://purl.org/dc/terms/> ' \
                           ' PREFIX dbo:<http://dbpedia.org/ontology/> ' \
                           ' PREFIX dbpprop:<http://dbpedia.org/property/> ' \
                           ' PREFIX dbc:<http://dbpedia.org/resource/Category/movie:> ' \
                           ' SELECT DISTINCT  ?top_kw ?score ?id ?movie ?movie_title ?year1 ?abstract ?link ?list WHERE{ ' \
                           ' { SELECT DISTINCT  ?score1 ?top_kw ?id ?movie ?movie_title ?year1 ?abstract ?link (group_concat(distinct ?subj1; separator = " ") as ?list) ' \
                           ' FROM <http://dbpedia.org>  WHERE{ ' \
                           ' ?movie dbo:wikiPageID ?id. ' \
                           ' ?movie rdf:type dbo:Film. ' \
                           ' ?movie rdfs:label ?movie_title ' \
                           ' FILTER langMatches(lang(?movie_title), "EN"). ' \
                           ' ?movie dbp:country ?country FILTER CONTAINS(xsd:string(?country), "' + str(
            language) + '").' \
                        ' ?movie foaf:isPrimaryTopicOf ?link  . ' \
                        ' ?movie dbo:abstract ?abstract  FILTER langMatches(lang(?abstract), "EN") . ' \
                        ' BIND((IF (REGEX(xsd:string(?abstract), ".' + top_kw[0] + '."), ' \
                           + str(int(top_kw[1] * 70)) + ' , -' + str(int(top_kw[1] * 70)) + ')) AS ?top_kw). ' \
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
            query_second_part = query_second_part + '  BIND(( ' + scorer + ' + ?top_kw) as ?score1).  }} '
        else:
            query_second_part = query_second_part + '  BIND(( 0 as ?score1).  }} '

        query_second_part, final_score = subject_keyword(keywords, query_second_part)

        w, genres, selected_gnr, query_second_part = defineGenres_subject(w, query_second_part, kw_gnr)
        query_second_part = query_second_part
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
            final_query = query_second_part + ' BIND((?score1 + ' + final_score + ' ) as ?score).  }ORDER BY desc(?score) desc(?year1) limit ' + limit + ' '
    else:
        final_query = ''
    return final_query, too_much, keywords
