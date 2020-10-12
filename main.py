import time
import pandas as pd
import telepot
from telepot.loop import MessageLoop
import sparql
from SPARQLWrapper import SPARQLWrapper, JSON
import spacy
from telepot.namedtuple import ReplyKeyboardRemove

import queryGenerator as qG
from keyboards import k1, k6
import inlineKeyboardSelector
import keywordConstructor as kc
import csv

language = 'United States'
year = '1980'
msg_id = 0
s = sparql.Service(endpoint='http://dbpedia.org', qs_encoding="uft-8", method="GET")
keyboards = ['Settings', 'Start', 'Nationality', 'Year', 'United States', 'Italy', 'France', 'England', 'Back', '1900',
             '1920', '1950', '1980', '1990', '2000', '2010', 'Continue']
# db = pd.read_csv(r"C:\Users\Stefano\Desktop\prova3-6515.csv", sep=';', header=None)
# keywords_first, keyword_second, keyword_general = kc.keywordGenerator(db, 6515)

keywords_first, keyword_second, keyword_general = [], [], []

with open('kw1.csv', 'r') as kw_1:
    csv_reader = csv.reader(kw_1, delimiter=';')
    for row in csv_reader:
        keywords_first.append((row[0], row[1]))

with open('kw2.csv', 'r') as kw_2:
    csv_reader = csv.reader(kw_2, delimiter=';')
    for row in csv_reader:
        keyword_second.append((row[0], row[1]))

with open('kw3.csv', 'r') as kw_3:
    csv_reader = csv.reader(kw_3, delimiter=';')
    for row in csv_reader:
        keyword_general.append((row[0], row[1]))

print(str(len(keywords_first)))
print(str(len(keyword_second)))
print(str(len(keyword_general)))
nlp = spacy.load("en_core_web_sm")
sparql = SPARQLWrapper('http://dbpedia.org/sparql')
sparql.setTimeout(50000)


def on_chat_message(msg):
    global language
    global year
    content_type, chat_type, chat_id = telepot.glance(msg)
    if msg['text'] == '/start':
        bot.sendMessage(chat_id, "WELCOME TO MOVIE ADVISOR! \n\nTold me what kind of movies you want to see"
                                 "\nWrite a short description about the type of film you want to see\nthe longer"
                                 " description provided, the better result you get\n\nDefault Nation: United States\n\nDefault Year: 1980",
                        reply_markup=k1)
    else:
        if msg['text'] in keyboards:
            language, year = inlineKeyboardSelector.selectKeyboard(chat_id, msg['text'], language, year)
        else:
            doc = nlp(str(msg['text']))
            for token in doc:
                if str(token.text) != str(token.lemma_) and '-' not in str(token.lemma_):
                    msg['text'] = msg['text'] + ', ' + str(token.lemma_)

            too_much = False
            final_query, kw_string, too_much = qG.queryConstructor(msg['text'], keywords_first, keyword_second,
                                                                   keyword_general,
                                                                   language, year)
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
                i = 0
                added = []
                for x in titles:
                    if x not in added:
                        bot.sendMessage(chat_id, titles[i].upper() + '\n\n' + abstracts[i] + '\n\n' + links[i])
                        added.append(x)
                    i += 1
                if too_much is True:
                    bot.sendMessage(chat_id,
                                    "WARNING! You have written too much text, the search excluded less significant keywords ")
                bot.sendMessage(chat_id, "Write again if you want to search another films")
            else:
                bot.sendMessage(chat_id, "Couldn't extract enough keywords, try rewriting the message", reply_markup=k6)


bot = telepot.Bot("1040963180:AAGh02okW5n0I3wJf0z9EzK7Xh1uGuwis_0")
MessageLoop(bot, on_chat_message).run_as_thread()
print("READY!")

while 1:
    time.sleep(1)
