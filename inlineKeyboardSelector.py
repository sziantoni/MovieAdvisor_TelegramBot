import telepot
from telepot.namedtuple import ReplyKeyboardRemove

from keyboards import k1, k2, k3, k4, k5

bot = telepot.Bot("1040963180:AAGh02okW5n0I3wJf0z9EzK7Xh1uGuwis_0")


def selectKeyboard(chat_id, text, lang, y):
    language = lang
    year = y
    if text == 'Start' or text == 'Continue':
        bot.sendMessage(chat_id, "Write a movie description")
    elif text == 'Settings':
        bot.sendMessage(chat_id, "Select between Nationality and Year", reply_markup=k2)
    elif text == 'Nationality':
        bot.sendMessage(chat_id, "Nationality available", reply_markup=k3)
    elif text == 'United States':
        language = "United States"
        bot.sendMessage(chat_id, "Nationality changed", reply_markup=k4)
    elif text == 'Italy':
        language = "Italy"
        bot.sendMessage(chat_id, "Nationality changed", reply_markup=k4)
    elif text == 'France':
        language = "France"
        bot.sendMessage(chat_id, "Nationality changed", reply_markup=k4)
    elif text == 'England':
        language = "England"
        bot.sendMessage(chat_id, "Nationality changed", k4)
    elif text == 'Year':
        bot.sendMessage(chat_id, "Choose the year to start from:", reply_markup=k5)
    elif text == 'Back':
        bot.sendMessage(chat_id, "Ok!", reply_markup=ReplyKeyboardRemove())
        bot.sendMessage(chat_id, "WELCOME TO MOVIE ADVISOR! \n\nTold me what kind of movies you want to see"
                                 "\nWrite a short description about the type of film you want to see\nthe longer"
                                 " description provided, the better result you get\n\nGive me a description",
                        reply_markup=k1)
    elif text == '1900':
        year = '1900'
        bot.sendMessage(chat_id, "Year changed", reply_markup=k4)
    elif text == '1920':
        year = '1920'
        bot.sendMessage(chat_id, "Year changed", reply_markup=k4)
    elif text == '1950':
        year = '1950'
        bot.sendMessage(chat_id, "Year changed", reply_markup=k4)
    elif text == '1980':
        year = '1980'
        bot.sendMessage(chat_id, "Year changed", reply_markup=k4)
    elif text == '1990':
        year = '1990'
        bot.sendMessage(chat_id, "Year changed", reply_markup=k4)
    elif text == '2000':
        year = '2000'
        bot.sendMessage(chat_id, "Year changed", reply_markup=k4)
    return language, year
