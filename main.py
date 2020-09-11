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
import keywordConstructor as kc
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy
import re

punctuation = set("!@#$%^&*()_+<>?:.,;")
db = pd.read_csv(r"C:\Users\Stefano\Desktop\films.csv", sep=';', header=None)

keywords = kc.keywordGenerator(db)


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)  # glance lavora con ogni tipo di messaggio
    # pulsante che ho creato
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Clicca Qui", callback_data='press')]
    ])
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
    try:
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
