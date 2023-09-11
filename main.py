import os
from datetime import datetime
from db import DataBase
from keyboard import register_kb, yes_no_kb
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text


load_dotenv()

storage = MemoryStorage()
bot = Bot(os.getenv("TOKEN"))
db = Dispatcher(bot, storage=MemoryStorage())
current_user_index = 0


database = DataBase("family")


class ProfileStatesGroup(StatesGroup):
    name = State()
    photo = State()


def get_users():
    users = database.get_users().split()
    return users

async def send_message_cron(bot: Bot):
    global current_user_index
    if current_user_index < len(get_users()):
        user = get_users()[current_user_index]
    else:
        current_user_index = 0
        user = get_users()[current_user_index]
    current_user_index += 1
    message = f"Сегодня дежурит на кухне {user}"
    await bot.send_message(-945893857, message, reply_markup=yes_no_kb())


def setup_scheduler(bot):
    scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")
    scheduler.add_job(send_message_cron, trigger="cron", hour=6, minute=53,
                    start_date=datetime.now(), kwargs={"bot": bot})
    scheduler.start()
    return scheduler


scheduler = setup_scheduler(bot)


async def on_startup(_):
    if not database.check_table():
        database.create_table()
    print("The bot has been connected!")


@db.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Приветствую! Если ты хочешь присоединиться к системе управления домашними обязанностями, нажми кнопку «/register».",
                         reply_markup=register_kb())


@db.message_handler(commands=["cancel"], state="*")
async def cancel(message: types.Message, state=FSMContext):
    if state is None:
        return

    await state.finish()
    await message.answer("Регистрация прервана")


@db.message_handler(commands=["register"])
async def register_user(message: types.Message):
    await message.answer("Укажи свое имя")
    await ProfileStatesGroup.name.set()


@db.message_handler(lambda message: not message.text.isalpha(), state=ProfileStatesGroup.name)
async def check_name(message: types.Message):
    await message.answer("Имя введено не корректно, отправьте еще раз!")


@db.message_handler(state=ProfileStatesGroup.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text

    await message.answer("Отправь свое фото")
    await ProfileStatesGroup.next()


@db.message_handler(lambda message: not message.photo, state=ProfileStatesGroup.photo)
async def check_photo(message: types.Message):
    await message.answer("Это не фотография!")


@db.message_handler(content_types=["photo"], state=ProfileStatesGroup.photo)
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["photo"] = message.photo[0].file_id
        file_photo = await bot.download_file_by_id(message.photo[0].file_id)

        with open(f"media/images/{message.photo[0].file_id}.jpg", "wb") as new_file:
            new_file.write(file_photo.read())

        database.registrate_user(
            user_id=message.from_user.id,
            name=data["name"],
            photo=data["photo"]
        )

    await message.answer("Поздравляем вы успешно зарегистрированы!")
    await state.finish()


@db.message_handler(commands=["list"])
async def users_list(message: types.Message):
    users = "Список участников:\n" + " \n".join(user for user in get_users())
    await message.answer(users)


@db.callback_query_handler()
async def personal_account(callback_query: types.CallbackQuery):
    if callback_query.data == "yes":
        pass
    elif callback_query.data == "no":
        await send_message_cron(bot)


if __name__ == "__main__":
    executor.start_polling(db, on_startup=on_startup, skip_updates=True)
