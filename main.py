import time
from pprint import pprint
import pandas as pd
import telepot
from telepot.loop import MessageLoop
import keywordConstructor as kc
import sparql
from SPARQLWrapper import SPARQLWrapper, JSON
import spacy

movies_genres = ['crime', 'action', 'adventure', 'comedy', 'drama', 'fantasy', 'historical', 'horror', 'mystery'
    , 'romance', 'saga', 'satire', 'thriller', 'science', 'urban', 'western', 'animation', 'cowboys', 'country',
                 'sci-fi', 'cartoon', 'detective', 'superhero']
s = sparql.Service(endpoint='http://dbpedia.org', qs_encoding="uft-8", method="GET")
punctuation = set("!@#$-%^&*()_+<>?:.,;")
db = pd.read_csv(r"C:\Users\Stefano\Desktop\films.csv", sep=';', header=None)
keywords_first, keyword_second, keyword_general = kc.keywordGenerator(db)
nlp = spacy.load("en_core_web_sm")


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)  # glance lavora con ogni tipo di messaggio
    genre = ''
    if msg['text'] == '/start':
        bot.sendMessage(chat_id, "WELCOME TO MOVIE ADVISOR! \n\nTold me what kind of movies you want to see"
                                 "\nWrite a short description about the type of film you want to see\nthe longer"
                                 " description provided, the better result you get\n\nGive me a description")
    else:
        doc = nlp(msg['text'])
        for chunk in doc.noun_chunks:
            print('\n' + chunk.text)
        extra_part = ''
        kw_f = []
        kw_f_words = []
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
        genre_score = '0'
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
        pprint(keywords_first)
        for i in range(0, len(keywords_first) - 1):
            for word in w:
                if (word == keywords_first[i][0] or (word in keywords_first[i][0] and len(keywords_first[i][0]) - len(
                        word) < 1)) and "ing" not in word and word not in kw_f_words and len(word) > 2:
                    kw_f.append(keywords_first[i])
                    kw_f_words.append(word)
                    kw.append(word)
                    kw_string = kw_string + '1) ' + str(word) + ' | '

        for i in range(0, len(keyword_second) - 1):
            for word in w:
                if word == keyword_second[i][0] or "ing" in word and len(word) > 2:
                    if word not in kw_string:
                        kw_s.append(word)
                        kw.append(word)
                        kw_string = kw_string + '2) ' + str(word) + ' | '
        for word in w:
            if word in keyword_general:
                if word not in kw_string and len(word) > 2:
                    if word not in kw_s:
                        kw_g.append(word)
                        kw.append(word)
                        kw_string = kw_string + '3) ' + str(word) + ' | '

        kw_f.sort(key=lambda tup: tup[1], reverse=True)
        if len(kw) > 0:
            bot.sendMessage(chat_id, "Ok ok I'm searching......\n")
            top_word = ''
            if len(kw_f) > 0:
                if genre != kw_f[0][0]:
                    top_word = kw_f[0][0]
                elif len(kw_f) > 1:
                    top_word = kw_f[1][0]

            nounArray = []
            print('CHUNKER:\n')
            for chunk in doc.noun_chunks:
                for key in kw:
                    if key in chunk.text:
                        first = key
                        for key_ in kw:
                            if key_ in chunk.text and key_ != first:
                                txt = nlp(chunk.text)
                                result = ''
                                for tk in txt:
                                    pos = str(tk.pos_)
                                    if pos != 'CONJ' and pos != 'PRON' and pos != 'ADV' and pos != 'ADP' and pos != 'PUNCT' and pos != 'SCONJ' and pos != 'DET':
                                        result = result + ' ' + tk.text
                                    testo = result
                                    res = len(testo.split())
                                    if testo not in nounArray and res > 1:
                                        nounArray.append(testo)
                                        print(testo + '\n')
            if genre_score != '0':
                query_first_part = 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> ' \
                                   'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ' \
                                   'PREFIX dct: <http://purl.org/dc/terms/> ' \
                                   'PREFIX dbo: <http://dbpedia.org/ontology/> ' \
                                   'PREFIX dbpprop: <http://dbpedia.org/property/> ' \
                                   'PREFIX dbc: <http://dbpedia.org/resource/Category:> ' \
                                   'SELECT DISTINCT ?id ?movie ?movie_title ?year1 ?abstract ?link ' \
                                   ' WHERE { ' \
                                   '?movie dbo:wikiPageID ?id. ' \
                                   ' ?movie rdf:type dbo:Film. ' \
                                   '?movie rdfs:label ?movie_title ' \
                                   'FILTER REGEX(?movie_title, "[Ff]ilm"). ' \
                                   '?movie foaf:isPrimaryTopicOf ?link  . ' \
                                   '?movie dbo:abstract ?abstract  FILTER langMatches(lang(?abstract), "EN") ' \
                                   'BIND((IF (REGEX(?abstract, "' + genre + '"), ' + genre_score + ' , 0)) AS ?genre_str). ' \
                                                                                                   '?movie dct:subject ?subject_.  ?subject_ rdfs:label ?subject1. '
            else:
                query_first_part = 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> ' \
                                   'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ' \
                                   'PREFIX dct: <http://purl.org/dc/terms/> ' \
                                   'PREFIX dbo: <http://dbpedia.org/ontology/> ' \
                                   'PREFIX dbpprop: <http://dbpedia.org/property/> ' \
                                   'PREFIX dbc: <http://dbpedia.org/resource/Category:> ' \
                                   'SELECT DISTINCT ?id ?movie ?movie_title ?year1 ?abstract ?link ' \
                                   ' WHERE { ' \
                                   '?movie dbo:wikiPageID ?id. ' \
                                   ' ?movie rdf:type dbo:Film. ' \
                                   '?movie rdfs:label ?movie_title ' \
                                   'FILTER REGEX(?movie_title, "[Ff]ilm"). ' \
                                   '?movie foaf:isPrimaryTopicOf ?link  . ' \
                                   '?movie dbo:abstract ?abstract  FILTER langMatches(lang(?abstract), "EN") ' \
                                   'BIND((IF (REGEX(?abstract, "' + genre + '"), 3 , 0)) AS ?genre_str). ' \
                                                                                                   '?movie dct:subject ?subject_.  ?subject_ rdfs:label ?subject1. '
            query_second_part = ''
            scorer = ''
            count = 0
            special = ''
            for noun in nounArray:
                nouner = ' BIND((IF (REGEX(?abstract, "' + str(noun) + '"), 5 , 0)) AS ?' + str(noun).replace(" ",
                                                                                                              "_") + 's). '
                scorer = scorer + '?' + str(noun).replace(" ", "_") + 's + '
                query_second_part = query_second_part + nouner
            scorer = scorer + ' ?genre_str +'
            for k in kw:
                if k in kw_f_words:
                    weight = '4'
                elif k in kw_s:
                    weight = '2'
                else:
                    weight = '1'
                if k == 'film' or k == 'movie' and k != kw_f[0][0] and len(k) > 2:
                    binder = ' BIND((IF (REGEX(?abstract, " [' + k[0].upper() + k[0].lower() + ']' + k[
                                                                                                     1:] + 's "), ' + weight + ', 0)) AS ?' + k.replace(
                        "-", "") + 's). '
                    query_second_part = query_second_part + binder
                    if count == len(kw) - 1:
                        scorer = scorer + '?' + k.replace("-", "") + 's'
                    else:
                        scorer = scorer + '?' + k.replace("-", "") + 's + '
                    count += 1
                    binder = ''
                    special = ''
                elif k != kw_f[0][0] and len(k) > 2:
                    binder = ' BIND((IF (REGEX(?abstract, " [' + k[0].upper() + k[0].lower() + ']' + k[
                                                                                                     1:] + ' "), ' + weight + ' , 0)) AS ?' + k.replace(
                        "-", "") + '). '
                    query_second_part = query_second_part + binder
                    if count == len(kw) - 1:
                        scorer = scorer + '?' + k.replace("-", "")
                    else:
                        scorer = scorer + '?' + k.replace("-", "") + ' + '
                    count += 1
                    binder = ''
                    special = ''
                elif k == kw_f[0][0] or len(k) <= 2:
                    count += 1
            query_third_part = ' FILTER langMatches(lang(?movie_title), "EN") . ' \
                               '?movie dct:subject ?subject. ' \
                               '?subject rdfs:label ?year . ' \
                               ' filter regex(?year, "\\\\d{4}.films") .' \
                               ' BIND(REPLACE(?year, "[^\\\\b0-9\\\\b]", "") AS ?movie_year2) BIND(SUBSTR(str(?movie_year2), 0,  4) AS ?year1) ' \
                               ' FILTER(xsd:integer(?year1) > 1990) ' \
                               '}ORDER BY desc(?score) desc(?year1)  limit 5'
            if top_word != '' and scorer != '':
                extra_part = ' BIND((IF  (REGEX(?subject1, "[' + top_word[0].upper() + top_word[
                    0].lower() + ']' + top_word[1:] + '"),  5 , 0)) AS ?special2 ). '
                if len(kw) > 1:
                    final_query = query_first_part + query_second_part + extra_part + '  BIND(( ?special2 + ' + scorer + ') as ?score). ' + query_third_part
                else:
                    final_query = query_first_part + query_second_part + extra_part + '  BIND(( ?special2 ) as ?score). ' + query_third_part

            elif top_word == '' and scorer != '':
                scorer = scorer.replace('+ )', ' )')
                final_query = query_first_part + query_second_part + '  BIND(( ' + scorer + ') as ?score). ' + query_third_part
            else:
                final_query = query_first_part + query_second_part + query_third_part
            print(final_query)
            print('\nKEYWORDS: ' + kw_string)
            print('---------------')
            sparql = SPARQLWrapper('http://dbpedia.org/sparql')
            sparql.setQuery(final_query)
            sparql.setReturnFormat(JSON)
            ret = sparql.query().convert()
            titles = []
            abstracts = []
            links = []
            for result in ret["results"]["bindings"]:
                titles.append(result["movie_title"]["value"])
                abstracts.append(
                    (result["abstract"]["value"][:300] + '....') if len(result["abstract"]["value"]) > 300 else
                    result["abstract"]["value"])
                links.append(result["link"]["value"])
            bot.sendMessage(chat_id, "I suggest you..\n\n")
            if len(titles) == 5:
                bot.sendMessage(chat_id, titles[0].upper() + '\n\n' + abstracts[0] + '\n\n' + links[0])
                bot.sendMessage(chat_id, titles[1].upper() + '\n\n' + abstracts[1] + '\n\n' + links[1])
                bot.sendMessage(chat_id, titles[2].upper() + '\n\n' + abstracts[2] + '\n\n' + links[2])
                bot.sendMessage(chat_id, titles[3].upper() + '\n\n' + abstracts[3] + '\n\n' + links[3])
                bot.sendMessage(chat_id, titles[4].upper() + '\n\n' + abstracts[4] + '\n\n' + links[4])
                bot.sendMessage(chat_id, "Write again if you want search another film\n\n")
            if len(titles) == 4:
                bot.sendMessage(chat_id, titles[0].upper() + '\n\n' + abstracts[0] + '\n\n' + links[0])
                bot.sendMessage(chat_id, titles[1].upper() + '\n\n' + abstracts[1] + '\n\n' + links[1])
                bot.sendMessage(chat_id, titles[2].upper() + '\n\n' + abstracts[2] + '\n\n' + links[2])
                bot.sendMessage(chat_id, titles[3].upper() + '\n\n' + abstracts[3] + '\n\n' + links[3])
                bot.sendMessage(chat_id, "Write again if you want search another film\n\n")
            if len(titles) == 3:
                bot.sendMessage(chat_id, titles[0].upper() + '\n\n' + abstracts[0] + '\n\n' + links[0])
                bot.sendMessage(chat_id, titles[1].upper() + '\n\n' + abstracts[1] + '\n\n' + links[1])
                bot.sendMessage(chat_id, titles[2].upper() + '\n\n' + abstracts[2] + '\n\n' + links[2])
                bot.sendMessage(chat_id, "Write again if you want search another film\n\n")
            if len(titles) == 2:
                bot.sendMessage(chat_id, titles[0].upper() + '\n\n' + abstracts[0] + '\n\n' + links[0])
                bot.sendMessage(chat_id, titles[1].upper() + '\n\n' + abstracts[1] + '\n\n' + links[1])
                bot.sendMessage(chat_id, "Write again if you want search another film\n\n")
            if len(titles) == 1:
                bot.sendMessage(chat_id, titles[0].upper() + '\n\n' + abstracts[0] + '\n\n' + links[0])
                bot.sendMessage(chat_id, "Write again if you want search another film\n\n")
        else:
            bot.sendMessage(chat_id, "Couldn't extract enough keywords, try rewriting the message")


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg,
                                                   flavor='callback_query')  # stiamo dicendo applica il metodo glance ma non alla chat come prima ma a un metodo che appunto chiamiamo callback_query e quindi una inline keyboard
    print("Callback Query: ", query_id, from_id, query_data)

    bot.answerCallbackQuery(query_id, text="E bravo")


bot = telepot.Bot("1040963180:AAGh02okW5n0I3wJf0z9EzK7Xh1uGuwis_0")
# specifico che devo usare un determinato gestore per la chat e un altro per le inlinequery
MessageLoop(bot, {'chat': on_chat_message, 'callback_query': on_callback_query}).run_as_thread()
print("READY!")

while 1:
    time.sleep(1)
