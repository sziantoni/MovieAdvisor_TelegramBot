import time
import urllib.error
import urllib.request
from pprint import pprint
import pandas as pd
import plotly.express as px
import bs4 as bs
import sklearn as sklearn
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy
import re

stopwords = open("stopwords.txt").read().splitlines()
whitelist = set('abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ')
db = pd.read_csv(r"C:\Users\Stefano\Desktop\films.csv", sep=';', header=None)

bagsOfWords = numpy.empty(shape=(4806,2), dtype=object)
titles = []
y=0
for x in db[0]:
    bagsOfWords[y][0] = str(x)
    titles.append(str(x))
    y+=1
y=0
for x in db[1]:
    plot = str(x)
    plot = ''.join(filter(whitelist.__contains__, plot))
    bagsOfWords[y][1] = plot.lower().split(' ')
    y+=1

uniqueWords = bagsOfWords[0][1]

for x in range(1, len(bagsOfWords)):
    uniqueWords = set(uniqueWords).union(set(bagsOfWords[x][1]))

#creo il dizionario con le occorrenze di ogni parola

dictionary = numpy.empty(shape=(4806,2), dtype=object)

y=0
for x in range(0, len(bagsOfWords)):
    numOfWords = dict.fromkeys(uniqueWords, 0)
    for word in bagsOfWords[y][1]:
        numOfWords[word] += 1
    dictionary[y][0] = titles[y]
    dictionary[y][1] = numOfWords
    y += 1

#calcolo di tf-idf

#TF
def TFcomputation(words, bag):
    TFcount= {}
    bagCount = len(bag)
    for word in words:
        TFcount[word] = words[word] / len(bag)
    return TFcount

#IDF
def IDFcomputation(documents):
    import math
    NDocs = len(documents)
    idfDict = dict.fromkeys(documents[0].keys(), 0)
    for document in documents:
        for word, val in document.items():
            if val > 0:
                idfDict[word] += 1

    for word, val in idfDict.items():
        idfDict[word] = math.log(NDocs / float(val))
    return idfDict

TFIDF_Array = numpy.empty(shape=(4806,2), dtype=object)
#TF-IDF
def TFIDF_Matrix_Computation(TFMatrix, Idf):
    y=0
    for i in TFMatrix[:,1]:
        tfidf = {}
        for word, val in i.items():
            if val > 0:
                tfidf[word] = val * Idf[word]
            else:
                tfidf[word] = 0
        TFIDF_Array[y][0]= titles[y]
        TFIDF_Array[y][1]= sorted(tfidf.items(), key=lambda values: values[1], reverse=True)
        y += 1

TFMatrix = numpy.empty(shape=(4806,2), dtype=object)

for x in range(0, len(bagsOfWords)):
    tfCurrent = TFcomputation(dictionary[x][1], bagsOfWords[x][1])
    TFMatrix[x][0] = titles[x]
    TFMatrix[x][1] = tfCurrent

Idf = IDFcomputation(dictionary[:,1])

TFIDF_Matrix_Computation(TFMatrix, Idf)

keywords = []

for i in range(0, len(TFIDF_Array)):
   words = TFIDF_Array[i][1]
   for j in range(0, 9):
       if len(words[j][0])>2:
           if words[j][0] not in stopwords:
               keywords.append(words[j][0])

#Lista delle 25.000 parole chiave migliori usate per descrivere i 5000 film
keywords = sorted(list(dict.fromkeys(keywords)))

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)  # glance lavora con ogni tipo di messaggio
    # pulsante che ho creato
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Clicca Qui", callback_data='press')]
    ])
    pprint(msg['text'])
    saluti = ["Ciao", "Salve", "Hi", "ciao", "salve", "hi"]
    if any(x in msg['text'] for x in saluti):
        bot.sendMessage(chat_id, "Tell me")
    else:
        w = msg['text'].lower().split(' ')
        kw = []
        kw_string = ''
        for word in w:
            if word in keywords:
                kw.append(word)
                kw_string = kw_string + str(word) + ' | '
        '''
        if content_type == 'text':
            bot.sendMessage(chat_id, "Non scrivere un messaggio usa la Inline Keyboard", reply_markup=keyboard)
        '''
        # ottenere le stats di youtube dato username
        try:
            '''
            sauce = urllib.request.urlopen('https://www.instagram.com/' + msg['text'] + '/').read()
            soup = bs.BeautifulSoup(sauce, 'html.parser')
            # Cercare i tag span con classe 'abput-stats' (su yt sono chiamate cosi le info nell HTML)
            for item in soup.find_all('meta'):
                if "Follower" in str(item):
                    if "link" not in str(item):
                        print(str(item))
                        answer = str(item)
                        answer = answer.replace(' - See Instagram photos and videos from', "")
                        answer = answer.replace('" property="og:description"/>', "")
                        answer = answer.replace('<meta content="', "")
                        answers = answer.split("Posts")
                        bot.sendMessage(chat_id, "Stats-> " + answers[0] + "Posts")
                        bot.sendMessage(chat_id, "Nome-> " + answers[1])
            
            #manda DOCUMENTO ALL'UTENTE CON I DATI PRELEVATI
            filename = "report"+msg['text']+".txt"
            with open(filename, "a") as out:
                out.write(answer)
    
            bot.sendDocument(chat_id, open(filename, 'rb'))
            
            '''
            bot.sendMessage(chat_id, 'KeyWords: ' + kw_string)
        except urllib.error.HTTPError as err:
            if err.code == 404:
                bot.sendMessage(chat_id, "Il profilo IG non è stato trovato :(")
                furl = urllib.request.urlopen(
                    'https://www.corriere.it/methode_image/2019/11/14/Scienze/Foto%20Gallery/Cane6.JPG')
                bot.sendPhoto(chat_id, ('cane.jpg', furl))


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg,
                                                   flavor='callback_query')  # stiamo dicendo applica il metodo glance ma non alla chat come prima ma a un metodo che appunto chiamiamo callback_query e quindi una inline keyboard
    print("Callback Query: ", query_id, from_id, query_data)

    bot.answerCallbackQuery(query_id, text="E bravo")


bot = telepot.Bot("1242680480:AAHqZFER--FBoxgEq_cZIkup2eW49tW5oDQ")
# specifico che devo usare un determinato gestore per la chat e un altro per le inlinequery
MessageLoop(bot, {'chat': on_chat_message, 'callback_query': on_callback_query}).run_as_thread()
print("listening...")

while 1:
    time.sleep(1)
