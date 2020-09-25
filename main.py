import time
import pandas as pd
import telepot
from telepot.loop import MessageLoop
import keywordConstructor as kc
import sparql
from SPARQLWrapper import SPARQLWrapper, JSON
import spacy
import queryGenerator as qG
import numpy


s = sparql.Service(endpoint='http://dbpedia.org', qs_encoding="uft-8", method="GET")

db = pd.read_csv(r"C:\Users\Stefano\Desktop\film_gigante.csv", sep=';', header=None)
keywords_first, keyword_second, keyword_general = kc.keywordGenerator(db, 7000)
print(str(len(keywords_first)))
print(str(len(keyword_second)))
print(str(len(keyword_general)))
nlp = spacy.load("en_core_web_sm")
sparql = SPARQLWrapper('http://dbpedia.org/sparql')
sparql.setTimeout(50000)


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)  # glance lavora con ogni tipo di messaggio
    if msg['text'] == '/start':
        bot.sendMessage(chat_id, "WELCOME TO MOVIE ADVISOR! \n\nTold me what kind of movies you want to see"
                                 "\nWrite a short description about the type of film you want to see\nthe longer"
                                 " description provided, the better result you get\n\nGive me a description")
    else:
        bot.sendMessage(chat_id, "Ok ok I'm searching......\n")
        final_query, kw_string = qG.queryConstrcutor(msg['text'], keywords_first, keyword_second, keyword_general, chat_id)
        print(final_query)
        print('\nKEYWORDS: ' + kw_string)
        print('---------------')
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
