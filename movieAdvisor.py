import time
from random import randint
import telepot
from telepot.loop import MessageLoop
import spacy
import queryGenerator as qG
from keyboards import k1, k6, k7, k8
import inlineKeyboardSelector
import csv
from SPARQLWrapper import SPARQLWrapper, JSON

no_genre = False
titles_ = []
previous_msg = []
sparql = SPARQLWrapper(endpoint='http://dbpedia.org/sparql')
chrome_diver = 'C:\\Users\\Stefano\\Downloads\\chromedriver.exe'
phantom = 'C:\\Users\\Stefano\\PycharmProjects\\botTelegram\\phantomjs-2.1.1-windows\\bin\\phantomjs'

language = 'United States'
year = '2000'
msg_id = 0
keyboards = ['Settings', 'Start', 'Nationality', 'Year', 'United States', 'Italy', 'France', 'England', 'Back', '1900',
             '1920', '1950', '1980', '1990', '2000', '2010', 'Continue']
saluti = ['hi', 'Hi', 'HI', 'hei', 'Hei', 'HEI', 'Hello', 'HELLO']
# db = pd.read_csv(r"C:\Users\Stefano\Desktop\databaseFilmPlotWikipedia.csv", sep=';', header=None)
# idf = keywordGenerator(db, 17477)
idf = []

with open('C:/Users/Stefano/PycharmProjects/botTelegram/venv/idf_list.csv', 'r') as kw_1:
    csv_reader = csv.reader(kw_1, delimiter=';')
    for row in csv_reader:
        if row[1] != '1' and row[1] != '2' and row[1] != '3':
            idf.append((row[0], row[1]))

nlp = spacy.load("en_core_web_sm")
added = []
second_time = False


def on_chat_message(msg):
    global language
    global year
    global no_genre
    global titles_
    global previous_msg
    content_type, chat_type, chat_id = telepot.glance(msg)
    if msg['text'] == '/start' or msg['text'] in saluti:
        bot.sendMessage(chat_id, "Hi dear! Let's start!\n")
        time.sleep(1)
        bot.sendMessage(chat_id, "WELCOME TO MOVIE ADVISOR! \n\nTold me what kind of movies you want to see"
                                 "\nWrite a short description about the type of film you want to see"
                                 "\n\nDefault Year: 2000\n\n",
                        reply_markup=k1)
        time.sleep(0.5)
        bot.sendMessage(chat_id, "I'm here I'm listening to you\n")
    else:
        if msg['text'] in keyboards:
            language, year = inlineKeyboardSelector.selectKeyboard(chat_id, msg['text'], language, year)
        else:
            if msg['text'] == 'Give me other results':
                no_genre = True
                msg['text'] = previous_msg
                final_query, too_much = qG.queryConstructor(msg['text'], idf, language, year, no_genre, '6')
            else:
                no_genre = False
                titles_ = []
                previous_msg = msg['text']
                final_query, too_much = qG.queryConstructor(msg['text'], idf, language, year, no_genre, '3')
            if final_query != '' and len(msg['text'].split(' ')) > 2:
                a = randint(1, 3)
                if a == 1:
                    bot.sendMessage(chat_id, "Good! Give me a few seconds to look for some movies to recommend..\n")
                elif a == 2:
                    bot.sendMessage(chat_id, "All right! I'll try to find some movie for you..\n")
                else:
                    bot.sendMessage(chat_id, "Ok! Let me think....\n")
                sparql.setQuery(final_query)
                sparql.setReturnFormat(JSON)
                ret = sparql.query().convert()
                abstracts = []
                links = []
                titles = []
                result_checker = False
                limit_value = 0
                count = 0
                for result in ret["results"]["bindings"]:
                    print(str(result["movie_title"]["value"]) + ' -> ' + str(result['score']['value']) + '')
                    if str(result["movie_title"]["value"]) != 'The Cutter':
                        if count == 0 or int(result['score']['value']) >= limit_value:
                            titles.append(result["movie_title"]["value"])
                            abstracts.append(
                                (result["abstract"]["value"][:300] + '....') if len(
                                    result["abstract"]["value"]) > 300 else
                                result["abstract"]["value"])
                            links.append(result["link"]["value"])
                            result_checker = True
                            if count == 0:
                                top_value = int(result['score']['value'])
                                if 0 <= top_value <= 4:
                                    limit_value = -4
                                elif top_value > 0:
                                    limit_value = int(top_value / 2)
                                else:
                                    limit_value = int(top_value * 2)
                            count += 1
                if result_checker is True:
                    bot.sendMessage(chat_id, "I suggest you..\n\n")
                    i = 0
                    if no_genre is False:
                        added.clear()
                    for x in titles:
                        if x not in added:
                            bot.sendMessage(chat_id, titles[i].upper() + '\n\n' + abstracts[i] + '\n\n' + links[i])
                            added.append(x)
                        i += 1
                    titles_ = titles
                    if too_much is True:
                        bot.sendMessage(chat_id,
                                        "WARNING! You have written too much text, the search excluded less significant keywords ")
                    if no_genre is False:
                        bot.sendMessage(chat_id, "Write again if you want to search another films\nOr try 'Give me other results!'", reply_markup=k7)
                    else:
                        bot.sendMessage(chat_id, "Write again if you want to search another films", reply_markup=k8)
                else:
                    bot.sendMessage(chat_id, "Couldn't extract enough keywords, try rewriting the message",
                                   reply_markup=k6)
            else:
                bot.sendMessage(chat_id, "Couldn't extract enough keywords, try rewriting the message", reply_markup=k6)


bot = telepot.Bot("1040963180:AAGh02okW5n0I3wJf0z9EzK7Xh1uGuwis_0")
MessageLoop(bot, on_chat_message).run_as_thread()
print("READY!")

while 1:
    time.sleep(1)
