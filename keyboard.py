from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_add = KeyboardButton("Add profile")
button_del = KeyboardButton("Delete profile")
button_stat = KeyboardButton("Show statistic")
button_help = KeyboardButton("Help")

all_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button_add).add(button_del).add(button_stat).add(button_help)

button_cancel = KeyboardButton("Cancel")

cancel_kb = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(button_cancel)
