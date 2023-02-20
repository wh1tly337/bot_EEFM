from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *
from bot import (
    message_handler as mh,
    doctor_handler as doch,
    admin_handler as ah,
    director_handler as dirh,
)
from bot.funcs import print_log_info
from workers import db_worker as dbw


# функция отвечающая за команду /start
@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    result = await dbw.get_data(
        field='id',
        what_need='id',
        value=message.chat.id
    )
    if message.from_user.id != result:

        msg_new_user_start = 'New user start bot'
        print_log_info(message, msg_new_user_start)

        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f"{message.from_user.full_name}"
                 f", к сожалению у вас нет доступа к данному боту",
            reply_markup=markup_new_user
        )

        # метод начинает считывание последующего сообщения пользователя
        # для его авторизации (нужен для работы функции authorization_handler
        # в файле message_handler.py)
        await mh.Response.authorization_handler.set()
    else:

        msg_log_in = 'User log in'
        print_log_info(message, msg_log_in)

        result = await dbw.get_data(
            field='id',
            what_need='post',
            value=message.chat.id
        )
        logger.info(f'Logged user post | {result}')
        markup_to_handlers = {
            'doctor': [
                markup_doctor,
                doch.Response.register_doctor_handler.set()
            ],
            'admin': [
                markup_admin,
                ah.Response.admin_message_handler.set()
            ],
            'director': [
                markup_director,
                dirh.Response.register_director_handler.set()
            ],
        }
        markup = markup_to_handlers[result][0]
        response = markup_to_handlers[result][1]
        await response

        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f"{message.from_user.full_name}"
                 f", добро пожаловать в бот клиники ИТА!",
            reply_markup=markup
        )


# регистратор передающий данные в main_bot.py
def register_handlers_default_commands(dp: Dispatcher):  # noqa
    dp.register_message_handler(
        start_message,
        commands=['start']
    )
