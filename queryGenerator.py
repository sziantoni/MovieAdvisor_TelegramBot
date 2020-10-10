import spacy
import telepot
import pattern.text.en as plur

punctuation = set("!@#$-%^'&*()_+<>?:.,;")
nlp = spacy.load("en_core_web_sm")
movies_genres = ['crime', 'action', 'adventure', 'comedy', 'drama', 'fantasy', 'historical', 'horror', 'mystery',
                 'romantic', 'saga', 'satirical', 'thriller', 'scientific', 'urban', 'western', 'country',
                 'sci-fi', 'science fiction', 'cartoon', 'superhero', 'animated', 'investigative', 'space',
                 'documentary', 'sport', 'war']
bot = telepot.Bot("1040963180:AAGh02okW5n0I3wJf0z9EzK7Xh1uGuwis_0")


def queryConstructor(msg, keywords_first, keyword_second, keyword_general, language, year):
    doc = nlp(msg)
    genre = ''
    kw_f = []
    kw_f_words = []
    kw_s_words = []
    kw_s = []
    kw_g = []
    kw = []
    kw_string = ''
    w = msg
    for p in punctuation:
        if p in w:
            w = w.replace(p, "")
    w = w.lower().split(' ')
    genres = []
    c_gnr = 0
    for k in range(0, len(w)-1):
        if len(w[k]) > 6:
            plural = plur.pluralize(w[k])
            if p not in w:
                w.append(plural)
        if w[k] in movies_genres:
            gnr = '(?=.*' + w[k] + ')'
            if gnr not in genres and c_gnr < 2:
                c_gnr += 1
                genres.append(gnr)
    for h in range(0, len(genres)):
        if h == len(genres) - 1:
            genre = genre + genres[h]
        else:
            genre = genre + genres[h]
    for i in range(0, len(keywords_first) - 1):
        for word in w:
            if (word == keywords_first[i][0] or (word in keywords_first[i][0] and len(keywords_first[i][0]) - len(
                    word) < 1)) and word not in kw_f_words and len(word) > 2 and keywords_first[i] not in kw_f:
                kw_f.append(keywords_first[i])
                kw_f_words.append(word)
                kw.append(word)
                kw_string = kw_string + '1) ' + str(word) + str(keywords_first[i][1]) + ' | '

    for i in range(0, len(keyword_second) - 1):
        for word in w:
            if word == keyword_second[i][0] and len(word) > 2 and word not in kw_s_words and word not in kw_f_words:
                kw_s.append(keyword_second[i])
                kw_s_words.append(word)
                kw.append(word)
                kw_string = kw_string + '2) ' + str(word) + str(keyword_second[i][1]) + ' | '
    for word in w:
        if word in keyword_general:
            if len(word) > 2:
                if word not in kw_s_words and word not in kw_g:
                    kw_g.append(word)
                    kw.append(word)
                    kw_string = kw_string + '3) ' + str(word) + ' | '

    kw_f.sort(key=lambda tup: tup[1], reverse=True)
    if len(kw) > 0:
        nounArray = []
        print('CHUNKER:\n')
        for chunk in doc.noun_chunks:
            text = chunk.text.lower()
            for key in kw:
                if key in text:
                    for k in kw:
                        if k in text and k is not key:
                            if text[0] == 'a' and text[1] == 'n' and text[2] == ' ':
                                text = text[3:]
                            if text[0] == 'a' and text[1] == ' ':
                                text = text[2:]
                            if text[0] == 't' and text[1] == 'h' and text[2] == 'e' and text[3] == ' ':
                                text = text[4:]
                            if len(text) - (len(k) + len(key)) == 1:
                                if text not in nounArray:
                                    nounArray.append(text)
                                    print(text)
        if genre == '' and len(kw_f) > 0:
            genre = '(?=.*' + kw_f[0][0] + '?)'
        elif genre == '':
            genre = 'film'
        query_first_part = ' PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> ' \
                           ' PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> ' \
                           ' PREFIX dct:<http://purl.org/dc/terms/> ' \
                           ' PREFIX dbo:<http://dbpedia.org/ontology/> ' \
                           ' PREFIX dbpprop:<http://dbpedia.org/property/> ' \
                           ' PREFIX dbc:<http://dbpedia.org/resource/Category:> ' \
                           ' SELECT DISTINCT ?score  ?id ?movie ?movie_title ?year1 ?abstract ?link ?list  WHERE{ ' \
                           ' { SELECT DISTINCT ?score1  ?id ?movie ?movie_title ?year1 ?abstract ?link (group_concat(distinct ?subj1; separator = " ") as ?list) ' \
                           ' FROM <http://dbpedia.org>  WHERE{ ' \
                           ' ?movie dbo:wikiPageID ?id. ' \
                           ' ?movie rdf:type dbo:Film. ' \
                           ' ?movie rdfs:label ?movie_title ' \
                           ' FILTER langMatches(lang(?movie_title), "EN"). ' \
                           ' FILTER REGEX(?movie_title, "[Ff]ilm"). ' \
                           ' ?movie dbp:country ?country FILTER CONTAINS(xsd:string(?country), "' + str(
            language) + '").' \
                        ' ?movie foaf:isPrimaryTopicOf ?link  . ' \
                        ' ?movie dbo:abstract ?abstract  FILTER langMatches(lang(?abstract), "EN") ' \
                        ' FILTER REGEX(lcase(xsd:string(?abstract)), "(' + genre + ')"). ' \
                                                                                   ' ?movie  dct:subject ?subject. ' \
                                                                                   ' ?subject rdfs:label ?year. ' \
                                                                                   ' filter regex(?year, "\\\\d{4}.films"). ' \
                                                                                   ' BIND(REPLACE(xsd:string(?year), "[^\\\\b0-9\\\\b]", "") AS ?movie_year2) ' \
                                                                                   ' BIND(SUBSTR(str(?movie_year2), 0, 4) AS ?year1)  FILTER(xsd:integer(?year1) > ' + year + ') ' \
                                                                                                                                                                              ' ?movie dct:subject ?subject1. ' \
                                                                                                                                                                              ' ?subject1 rdfs:label ?subj1 '
        query_second_part = ''
        scorer = ''
        count = 0
        for noun in nounArray:
            support = str(noun).replace(" ", "_")
            support = support.replace("-", "_")
            nouner = ' BIND((IF (REGEX(xsd:string(?abstract), "' + str(
                noun) + '"), 12 , -5)) AS ?' + support + 's). '
            scorer = scorer + '?' + support + 's + '
            query_second_part = query_second_part + nouner
        d_kw_f = dict(kw_f)
        d_kw_s = dict(kw_s)
        for k in kw:
            penalties = '0'
            if len(kw_f_words) > 0:
                if k in kw_f_words:
                    if float(d_kw_f[k]) > 0.55:
                        weight = '20'
                        penalties = '-20'
                    elif float(d_kw_f[k]) > 0.5:
                        weight = '15'
                        penalties = '-10'
                    elif float(d_kw_f[k]) > 0.45:
                        weight = '12'
                        penalties = '-8'
                    else:
                        weight = '8'
                elif k in kw_s_words:
                    if len(kw_f) == 0 and len(kw_s) < 3:
                        weight = '8'
                    elif len(kw_f) == 0 and len(kw_s) > 2:
                        weight = '6'
                    else:
                        weight = '3'
                else:
                    weight = '2'
                if len(k) > 2 and k != 'film' and k != 'movie':
                    binder = ' BIND((IF (REGEX(lcase(xsd:string(?abstract)), "^(?=.* ' + k + ' ).*$"), ' + weight + ' , ' + penalties + ')) AS ?' + k.replace(
                        "-", "") + '). '
                    query_second_part = query_second_part + binder
                    if count == len(kw) - 1:
                        scorer = scorer + '?' + k.replace("-", "")
                    else:
                        scorer = scorer + '?' + k.replace("-", "") + ' + '
                    count += 1
                elif len(k) <= 2:
                    count += 1
            else:
                if k in kw_s_words:
                    if float(d_kw_s[k]) > 0.35:
                        weight = '20'
                        penalties = '-20'
                    elif float(d_kw_s[k]) > 0.30:
                        weight = '15'
                        penalties = '-10'
                    else:
                        weight = '8'
                else:
                    weight = '2'
                if len(k) > 2 and k != 'film' and k != 'movie':
                    binder = ' BIND((IF (REGEX(lcase(xsd:string(?abstract)), "^(?=.* ' + k + ' ).*$"), ' + weight + ' , ' + penalties + ')) AS ?' + k.replace(
                        "-", "") + '). '
                    query_second_part = query_second_part + binder
                    if count == len(kw) - 1:
                        scorer = scorer + '?' + k.replace("-", "")
                    else:
                        scorer = scorer + '?' + k.replace("-", "") + ' + '
                    count += 1
                elif len(k) <= 2:
                    count += 1
        query_second_part = query_first_part + query_second_part

        if scorer != ' ':
            if scorer[len(scorer)-2] == '+':
                scorer = scorer[:-2] + ' '
            query_second_part = query_second_part + '  BIND(( ' + scorer + ') as ?score1).  }} '
        else:
            query_second_part = query_second_part + '  BIND(( 0 as ?score1).  }} '

        s1 = 1
        final_score = ''

        for noun in nounArray:
            current = str(noun).strip()
            n = ' BIND((IF (REGEX(lcase(xsd:string(?list)), " [' + current[0].upper() + current[
                0].lower() + ']' + current[1:] + '"), 15 , 0)) AS ?special' + str(s1) + ' ). '
            final_score = final_score + '?special' + str(s1) + ' + '
            query_second_part = query_second_part + n
            s1 += 1
        count = 0
        for x in kw_f:
            penalties = '0'
            if float(x[1]) > 0.55:
                weight = '20'
                penalties = '-20'
            elif float(x[1]) > 0.50:
                weight = '15'
                penalties = '-10'
            elif float(x[1]) > 0.45:
                weight = '12'
                penalties = '-8'
            else:
                weight = '7'
            binder = ' BIND((IF  (regex(lcase(xsd:string(?list)), "^(?=.* ' + x[0] + ' ).*$"),  ' + weight + ' , ' + penalties + ')) AS ?special' + str(
                s1) + ' ).  '
            query_second_part = query_second_part + binder
            if count == (len(kw_f_words) - 1):
                final_score = final_score + '?special' + str(s1)
            else:
                final_score = final_score + '?special' + str(s1) + ' + '
            s1 += 1
            count += 1

        if len(kw_s_words) > 0:
            if len(kw_f_words) > 0:
                count = 0
                final_score = final_score + ' + '
                for x in kw_s_words:
                    binder = ' BIND((IF  (regex(lcase(xsd:string(?list)), "^(?=.* ' + x + ' ).*$"),  6 , 0)) AS ?special' + str(
                        s1) + ' ).  '
                    query_second_part = query_second_part + binder
                    if count == (len(kw_s_words) - 1):
                        final_score = final_score + '?special' + str(s1)
                    else:
                        final_score = final_score + '?special' + str(s1) + ' + '
                    s1 += 1
                    count += 1
            else:
                count = 0
                final_score = final_score + ' + '
                for x in kw_s:
                    penalties = '0'
                    if float(x[1]) > 0.35:
                        weight = '20'
                        penalties = '-20'
                    elif float(x[1]) > 0.30:
                        weight = '15'
                        penalties = '-10'
                    else:
                        weight = '8'

                    binder = ' BIND((IF  (regex(lcase(xsd:string(?list)), "^(?=.* ' + x[0] + ' ).*$"),  ' + weight + ' , ' + penalties + ')) AS ?special' + str(
                        s1) + ' ).  '
                    query_second_part = query_second_part + binder
                    if count == (len(kw_s_words) - 1):
                        final_score = final_score + '?special' + str(s1)
                    else:
                        final_score = final_score + '?special' + str(s1) + ' + '
                    s1 += 1
                    count += 1

        binder = ' BIND((IF  (regex(xsd:string(?list), "(' + genre + ')"),  10 , 0)) AS ?genres ).  '
        checker = ' BIND((IF  (regex(xsd:string(?list), "short film"),  -100 , 0)) AS ?optional1 ).  '
        checker1 = ' BIND((IF  (regex(xsd:string(?list), "short movie"),  -100 , 0)) AS ?optional2 ).  '
        checker2 = ' BIND((IF  (regex(xsd:string(?abstract), "short film"),  -100 , 0)) AS ?optional3 ).  '
        checker3 = ' BIND((IF  (regex(xsd:string(?abstract), "short movie"),  -100 , 0)) AS ?optional4 ).  '
        query_second_part = query_second_part + binder + checker + checker1 + checker2 + checker3
        if final_score == '':
            final_query = query_second_part + ' BIND((?genres +?score1 ) as ?score).  }ORDER BY desc(?score) desc(?year1) limit 5 '
        else:
            if final_score[len(final_score) - 2] == '+':
                final_score = final_score[:-2] + ' '
            final_score = ' ?genres + ?optional1 + ?optional2 + ?optional3 + ?optional4 + ' + final_score
            final_query = query_second_part + ' BIND((?score1 + ' + final_score + ') as ?score).  }ORDER BY desc(?score) limit 5 '
    else:
        final_query = ''
    return final_query, kw_string
