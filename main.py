# -*- coding: utf-8 -*-
import config
import database

import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())



@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        text = f"""<b>🙇‍♂️ Команды админа:
/{config.RASSILKA_COMMAND} ➙ сделать рассылку
/{config.SKOLKO_USEROV} ➙ узнать сколько пользователей в боте</b>"""
        await message.reply(text, parse_mode='html')
    registered = database.add_user_from_database(message.from_user.id, True)
    if registered:
        users_len = len(database.get_all_user_from_database())
        user_name = message.from_user.username
        user_first_name = message.from_user.first_name
        await bot.send_message(config.ADMIN_ID,
            f'<b>🙇‍♂️ Пользователь <a href="t.me/{user_name}">{user_first_name}</a> зарегистрировался!</b>\n👥 Теперь в боте <u>{users_len}</u> пользователей.',
            parse_mode='html', disable_web_page_preview=True)

    gif_path = "data/IMG_1314.gif"
    welcome_text = f"<b>👋Привет!\n🤖Я покажу тебе насколько ты гей.\n💭 Чтобы отправить свой результат в любой чат, введи в поле ввода <code>@{config.BOT_URL[13:]}</code> \n\n✏️ Используй команду /set для изменения результата.\nНапример: <code>/set 100</code></b>"
    try:
        with open(gif_path, 'rb') as gif:
            await bot.send_animation(chat_id=message.chat.id, animation=gif, caption=welcome_text, parse_mode='html')
    except Exception:
        await message.reply(welcome_text, parse_mode='html')
        

    


@dp.message_handler(commands=[config.SKOLKO_USEROV])
async def send_message(message: types.Message):
    user_id = message.from_user.id
    if user_id == config.ADMIN_ID:
        users = database.get_all_user_from_database()
        await message.reply(f"<b>👥 В боте зарегистрировано ⇒ {len(users)} ⇐ пользователей!</b>", parse_mode='html')


@dp.message_handler(commands=['set'])
async def send_message(message: types.Message):
    user_id = message.from_user.id
    try:
        percent = int(message.text.split(" ")[1])
        if percent >= 0 and percent <= 100:
            database.set_user_last_percent(user_id, percent)
            database.set_user_saved_time(user_id)
            await message.reply(f"<b>🏳️‍🌈 Процент твоего гейства теперь {percent}%</b>\nРезультат сохранится {config.SAVED_HOURS} час.", parse_mode='html')
        else:
            await message.reply(f"<b>❌ Не верно оформлена команда!</b>\n🏳️‍🌈 Процент должен быть от 0 до 100!", parse_mode='html')
    except Exception as e:
        await message.reply(f"<b>❌ Не верно оформлена команда!</b>\n💭 Используй команду /set для изменения результата.\n\nНапример: <code>/set 100</code>", parse_mode='html')


@dp.inline_handler()
async def inline_query(query: types.InlineQuery):
    user_id = query.from_user.id
    user_name = query.from_user.username
    user_first_name = query.from_user.first_name
    current_time = datetime.now()
    registered = database.add_user_from_database(user_id, False)
    if registered:
        users_len = len(database.get_all_user_from_database())
        await bot.send_message(config.ADMIN_ID,
            f'<b>🙇‍♂️ Пользователь <a href="t.me/{user_name}">{user_first_name}</a> зарегистрировался!</b>\n👥 Теперь в боте <u>{users_len}</u> пользователей.',
            parse_mode='html', disable_web_page_preview=True)

    saved_time = database.get_user_saved_time(user_id)
    saved_percent = database.get_user_last_percent(user_id)

    if (current_time - saved_time) < config.RESULT_LIFETIME:
        random_percent = saved_percent
    else:
        random_percent = random.randint(0, 100)
        database.set_user_last_percent(user_id, random_percent)
        database.set_user_saved_time(user_id)

    inline_kb = InlineKeyboardMarkup()
    to_bot = InlineKeyboardButton("✏️ Изменить результат", url=config.BOT_URL)
    share = InlineKeyboardButton("💭 Поделиться", switch_inline_query="")
    inline_kb.add(to_bot)
    inline_kb.add(share)

    message_content = InputTextMessageContent(message_text=f'<b><a href="t.me/{user_name}">{user_first_name}</a> гей на {random_percent}%</b>', parse_mode='html', disable_web_page_preview=True)

    result = types.InlineQueryResultArticle( id='1', title=f"🏳️‍🌈 Насколько я гей?",
        description="👇🏻 Нажми, чтобы отправить результат", thumb_url=config.GAY_IMAGE_URL,
        input_message_content=message_content, reply_markup=inline_kb
    )
    
    await query.answer([result], cache_time=1) 



@dp.message_handler(commands=[config.RASSILKA_COMMAND])
async def send_message(message: types.Message):
    user_id = message.from_user.id
    if user_id == config.ADMIN_ID:
        database.set_user_menu(user_id, "РАССЫЛКА")
        await message.answer(f"<b>✏️ Отправь сообщение которое отправится всем пользователям бота!</b>", parse_mode="html")


@dp.message_handler(content_types=[types.ContentType.TEXT, types.ContentType.PHOTO, types.ContentType.VIDEO])
async def without_puree(message: types.Message):
    user_id = message.from_user.id
    if database.get_user_menu(user_id) == "РАССЫЛКА":
        mailing = 0
        try:
            users = database.get_all_user_from_database()
            for user in users:
                await message.copy_to(user[0])
                mailing += 1
        except Exception as ex:
            pass

        database.set_user_menu(user_id, "main_menu")
        await message.answer(f"<b>📩 Доставлено {mailing} из {len(users)} сообщений!</b>", parse_mode="html")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)