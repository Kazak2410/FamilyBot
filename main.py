import os
from datetime import datetime, timedelta
import asyncio
from db import DataBase
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler


load_dotenv()

bot = Bot(os.getenv("TOKEN"))
db = Dispatcher(bot)
database = DataBase("family")
number = 0


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
    message = f"Сегодня дежурит на кухне @{user}"
    await bot.send_message(-945893857, message)


scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")
scheduler.add_job(send_message_cron, trigger="cron", hour=17, minute=23,
                  start_date=datetime.now(), kwargs={"bot": bot})
scheduler.start()


async def on_startup(_):
    if not database.check_table():
        database.create_table()
    print("The bot has been connected!")


@db.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Поздравляем! Ты присоединился к системе управления домашними обязанностями.")
    print(get_users())
    database.insert_user(message)


@db.message_handler(commands=["list"])
async def cmd_list(message: types.Message):
    await message.answer(database.get_users())


if __name__ == "__main__":
    executor.start_polling(db, on_startup=on_startup, skip_updates=True)
