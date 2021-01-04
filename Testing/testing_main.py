import time
import telepot
from telepot.loop import MessageLoop
import sparql
from SPARQLWrapper import SPARQLWrapper, JSON
import spacy
from Testing import testerResult as tR, tester as tG
from keyboards import k1, k6, k7
import inlineKeyboardSelector
import csv

f = open('results_total_key.txt', 'w', newline='')
nlp = spacy.load("en_core_web_sm")
language = 'United States'
year = '2000'
msg_id = 0
s = sparql.Service(endpoint='http://dbpedia.org', qs_encoding="uft-8", method="GET")
sparql = SPARQLWrapper(endpoint='http://dbpedia.org/sparql')
keyboards = ['Settings', 'Start', 'Nationality', 'Year', 'United States', 'Italy', 'France', 'England', 'Back', '1900',
             '1920', '1950', '1980', '1990', '2000', '2010', 'Continue']
saluti = ['hi', 'Hi', 'HI', 'hei', 'Hei', 'HEI', 'Hello', 'HELLO']
# db = pd.read_csv(r"C:\Users\Stefano\Desktop\wikidata15000.csv", sep=';', header=None)
# idf = kc.keywordGenerator(db, 15000)


idf = []
check = []

with open('C:/Users/Stefano/PycharmProjects/botTelegram/venv/idf_list.csv', 'r') as kw_1:
    csv_reader = csv.reader(kw_1, delimiter=';')
    count = 0
    for row in csv_reader:
        '''
        doc = nlp(row[0])
        app = ''
        for t in doc:
            app = t.lemma_
            app1 = app[0].upper() + app[1:(len(app))]
        if app in words.words():
            check.append((app, row[1]))
        if app1 in words.words():
            check.append((app, row[1]))
        if app[len(app)-2:len(app)] == 'ed' or app1[len(app1)-2:len(app1)] == 'ed':
            if app[0:len(app)-2] in words.words():
                check.append((app, row[1]))
        '''
        idf.append((row[0], row[1]))
    print(count)
'''
with open('C:/Users/Stefano/PycharmProjects/botTelegram/Testing/keywordEn_GB.csv', 'r') as kw_1:
    csv_reader = csv.reader(kw_1, delimiter=';')
    count = 0
    for row in csv_reader:
        idf.append((row[0], row[1]))

f = open('keywordEn_GB.csv', 'w', newline='')
w = csv.writer(f, delimiter=';' )
for s in check:
    w.writerow((s[0],s[1]))
'''

nlp = spacy.load("en_core_web_sm")
sparql.setTimeout(50000)

list_of_result = []
query_2 = []

with open('C:/Users/Stefano/PycharmProjects/botTelegram/test_keyword.csv', 'r') as kw_5:
    csv_reader = csv.reader(kw_5, delimiter=';')
    for row in csv_reader:
        row_0 = ''
        if 'ï»¿' in row[0]:
            row_0 = row[0].replace('ï»¿', '')
        else:
            row_0 = row[0]
        clean = str(row[1]).replace("  ", " ")
        keyword = row[2].split(' ')
        for k in keyword:
            if '_' in k:
                k = k.replace('-', '')
        query_string = str(row_0).lower() + ' ' + str(clean)
        query_2.append((query_string, keyword))


