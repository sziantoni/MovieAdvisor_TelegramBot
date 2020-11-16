import time
import telepot
from telepot.loop import MessageLoop
import sparql
from SPARQLWrapper import SPARQLWrapper, JSON
import spacy
import queryGenerator as qG
from Testing import testerResult as tR, tester as tG
from keyboards import k1, k6
import inlineKeyboardSelector
import csv

language = 'United States'
year = '1950'
msg_id = 0
s = sparql.Service(endpoint='http://dbpedia.org', qs_encoding="uft-8", method="GET")
sparql = SPARQLWrapper(endpoint='http://dbpedia.org/sparql')
keyboards = ['Settings', 'Start', 'Nationality', 'Year', 'United States', 'Italy', 'France', 'England', 'Back', '1900',
             '1920', '1950', '1980', '1990', '2000', '2010', 'Continue']
#db = pd.read_csv(r"C:\Users\Stefano\Desktop\wikidata15000.csv", sep=';', header=None)
#idf = kc.keywordGenerator(db, 15000)

idf = []
with open('kw1.csv', 'r') as kw_1:
    csv_reader = csv.reader(kw_1, delimiter=';')
    for row in csv_reader:
        idf.append((row[0], row[1]))

nlp = spacy.load("en_core_web_sm")
sparql.setTimeout(50000)

f = open("results.txt", "w+")

def on_chat_message(msg):
    global language
    global year
    global no_genre
    global titles_
    global previous_msg
    content_type, chat_type, chat_id = telepot.glance(msg)
    if msg['text'] == '/start':
        bot.sendMessage(chat_id, "WELCOME TO MOVIE ADVISOR! \n\nTold me what kind of movies you want to see"
                                 "\nWrite a short description about the type of film you want to see\nthe longer"
                                 " description provided, the better result you get\n\nDefault Nation: United States\n\nDefault Year: 2000",
                        reply_markup=k1)
    else:
        if msg['text'] in keyboards:
            language, year = inlineKeyboardSelector.selectKeyboard(chat_id, msg['text'], language, year)
        elif msg['text'] == 'Give me other results':
            final_query, too_much = qG.queryConstructor(previous_msg, idf, language, year, True, '10')
            print(final_query)
            sparql.setQuery(final_query)
            sparql.setReturnFormat(JSON)
            ret = sparql.query().convert()
            abstracts = []
            links = []
            titles = []
            result_checker = False
            previous_value = 0
            count = 0
            for result in ret["results"]["bindings"]:
                print(str(result["movie_title"]["value"]) + ' -> ' + str(result['score']['value']))
                if (int(result['score']['value']) > previous_value - 30 or (
                        count == 0 and int(result['score']['value']) > 10) ) and result["movie_title"]["value"] not in titles_ and count < 3:
                    titles.append(result["movie_title"]["value"])
                    abstracts.append(
                        (result["abstract"]["value"][:300] + '....') if len(result["abstract"]["value"]) > 300 else
                        result["abstract"]["value"])
                    links.append(result["link"]["value"])
                    result_checker = True
                    previous_value = int(result['score']['value'])
                    count += 1
            if result_checker is True:
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
                bot.sendMessage(chat_id, "Couldn't extract enough keywords, try rewriting the message",
                                reply_markup=k6)
        else:
            no_genre = False
            titles_ = []
            too_much = False
            final_query, too_much, tester1, keywords = tG.queryConstructor(msg['text'], idf, language, year, False, '5')
            previous_msg = msg['text']
            if final_query != '':
                bot.sendMessage(chat_id, "OK give me a few seconds to look for some movies to recommend..\n")
                #print(final_query)
                sparql.setQuery(final_query)
                sparql.setReturnFormat(JSON)
                ret = sparql.query().convert()
                '''
                abstracts = []
                links = []
                titles = []
                result_checker = False
                previous_value = 0
                count = 0
                '''
                f.write("-----------------------------------------------------------------\n")
                f.write("QUERY: " + msg['text'])
                f.write(" ")
                tr = tR.manageResults(ret, tester1, keywords, f)
                f.write("-----------------------------------------------------------------\n")
                '''
                for result in ret["results"]["bindings"]:
                    #print(str(result["movie_title"]["value"]) + ' -> ' + str(result['score']['value']))
                    if int(result['score']['value']) > previous_value - 30 or (
                            count == 0 and int(result['score']['value']) > 10) or int(result['score']['value']) > 90:
                        titles.append(result["movie_title"]["value"])
                        abstracts.append(
                            (result["abstract"]["value"][:300] + '....') if len(result["abstract"]["value"]) > 300 else
                            result["abstract"]["value"])
                        links.append(result["link"]["value"])
                        result_checker = True
                        previous_value = int(result['score']['value'])
                        count += 1
                if result_checker is True:
                    bot.sendMessage(chat_id, "I suggest you..\n\n")
                    i = 0
                    added = []
                    for x in titles:
                        if x not in added:
                            bot.sendMessage(chat_id, titles[i].upper() + '\n\n' + abstracts[i] + '\n\n' + links[i])
                            added.append(x)
                        i += 1
                    titles_ = titles
                    if too_much is True:
                        bot.sendMessage(chat_id,
                                        "WARNING! You have written too much text, the search excluded less significant keywords ")
                
                    bot.sendMessage(chat_id, "Write again if you want to search another films", reply_markup=k7)
                else:
                    bot.sendMessage(chat_id, "Couldn't extract enough keywords, try rewriting the message",
                                    reply_markup=k6)
                '''
                bot.sendMessage(chat_id, 'done')
            else:
                bot.sendMessage(chat_id, "Couldn't extract enough keywords, try rewriting the message", reply_markup=k6)


bot = telepot.Bot("1040963180:AAGh02okW5n0I3wJf0z9EzK7Xh1uGuwis_0")
MessageLoop(bot, on_chat_message).run_as_thread()
print("READY!")

while 1:
    time.sleep(1)
