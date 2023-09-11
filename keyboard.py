from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def register_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/register'))
    return kb


def yes_no_kb():
    list_answers = InlineKeyboardMarkup(row_width=2)
    list_answers.add(InlineKeyboardButton("Да, могу", callback_data="yes"),
                     InlineKeyboardButton("Нет, не могу ", callback_data="no"))
    return list_answers
