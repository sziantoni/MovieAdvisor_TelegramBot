import time
import pandas as pd
import telepot
from telepot.loop import MessageLoop
import sparql
from SPARQLWrapper import SPARQLWrapper, JSON
import spacy
import queryGenerator as qG
from keyboards import keyboard, keyboard5
import inlineKeyboardSelector
import keywordConstructor as kc
language = 'United States'
year = '2000'
msg_id = 0
s = sparql.Service(endpoint='http://dbpedia.org', qs_encoding="uft-8", method="GET")
db = pd.read_csv(r"C:\Users\Stefano\Desktop\films_new_clear.csv", sep=';', header=None)
#keywords_first, keyword_second, keyword_general = kc.keywordGenerator(db, 7378)
keywords_first, keyword_second, keyword_general = [], [], []
print(str(len(keywords_first)))
print(str(len(keyword_second)))
print(str(len(keyword_general)))
nlp = spacy.load("en_core_web_sm")
sparql = SPARQLWrapper('http://dbpedia.org/sparql')
sparql.setTimeout(50000)


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if msg['text'] == '/start':
        bot.sendMessage(chat_id, "WELCOME TO MOVIE ADVISOR! \n\nTold me what kind of movies you want to see"
                                 "\nWrite a short description about the type of film you want to see\nthe longer"
                                 " description provided, the better result you get\n\nDefault Nation: United States\n\nDefault Year: 2000",
                        reply_markup=keyboard)
    else:
        doc = nlp(str(msg['text']))
        for chunk in doc.noun_chunks:
            print(chunk.text)
        for token in doc:
            if str(token.text) != str(token.lemma_):
                msg['text'] = msg['text'] + ' ' + str(token.lemma_)
        final_query, kw_string = qG.queryConstructor(msg['text'], keywords_first, keyword_second, keyword_general, language, year)
        if final_query != '':
            bot.sendMessage(chat_id, "OK give me a few seconds to look for some movies to recommend..\n")
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
            i=0
            for x in titles:
                bot.sendMessage(chat_id, titles[i].upper() + '\n\n' + abstracts[i] + '\n\n' + links[i])
                i += 1
            bot.sendMessage(chat_id, "Write again if you want to search another films", reply_markup=keyboard5)
        else:
            bot.sendMessage(chat_id, "Couldn't extract enough keywords, try rewriting the message", reply_markup=keyboard5)


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg,
                                                   flavor='callback_query')
    global language
    global year
    language, year = inlineKeyboardSelector.selectKeyboard(query_data, from_id, language, year)


bot = telepot.Bot("1040963180:AAGh02okW5n0I3wJf0z9EzK7Xh1uGuwis_0")
MessageLoop(bot, {'chat': on_chat_message, 'callback_query': on_callback_query}).run_as_thread()
print("READY!")

while 1:
    time.sleep(1)
