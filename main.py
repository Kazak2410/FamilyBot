import os
from datetime import datetime
import asyncio
from db import DataBase
from keyboard import kb_register
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext


load_dotenv()

storage = MemoryStorage()
bot = Bot(os.getenv("TOKEN"))
db = Dispatcher(bot, storage=MemoryStorage())
database = DataBase("family")
number = 0


class ProfileStatesGroup(StatesGroup):
    name = State()
    photo = State()


def get_users():
    users = database.get_users().split()
    return users

async def send_message_cron(bot: Bot):
    global number
    if number < len(get_users()):
        user = get_users()[number]
    else:
        number = 0
        user = get_users()[number]
    number += 1
    message = f"Сегодня дежурит на кухне {user}"
    await bot.send_message(-945893857, message)


scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")
scheduler.add_job(send_message_cron, trigger="cron", hour=19, minute=54,
                  start_date=datetime.now(), kwargs={"bot": bot})
scheduler.start()


async def on_startup(_):
    if not database.check_table():
        database.create_table()
    print("The bot has been connected!")


@db.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Приветствую! Если ты хочешь присоединиться к системе управления домашними обязанностями, нажми кнопку «/register».",
                         reply_markup=kb_register())


@db.message_handler(commands=["register"])
async def register_user(message: types.Message):
    await message.answer("Укажи свое имя")
    await ProfileStatesGroup.name.set()


@db.message_handler(state=ProfileStatesGroup.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text

    await message.answer("Отправь свое фото")
    await ProfileStatesGroup.next()


@db.message_handler(content_types=["photo"], state=ProfileStatesGroup.photo)
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["photo"] = message.photo[0].file_id
        file_photo = await bot.download_file_by_id(message.photo[0].file_id)

        with open(f"media/{message.photo[0].file_id}.jpg", "wb") as new_file:
            new_file.write(file_photo.read())

        database.registrate_user(
            name=data["name"], photo=data["photo"]
        )

    await message.answer("Поздравляем вы успешно зарегистрированы!")
    await state.finish()


@db.message_handler(commands=["list"])
async def cmd_list(message: types.Message):
    await message.answer(database.get_users())


if __name__ == "__main__":
    executor.start_polling(db, on_startup=on_startup, skip_updates=True)
