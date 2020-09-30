import telepot
from keyboards import keyboard, keyboard1, keyboard2, keyboard3, keyboard4, keyboard5

bot = telepot.Bot("1040963180:AAGh02okW5n0I3wJf0z9EzK7Xh1uGuwis_0")


def selectKeyboard(query_data, from_id, lang, y):
    language = lang
    year = y
    if str(query_data) == 'start':
        bot.sendMessage(from_id, "Write a movie description")
    elif str(query_data) == 'setting':
        bot.sendMessage(from_id, "Settings:", reply_markup=keyboard1)
    elif str(query_data) == 'lang':
        bot.sendMessage(from_id, "Nationality available", reply_markup=keyboard2)
    elif str(query_data) == 'usa':
        language = "United States"
        bot.sendMessage(from_id, "Nationality changed", reply_markup=keyboard3)
    elif str(query_data) == 'ita':
        language = "Italy"
        bot.sendMessage(from_id, "Nationality changed", reply_markup=keyboard3)
    elif str(query_data) == 'fr':
        language = "France"
        bot.sendMessage(from_id, "Nationality changed", reply_markup=keyboard3)
    elif str(query_data) == 'eng':
        language = "England"
        bot.sendMessage(from_id, "Nationality changed", keyboard3)
    elif str(query_data) == 'year':
        bot.sendMessage(from_id, "Choose the year to start from:", reply_markup=keyboard4)
    elif str(query_data) == 'back':
        bot.sendMessage(from_id, "WELCOME TO MOVIE ADVISOR! \n\nTold me what kind of movies you want to see"
                                 "\nWrite a short description about the type of film you want to see\nthe longer"
                                 " description provided, the better result you get\n\nGive me a description",
                        reply_markup=keyboard)
    elif str(query_data) == '1900':
        year = '1900'
        bot.sendMessage(from_id, "Year changed", reply_markup=keyboard3)
    elif str(query_data) == '1920':
        year = '1920'
        bot.sendMessage(from_id, "Year changed", reply_markup=keyboard3)
    elif str(query_data) == '1950':
        year = '1950'
        bot.sendMessage(from_id, "Year changed", reply_markup=keyboard3)
    elif str(query_data) == '1980':
        year = '1980'
        bot.sendMessage(from_id, "Year changed", reply_markup=keyboard3)
    elif str(query_data) == '1990':
        year = '1990'
        bot.sendMessage(from_id, "Year changed", reply_markup=keyboard3)
    elif str(query_data) == '2000':
        year = '2000'
        bot.sendMessage(from_id, "Year changed", reply_markup=keyboard3)
    elif str(query_data) == '2005':
        year = '2005'
        bot.sendMessage(from_id, "Year changed", reply_markup=keyboard3)
    elif str(query_data) == '2010':
        year = '2010'
        bot.sendMessage(from_id, "Year changed", reply_markup=keyboard3)
    return language, year
