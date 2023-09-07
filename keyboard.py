from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def kb_register():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/register'))
    return kb