def on_chat_message(msg):
    global language
    global year
    global no_genre
    global titles_
    global previous_msg
    content_type, chat_type, chat_id = telepot.glance(msg)
    if msg['text'] == '/start' or msg['text'] in saluti:
        bot.sendMessage(chat_id, "WELCOME TO MOVIE ADVISOR! \n\nTold me what kind of movies you want to see"
                                 "\nWrite a short description about the type of film you want to see"
                                 "\n\nDefault Nation: United States\n\nDefault Year: 2000",
                        reply_markup=k1)
    elif msg['text'] == 'close file':
        f.close()
        bot.sendMessage(chat_id, 'closed')
    else:
        if msg['text'] in keyboards:
            language, year = inlineKeyboardSelector.selectKeyboard(chat_id, msg['text'], language, year)
        elif msg['text'] == 'calculate result':
            TP = 0
            FP = 0
            TN = 0
            FN = 0
            for l in range(0, len(list_of_result) - 1):
                take = []
                splitted = list_of_result[l][0].split(' ')
                selected = [i[0] for i in list_of_result[l][1]]
                for s in splitted:
                    nounerr = []
                    if " " in s:
                        nounerr = s.split(" ")
                    if s != ' ':
                        if s in selected and s in query_2[l][1] and s not in take:
                            TP += 1
                            take.append(s)
                        elif s in selected and s not in query_2[l][1] and len(
                                nounerr) < 2 and s != 'movie' and s not in take:
                            FP += 1
                            take.append(s)
                        elif s in list_of_result[l][2] and s not in query_2[l][1] and s not in take:
                            TN += 1
                            take.append(s)
                        elif s in query_2[l][1] and s not in selected and s not in take:
                            FN += 1
                            take.append(s)
            print('FN:' + str(FN))
            print('TN:' + str(TN))
            print('TP:' + str(TP))
            print('FP:' + str(FP))
            precision = TP / (TP + FP)
            recall = TP / (TP + FN)
            print('Precision: ' + str(precision))
            print('Recall: ' + str(recall))
            print('F-Measure: ' + str((2 * precision * recall) / (precision + recall)))

        else:
            no_genre = False
            titles_ = []
            final_query, too_much, tester1, keywords, top_kw, nounArray, selected_gnr = tG.queryConstructor(msg['text'],
                                                                                                            idf,
                                                                                                            language,
                                                                                                            year,
                                                                                                            False, '5')
            previous_msg = msg['text']
            f.write(final_query + '\n')
            f.write('Keywords: \n')
            for k in keywords:
                f.write(str(k) + '\n')
            for n in nounArray:
                f.write(str(n) + '\n')
            f.write('Top Kw: ' + str(top_kw))
            if final_query != '' and len(msg['text'].split(' ')) > 2:
                bot.sendMessage(chat_id, "OK give me a few seconds to look for some movies to recommend..\n")
                sparql.setQuery(final_query)
                sparql.setReturnFormat(JSON)
                ret = sparql.query().convert()
                abstracts = []
                links = []
                titles = []
                result_checker = False
                limit_value = 0
                count = 0
                tR.manageResults(ret, tester1, keywords)
                for result in ret["results"]["bindings"]:
                    f.write(str(result["movie_title"]["value"]) + ' -> ' + str(result['score']['value']) + '\n')
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
                                if 0 <= top_value <= 2:
                                    limit_value = -4
                                elif top_value > 0:
                                    limit_value = int(top_value / 2)
                                else:
                                    limit_value = int(top_value * 2)
                            count += 1
                            f.write("Top KW VALUE " + str(result["top_kw"]["value"]) + '\n')
                            f.write('LINK: ' + result["link"]["value"] + '\n')
                            f.write('SUBJECT: ' + result["list"]["value"] + '\n')
                f.write('LIMIT:' + str(limit_value))
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
            else:
                bot.sendMessage(chat_id, "Couldn't extract enough keywords, try rewriting the message", reply_markup=k6)

            # TEST SULLE KEYWORD
            kw_string = ''
            result = []
            rest_of_words = []
            for k in keywords:
                kw_string = kw_string + ' ' + k[0]
            for n in nounArray:
                tuples = (n, 0.0)
                keywords.append(tuples)
                n = n.replace(" ", "_")
                kw_string = kw_string + ' ' + n
            for s in selected_gnr:
                keywords.append(s)
                kw_string = kw_string + ' ' + s[0]
            keywords.append(top_kw)
            kw_string = kw_string + ' ' + top_kw[0]
            lista = msg['text'].split(' ')
            checker = [i[0] for i in keywords]
            for l in lista:
                if l not in checker:
                    rest_of_words.append(l)
            list_of_result.append((msg['text'], keywords, rest_of_words))
            bot.sendMessage(chat_id, str(
                ' Keywords: ' + kw_string))


bot = telepot.Bot("1040963180:AAGh02okW5n0I3wJf0z9EzK7Xh1uGuwis_0")
MessageLoop(bot, on_chat_message).run_as_thread()
print("READY!")

while 1:
    time.sleep(1)
