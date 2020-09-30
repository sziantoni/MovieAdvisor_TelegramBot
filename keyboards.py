from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup


keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Settings", callback_data='setting'),
                                                  InlineKeyboardButton(text="Start", callback_data='start')], ])
keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Nationality", callback_data='lang'),
     InlineKeyboardButton(text="Year", callback_data='year')], ])

keyboard2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="United States", callback_data='usa'),
     InlineKeyboardButton(text="Italy", callback_data='ita'),
     InlineKeyboardButton(text="France", callback_data='fr'),
     InlineKeyboardButton(text="England", callback_data='eng'),
     InlineKeyboardButton(text="Back", callback_data='back')]])

keyboard3 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Back", callback_data='back')]])

keyboard4 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1900", callback_data='1900'),
     InlineKeyboardButton(text="1920", callback_data='1920'),
     InlineKeyboardButton(text="1950", callback_data='1950'),
     InlineKeyboardButton(text="1980", callback_data='1980'),
     InlineKeyboardButton(text="1990", callback_data='1990'),
     InlineKeyboardButton(text="2000", callback_data='2000'),
     InlineKeyboardButton(text="2005", callback_data='2005'),
     InlineKeyboardButton(text="2010", callback_data='2010'),
     InlineKeyboardButton(text="Back", callback_data='back')
     ]])
keyboard5 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Settings", callback_data='setting')]])