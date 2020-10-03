import spacy
import telepot

punctuation = set("!@#$-%^'&*()_+<>?:.,;")
nlp = spacy.load("en_core_web_sm")
movies_genres = ['crime', 'action', 'adventure', 'comedy', 'drama', 'fantasy', 'historical', 'horror', 'mystery',
                 'romantic', 'saga', 'satirical', 'thriller', 'scientific', 'urban', 'western', 'cowboys', 'country',
                 'sci-fi', 'science fiction', 'cartoon', 'detective', 'superhero', 'animated', 'investigative', 'space',
                 'documentary']
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
    w = ''
    for token in doc:
        if token.pos_ != 'VERB':
            w = w + ' ' + token.text
    for p in punctuation:
        if p in w:
            w = w.replace(p, "")
    w = w.lower().split(' ')
    for k in w:
        if k in movies_genres:
            if genre == '':
                genre = '^(?=.*' + k + ')'
            else:
                genre = genre + '(?=.*' + k + ')'
    if genre != '':
        genre = genre + '.*$'
        genre_score = '10'
    else:
        genre = 'award'
        genre_score = '5'
    for i in range(0, len(keywords_first) - 1):
        for word in w:
            if (word == keywords_first[i][0] or (word in keywords_first[i][0] and len(keywords_first[i][0]) - len(
                    word) < 1)) and "ing" not in word and word not in kw_f_words and len(word) > 2:
                kw_f.append(keywords_first[i])
                kw_f_words.append(word)
                kw.append(word)
                kw_string = kw_string + '1) ' + str(word) + str(keywords_first[i][1]) + ' | '

    for i in range(0, len(keyword_second) - 1):
        for word in w:
            if word == keyword_second[i][0] or "ing" in word and len(word) > 2:
                if word not in kw_string:
                    kw_s.append(word)
                    kw_s_words.append(word)
                    kw.append(word)
                    kw_string = kw_string + '2) ' + str(word) + str(keyword_second[i][1]) + ' | '
    for word in w:
        if word in keyword_general:
            if word not in kw_string and len(word) > 2:
                if word not in kw_s:
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
            query_first_part = ' PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> ' \
                               ' PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> ' \
                               ' PREFIX dct:<http://purl.org/dc/terms/> ' \
                               ' PREFIX dbo:<http://dbpedia.org/ontology/> ' \
                               ' PREFIX dbpprop:<http://dbpedia.org/property/> ' \
                               ' PREFIX dbc:<http://dbpedia.org/resource/Category:> ' \
                               ' SELECT DISTINCT ?score  ?id ?movie ?movie_title ?year1 ?abstract ?link ?list  WHERE{ ' \
                               ' { SELECT DISTINCT ?score1  ?id ?movie ?movie_title ?year1 ?abstract ?link (group_concat(distinct ?subj1; separator = ";") as ?list) ' \
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
                            ' BIND((IF (REGEX(xsd:string(?abstract), "' + genre + '"), ' + genre_score + ' , 0)) AS ?genre_str). ' \
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
                nouner = ' BIND((IF (REGEX(xsd:string(?abstract), "' + str(noun) + '"), 5 , 0)) AS ?' + support + 's). '
                scorer = scorer + '?' + support + 's + '
                query_second_part = query_second_part + nouner
            scorer = scorer + ' ?genre_str +'
            for k in kw:
                if k in kw_f_words:
                    weight = '4'
                elif k in kw_s:
                    weight = '2'
                else:
                    weight = '1'
                if len(k) > 2 and k != 'film' and k != 'movie':
                    binder = ' BIND((IF (REGEX(xsd:string(?abstract), " [' + k[0].upper() + k[0].lower() + ']' + k[
                                                                                                                 1:] + ' "), ' + weight + ' , 0)) AS ?' + k.replace(
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
                query_second_part = query_second_part + '  BIND(( ' + scorer + ') as ?score1).  }} '
            else:
                query_second_part = query_second_part + '  BIND(( 0 as ?score1).  }} '

            s1 = 1
            final_score = ''

            for noun in nounArray:
                current = str(noun).strip()
                n = ' BIND((IF (REGEX(xsd:string(?list), "[' + current[0].upper() + current[
                    0].lower() + ']' + current[1:] + '"), 10 , 0)) AS ?special' + str(s1) + ' ). '
                final_score = final_score + '?special' + str(s1) + ' + '
                query_second_part = query_second_part + n
                s1 += 1
            count = 0
            for x in kw_f_words:
                binder = ' BIND((IF  (regex(xsd:string(?list), "[' + x[0].upper() + x[0].lower() + ']' + x[
                                                                                                         1:] + '"),  7 , 0)) AS ?special' + str(
                    s1) + ' ).  '
                query_second_part = query_second_part + binder
                if count == (len(kw_f_words) - 1):
                    final_score = final_score + '?special' + str(s1)
                else:
                    final_score = final_score + '?special' + str(s1) + ' + '
                s1 += 1
                count += 1
            if len(kw_s_words) > 0:
                count = 0
                final_score = final_score + ' + '
                for x in kw_s_words:
                    binder = ' BIND((IF  (regex(xsd:string(?list), "[' + x[0].upper() + x[0].lower() + ']' + x[
                                                                                                             1:] + '"),  4 , 0)) AS ?special' + str(
                        s1) + ' ).  '
                    query_second_part = query_second_part + binder
                    if count == (len(kw_s_words) - 1):
                        final_score = final_score + '?special' + str(s1)
                    else:
                        final_score = final_score + '?special' + str(s1) + ' + '
                    s1 += 1
                    count += 1
            binder = ' BIND((IF  (regex(xsd:string(?list), "' + genre + '"),  10 , 0)) AS ?genres ).  '
            query_second_part = query_second_part + binder
            if final_score == '':
                final_query = query_second_part + ' BIND((?genres +?score1 ) as ?score).  }ORDER BY desc(?score) desc(?year1) limit 5 '
            else:
                if final_score[len(final_score) - 2] == '+':
                    final_score = final_score[:-2] + ' '
                final_score = ' ?genres + ' + final_score
                final_query = query_second_part + ' BIND((?score1 + ' + final_score + ') as ?score).  }ORDER BY desc(?score) desc(?year1) limit 5 '
    else:
        final_query = ''
    return final_query, kw_string
