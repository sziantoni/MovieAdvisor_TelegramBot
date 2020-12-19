import csv
from datetime import datetime, timedelta
from random import random, randint

import numpy
from selenium import webdriver
import time
import json

query = []
query_2 = []
query_3 = []
'''
#TEST CON QUERY SCRITTE A MANO
with open('Testing/nuovoTest.csv', 'r') as kw_3:
    csv_reader = csv.reader(kw_3, delimiter=';')
    for row in csv_reader:
        query.append(row)

#TEST CON KEYWORD DI IMDB
with open('C:/Users/Stefano/PycharmProjects/botTelegram/TestDaIMDB.csv', 'r') as kw_4:
    csv_reader = csv.reader(kw_4, delimiter=';')
    for row in csv_reader:
        row_0 = ''
        if 'ï»¿' in row[0]:
            row_0 = row[0].replace('ï»¿', '')
        else:
            row_0 = row[0]
        clean = str(row[1]).replace("  ", " ")
        query_string = str(row_0).lower() + ' ' + str(clean)
        query_string.replace("  ", " ")
        query_2.append(query_string)
'''
with open('C:/Users/Stefano/PycharmProjects/botTelegram/testNoGenere.csv', 'r') as kw_5:
    csv_reader = csv.reader(kw_5, delimiter=';')
    for row in csv_reader:
        query_3.append(row)

chrome_diver = 'C:\\Users\\Stefano\\Downloads\\chromedriver.exe'
driver = webdriver.Chrome(chrome_diver)
driver.get('https://web.telegram.org/')


def queryBot(q):
    time.sleep(1)
    select_bot = '//*[@id="ng-app"]/body/div[1]/div[2]/div/div[1]/div[1]/div/input'
    driver.find_element_by_xpath(select_bot).send_keys('@theMovieAdvisor_bot')
    time.sleep(1)
    bot = '//*[@id="ng-app"]/body/div[1]/div[2]/div/div[1]/div[2]/div/div[1]/ul/li/a'
    driver.find_element_by_xpath(bot).click()
    time.sleep(1)
    select_textbox = '//*[@id="ng-app"]/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[2]/div[5]'
    driver.find_element_by_xpath(select_textbox).send_keys(q)
    time.sleep(1)
    invia = '//*[@id="ng-app"]/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[3]/button/span[1]'
    driver.find_element_by_xpath(invia).click()
    time.sleep(60)


time.sleep(35)
print("------------------------------------------------------------------ PRIMO TEST ------------------------------------------------------------------")
print("% Inizio test con Query a mano")
for q in query:
    queryBot(q)
print("---------------------------------------------------------------- FINE PRIMO TEST ----------------------------------------------------------------")
print("------------------------------------------------------------------ SECONDO TEST ------------------------------------------------------------------")
print("% Inizio test con IMDB")
for q_2 in query_2:
    queryBot(q_2)
print("---------------------------------------------------------------- FINE SECONDO TEST ----------------------------------------------------------------")
print("------------------------------------------------------------------ TERZO TEST ------------------------------------------------------------------")
print("% Inizio test con IMDB")
for q_3 in query_3:
    queryBot(q_3)
print("---------------------------------------------------------------- FINE TERZO TEST ----------------------------------------------------------------")
driver.quit()
