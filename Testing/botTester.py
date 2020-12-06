import csv
from datetime import datetime, timedelta
import numpy
from selenium import webdriver
import time
import json

query = []
with open('Testing/actionQuery.csv', 'r') as kw_3:
    csv_reader = csv.reader(kw_3, delimiter=';')
    for row in csv_reader:
        query.append(row)
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
    time.sleep(70)


time.sleep(30)

for q in query:
    queryBot(q)

driver.quit()
