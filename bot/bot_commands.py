from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *
from bot import (
    message_handler as mh,
    doctor_handler as doch,
    director_handler as dirh,
    admin_handler as adm
)
from workers import db_worker as dbw


# функция отвечающая за команду /start
@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    result = await dbw.get_data('id', message.chat.id)
    if message.from_user.id != result:
        logger.info(
            f"New user start bot | "
            f"{message.from_user.id}, "
            f"{message.from_user.full_name}, "
            f"{message.from_user.username}"
        )
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f"{message.from_user.full_name}, к сожалению у вас нет доступа к данному боту",
            reply_markup=markup_new_user
        )
        await mh.Response.authorization_handler.set()
        # метод выше начинает считывание последующего сообщения пользователя для его авторизации
        # (нужен для работы функции authorization_handler в файле message_handler.py)
    else:
        logger.info(
            f"User log in | "
            f"{message.from_user.id}, "
            f"{message.from_user.full_name}, "
            f"{message.from_user.username}"
        )

        result = await dbw.get_data('post', message.chat.id)
        if result == 'doctor':
            markup = markup_doctor
            await doch.Response.register_doctor_handler.set()
        elif result == 'admin':
            markup = markup_admin
        else:
            markup = markup_director

        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f"{message.from_user.full_name}, добро пожаловать в бот клиники ИТА!",
            reply_markup=markup
        )


# регистратор передающий данные в main_bot.py
def register_handlers_default_commands(dp: Dispatcher):  # noqa
    dp.register_message_handler(
        start_message,
        commands=['start']
    )
