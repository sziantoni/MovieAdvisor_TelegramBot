import time
from pprint import pprint
import pandas as pd
import telepot
from telepot.loop import MessageLoop
import keywordConstructor as kc
import sparql

movies_genres = ['crime', 'action', 'adventure', 'comedy', 'drama', 'fantasy', 'historical', 'horror', 'mystery'
    , 'romance', 'saga', 'satire', 'thriller', 'science', 'urban', 'western', 'animation']
s = sparql.Service(endpoint='http://dbpedia.org', qs_encoding="uft-8", method="GET")
punctuation = set("!@#$%^&*()_+<>?:.,;")
db = pd.read_csv(r"C:\Users\Stefano\Desktop\films.csv", sep=';', header=None)

keywords = kc.keywordGenerator(db)

genre = ''


# result = sparql.query('http://dbpedia.org/sparql', q)
# pprint(result.variables)


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)  # glance lavora con ogni tipo di messaggio

    if msg['text'] == '/start':
        bot.sendMessage(chat_id, "WELCOME TO MOVIE ADVISOR! \n\nTold me what kind of movies you want to see"
                                 "\nWrite a short description about the type of film you want to see\nthe longer"
                                 " description provided, the better result you get\n\nGive me a description")
    else:
        pprint(msg['text'])
        kw = []
        kw_string = ''
        w = msg['text']
        for p in punctuation:
            if p in w:
                w = w.replace(p, "")
        w = w.lower().split(' ')
        for word in w:
            if word in keywords:
                if word not in kw:
                    kw.append(word)
                    kw_string = kw_string + str(word) + ' | '
        if len(kw) > 0:
            for k in kw:
                if k in movies_genres:
                    genre = k
            if genre == '':
                genre = 'film'

            query_first_part = 'PREFIX dbo: <http://dbpedia.org/ontology/> ' \
                               'PREFIX res: <http://dbpedia.org/resource/> ' \
                               'PREFIX dct: <http://purl.org/dc/terms/> ' \
                               'PREFIX dbc: <http://dbpedia.org/resource/Category:> ' \
                               'SELECT DISTINCT ?film ?score ?abstract ?link ?film_name ' \
                               'WHERE { ?film dbo:abstract ?abstract  FILTER CONTAINS(?abstract, " ' + genre + ' "). '
            query_second_part = ''
            scorer = ''
            count = 0
            for k in kw:
                if k == 'film':
                    binder = ' BIND((IF (REGEX(?abstract, " [' + k[0].upper() + k[0].lower() + ']' + k[
                                                                                                     1:] + 's "), 1, 0)) AS ?' + k + 's). '
                    query_second_part = query_second_part + binder
                    if count == len(kw) - 1:
                        scorer = scorer + '?' + k + 's'
                    else:
                        scorer = scorer + '?' + k + 's + '
                    count += 1
                    binder = ''
                else:
                    binder = ' BIND((IF (REGEX(?abstract, " [' + k[0].upper() + k[0].lower() + ']' + k[
                                                                                                 1:] + ' "), 1, 0)) AS ?' + k + '). '
                    query_second_part = query_second_part + binder
                    if count == len(kw) - 1:
                        scorer = scorer + '?' + k
                    else:
                        scorer = scorer + '?' + k + ' + '
                    count += 1
                    binder = ''


            query_third_part = ' ?film rdfs:label ?film_name ' \
                               'filter (lang(?film_name)="en"). ' \
                               'filter contains(?film_name, "film") ' \
                               '?film rdf:type dbo:Film . ' \
                               ' ?film foaf:isPrimaryTopicOf ?link  ' \
                               '} ORDER BY DESC(?score) LIMIT 5 '

            final_query = query_first_part + query_second_part + '  BIND((' + scorer + ') as ?score). ' + query_third_part

            print(final_query)
            bot.sendMessage(chat_id, 'KeyWords: ' + kw_string)
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
print("listening...")

while 1:
    time.sleep(1)
