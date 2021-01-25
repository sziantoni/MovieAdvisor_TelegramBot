import csv
import nltk
import spacy
import telepot
import inflection
from gensim.models import Word2Vec
from sklearn.feature_extraction.text import CountVectorizer
from spellchecker import SpellChecker
from spacy.lang.en.stop_words import STOP_WORDS

nltk.download('words')
spell = SpellChecker(distance=1)
nlp = spacy.load("en_core_web_sm")
movies_genres = []
bot = telepot.Bot("1040963180:AAGh02okW5n0I3wJf0z9EzK7Xh1uGuwis_0")
stopwords = set(STOP_WORDS)
w2v_model = Word2Vec.load("C:/Users/Stefano/PycharmProjects/botTelegram/venv/word2vec.model")
with open('C:/Users/Stefano/PycharmProjects/botTelegram/Testing/genres.csv', 'r') as kw_3:
    csv_reader = csv.reader(kw_3, delimiter=';')
    index = 0
    for row in csv_reader:
        if index > 0:
            word = row[0].replace(" ", "")
            movies_genres.append(word)
        index += 1


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
        if (w[k] in movies_genres or s in movies_genres) and c_gnr < 3:
            if w[k] not in selected_gnr and s not in selected_gnr:
                if s in movies_genres and w[k] not in movies_genres:
                    selected_gnr.append(s)
                else:
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
            if s in w:
                w.remove(s)
            elif s + 's' in w:
                w.remove(s + 's')

    for g in selected_gnr:
        for k in keywords:
            d = nlp(k[0])
            lem = ''
            for t in d:
                lem = t.lemma_
            if k[0] == g:
                gnr_keyword.append(k)
            elif lem == g:
                gnr_keyword.append((lem, k[1]))
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
    penalties = 0
    weight = 0
    for k in gnr_score:
        if len(gnr_score) == 1:
            weight = int(k[1] * 0)
            penalties = -int(k[1] * 130)
        elif len(gnr_score) == 2:
            weight = int(k[1] * 0)
            penalties = -int(k[1] * 90)
        elif len(gnr_score) > 2:
            weight = int(k[1] * 0)
            penalties = -int(k[1] * 70)

        gnr = ' BIND((IF (REGEX(xsd:string(?list), "[^a-zA-Z0-9]' + str(k[0]) + '[^a-zA-Z0-9]", "i"), ' + str(weight) + ' , ' + str(penalties) + ')) AS ?genre' + str(c_gnr) + '). '
        c_gnr += 1
        gnr = gnr + ' BIND((IF (REGEX(xsd:string(?abstract), "[^a-zA-Z0-9]' + str(k[0]) + '[^a-zA-Z0-9]", "i"), ' + str(weight) + ' , ' + str(penalties) + ')) AS ?genre' + str(c_gnr) + '). '

        if k not in selected_gnr:
            genres.append(gnr)
            selected_gnr.append(k)
            c_gnr += 1
            query_second_part = query_second_part + gnr
    return w, genres, selected_gnr, query_second_part


def tfidf_(msg, Idf):
    vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 1), token_pattern=r'[A-Za-z]*-?[A-Za-z]*',
                                 stop_words=None, lowercase=True)
    analyzer = vectorizer.build_analyzer()
    text = str(msg)
    doc = nlp(msg)
    plot = analyzer(text)
    Nwords = len(doc)
    plot = [i for i in plot if i != '' and len(i) > 2]
    w = []
    ck = [i[0] for i in Idf]
    for token in plot:
        tk = str(spell.correction(token)).lower()
        if tk not in ck:
            new_tk = inflection.singularize(tk)
            if new_tk in ck:
                w.append(new_tk.lower())
            elif str(token) in ck:
                w.append(str(token))
        else:
            w.append(tk)

    tfidf = {}
    TF = []

    uniqueWords = list(dict.fromkeys(w))
    dictionary = []

    for u in uniqueWords:
        counter = w.count(u)
        if counter != 0:
            dictionary.append((u, counter))

    for j in dictionary:
        value = j[1] / Nwords
        TF.append((j[0], value))

    for j in Idf:
        if j[0] in [item[0] for item in TF]:
            for i in TF:
                if i is not None and i[0] == j[0]:
                    if i[1] > 0 and len(i[0]) > 2:
                        tfidf[i[0]] = float(i[1]) * float(j[1])

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
        flag = False

        for k in keywords:
            mean += k[1]
        mean = mean / len(keywords)
        for k in keywords:
            d = nlp(k[0])
            if ((k[1] >= mean and k[1] > 0.05) or k[1] > 0.08) and k[0] not in movies_genres:
                for t in d:
                    if t.lemma_ in movies_genres:
                        flag = True
                    else:
                        flag = False
                if flag is False:
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


