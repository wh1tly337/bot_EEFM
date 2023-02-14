from loguru import logger
from datetime import datetime

from auxiliary.all_markups import *
from auxiliary.req_data import *
from bot import message_handler as mh
from workers import db_worker as dbw

database = []  # временная бд для проверки всего остального функционала, пока не настроена работа с нормальной бд


# функция отвечающая за команду /start
@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    if message.from_user.id not in database:
        # метод начинает считывание последующего сообщения пользователя
        # для его авторизации 
        # (нужен для работы функции authorization_handler в файле message_handler.py)
        logger.info((
            "New user start bot |",
            message.from_user.id,
            message.from_user.full_name,
            message.from_user.username,
        ))
        msg_dont_have_perm = ' , к сожалению у вас нет доступа к данному боту'
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=message.from_user.full_name + msg_dont_have_perm,
            reply_markup=markup_new_user,
        )
        await mh.Response.authorization_handler.set()
    else:
        logger.info(("User log in |",
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username,
        ))
        msg_hello_new_doc = " , добро пожаловать в бот клиники ИТА!"
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text={message.from_user.full_name} + msg_hello_new_doc,
            reply_markup=markup_test
        )


# регистратор передающий данные в main_bot.py
def register_handlers_default_commands(dp: Dispatcher):  # noqa
    dp.register_message_handler(start_message, commands=['start'])
