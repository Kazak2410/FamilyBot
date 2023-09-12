from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def register_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/register'))
    return kb