def top_keyword(keywords):
    top_kw = []
    remove = []
    support = keywords.copy()
    word_vector = w2v_model.wv
    for s in support:
        if s[0] in movies_genres:
            support.remove(s)

    if support[0][0] not in stopwords and support[0][
        0] not in movies_genres and support[0][0] != 'science' and support[0][0] != 'fiction':
        top_kw = support[0]
        remove = top_kw
    elif support[0][0] not in stopwords and keywords[0][0] not in movies_genres and support[0][0] != 'science' and \
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
    words = [item[0] for item in keywords]

    for chunk in doc.noun_chunks:
        is_valid = False
        lenght = chunk.text.replace("  ", " ").split(' ')
        if len(lenght) == 2:
            if lenght[0] not in STOP_WORDS:
                if lenght[0] in words:
                    words.remove(lenght[0])
                    to_remove = [item for item in keywords if item[0] == lenght[0]]
                    keywords.remove(to_remove[0])
                    is_valid = True
                if lenght[1] in words:
                    words.remove(lenght[1])
                    to_remove = [item for item in keywords if item[0] == lenght[1]]
                    keywords.remove(to_remove[0])
                    is_valid = True
            if is_valid :
                nounArray.append(chunk.text)
        elif len(lenght) > 2:
            lenght = lenght[-2:]
            if lenght[0] not in STOP_WORDS:
                txt = lenght[0] + ' ' + lenght[1]
                if lenght[0] not in STOP_WORDS:
                    if lenght[0] in words:
                        words.remove(lenght[0])
                        to_remove = [item for item in keywords if item[0] == lenght[0]]
                        keywords.remove(to_remove[0])
                        is_valid = True
                    if lenght[1] in words:
                        words.remove(lenght[1])
                        to_remove = [item for item in keywords if item[0] == lenght[1]]
                        keywords.remove(to_remove[0])
                        is_valid = True
                    if is_valid:
                        nounArray.append(txt)
    n = ''
    for noun in nounArray:
        support = str(noun).replace(" ", "_")
        support = support.replace("-", "_")
        n = n + ' BIND((IF (REGEX(xsd:string(?abstract), "[^a-zA-Z0-9]' + str(
            noun).replace(" ", ".") + '[^a-zA-Z0-9]", "i"), 20 , 0)) AS ?' + support + 's). '
        scorer = scorer + '?' + support + 's + '

    query_second_part = query_second_part + n

    return query_second_part, nounArray, scorer, keywords


def abstract_keyword(keywords, query_second_part, scorer,  mean):

    word_vector = w2v_model.wv
    count = 0
    similar_word = []
    max_number_of_kw = len(keywords)

    for k in keywords:
        weight = int(k[1] * 100)
        penalties = 0
        check = [kw[0] for kw in keywords]
        if k[0] in word_vector.vocab and k[1] > (mean + 0.05):
            similar = w2v_model.wv.most_similar(positive=[k[0]])
        else:
            similar = []
        if len(k[0]) > 2 :
            if len(similar) > 0 and similar[0][0] not in similar_word and similar[0][0] != 'film' and similar[0][0] != 'movie' and similar[0][0] not in movies_genres and max_number_of_kw < 8 and similar[0][0] not in check:

                binder = ' BIND((IF (REGEX(xsd:string(?abstract), "[^a-zA-Z0-9]' + k[0] + '[^a-zA-Z0-9]", "i"), ' + str(weight) + ' , -' + str(penalties) + ')) AS ?' + k[0].replace("-", "") + '). '

                binder_similar = ' BIND((IF (REGEX(xsd:string(?abstract), "[^a-zA-Z0-9]' + similar[0][0] + '[^a-zA-Z0-9]", "i"), -' + str(int(weight / 2)) + ' , ' + str(penalties) + ')) AS ?' + similar[0][0].replace("-", "") + '). '

                query_second_part = query_second_part + binder + binder_similar
                similar_word.append(similar[0][0])
                max_number_of_kw += 1

                if count == len(keywords) - 1:
                    scorer = scorer + '?' + k[0].replace("-", "") + '+ ?' + similar[0][0].replace('-', "")
                else:
                    scorer = scorer + '?' + k[0].replace("-", "") + ' + ?' + similar[0][0].replace('-', "") + '+'
                count += 1
            else:
                binder = ' BIND((IF (REGEX(xsd:string(?abstract), "[^a-zA-Z0-9]' + k[0].replace("-", ".") + '[^a-zA-Z0-9]", "i"), ' + str(weight) + ' , -' + str(penalties) + ')) AS ?' + k[0].replace("-", "") + '). '

                query_second_part = query_second_part + binder

                if count == len(keywords) - 1:
                    scorer = scorer + '?' + k[0].replace("-", "")
                else:
                    scorer = scorer + '?' + k[0].replace("-", "") + ' + '
                count += 1

        elif len(k[0]) <= 2:
            count += 1

    return query_second_part, scorer


def subject_keyword(keywords, query_second_part):
    s1 = 1
    final_score = ''
    count = 0

    for k in keywords:
        weight = int(k[1] * 170)
        binder = ' BIND((IF  (regex(xsd:string(?list), "[^a-zA-Z0-9]' + k[0].replace('-', '.') + '[^a-zA-Z0-9]", "i"),  ' + str(weight) + ' , 0)) AS ?special' + str(s1) + ' ).  '

        query_second_part = query_second_part + binder
        if count == (len(keywords) - 1):
            final_score = final_score + '?special' + str(s1)
        else:
            final_score = final_score + '?special' + str(s1) + ' + '
        s1 += 1
        count += 1

    query_second_part = query_second_part
    return query_second_part, final_score


def queryConstructor(msg, Idf, language, year, no_genre, limit):
    too_much = False
    genre = ''
    keywords, w, Nwords, doc, tfidf = tfidf_(msg, Idf)

    top_kw, keywords = top_keyword(keywords)

    keywords, genre, scorer, selected_genres, gnr_score, kw_gnr, mean = keyword_filter(keywords, Nwords, no_genre, w, genre)

    if len(keywords) >= 1:
        query_second_part = ''

        query_second_part, nounArray, scorer, keywords = bigrams(doc, keywords, query_second_part,scorer)

        query_second_part, scorer = abstract_keyword(keywords, query_second_part, scorer, mean)

        query_first_part = ' PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>' \
                           ' PREFIX dct:<http://purl.org/dc/terms/>   ' \
                           ' PREFIX dbo:<http://dbpedia.org/ontology/>  ' \
                           ' SELECT DISTINCT  ?score ?movie_title ?list ?top_kw  ?link  ?abstract ' \
                           ' WHERE{' \
                           ' {' \
                           ' SELECT DISTINCT ?movie ?movie_title ?abstract ?link ?year_sub2(group_concat(?subject; separator = " ") as ?list)' \
                           ' WHERE{   ' \
                           ' ?movie a dbo:Film ; ' \
                           ' foaf:isPrimaryTopicOf ?link; ' \
                           ' rdfs:label ?movie_title ;' \
                           ' dbp:country|dbo:country ?country ;' \
                           ' dbo:abstract ?abstract;' \
                           ' dct:subject ?sub;' \
                           ' dct:subject ?subject' \
                           ' FILTER langMatches(lang(?movie_title), "en").' \
                           ' FILTER langMatches(lang(?abstract), "en").' \
                           ' FILTER (CONTAINS(xsd:string(?country), "United States")||CONTAINS(xsd:string(?country), "USA"))' \
                           ' BIND( IF( REGEX(xsd:string(?sub), "\\\\d{4}_"),   xsd:string(?sub),  0) AS ?year_sub)' \
                           ' BIND(REPLACE(xsd:string(?year_sub), "([^\\\\d]|(?<!\\\\d)\\\\d(?!\\\\d{3}(?!\\\\d))\\\\d*)", "") AS ?year_sub2)' \
                           'FILTER(xsd:integer(?year_sub2) >= ' + year + ' )'\
                           '} ' \
                           '}' \
                           ' BIND((IF  (regex(xsd:string(?abstract), "' + \
                           top_kw[0] + '", "i"),  ' + str(int(top_kw[1] * 70)) + ' , -' + str(int(top_kw[1] * 70)) + ')) AS ?top_kw).'

        query_second_part = query_first_part + query_second_part
        query_second_part, final_score = subject_keyword(keywords, query_second_part)

        w, genres, selected_gnr, query_second_part = defineGenres_subject(w, query_second_part, kw_gnr)
        checker2 = ' BIND((IF  (regex(xsd:string(?abstract), "short.film"),  -100 , 0)) AS ?optional3 ).  '
        checker3 = ' BIND((IF  (regex(xsd:string(?abstract), "short.movie"),  -100 , 0)) AS ?optional4 ).  '

        if len(keywords) == 0 and len(nounArray) > 0:
            scorer = scorer[:-2]

        for g in range(0, len(genres)*2):
            scorer = scorer + '+ ?genre' + str(g)

        scorer = scorer.replace("+ +", "+")

        if final_score == '':
            final_query = query_second_part + checker2 + checker3 + '   BIND((?top_kw + ?optional3 + ?optional4 + ' + scorer + ' ) as ?score).   } ORDER BY desc(?score) limit ' + limit + ' '
        else:
            if final_score[len(final_score) - 2] == '+':
                final_score = final_score[:-2] + ' '
            final_query = query_second_part + checker2 + checker3 + ' BIND((?top_kw + ?optional3 + ?optional4 + ' + scorer + ' + ' + final_score + ' ) as ?score).  } ORDER BY desc(?score) limit ' + limit + ''
    else:
        final_query = ''
    return final_query, too_much
