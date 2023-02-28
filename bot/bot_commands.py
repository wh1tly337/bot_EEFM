from loguru import logger

from auxiliary.all_markups import *
from auxiliary.funcs import print_log_info
from auxiliary.req_data import *
from bot import (
    message_handler as mh,
    doctor_handler as doch,
    admin_handler as ah,
    director_handler as dirh,
)
from workers import db_worker as dbw


async def start_message(message: types.Message):
    """ Функция отвечающая за команду /start """
    result = await dbw.get_data(
        field='id',
        what_need='id',
        value=message.chat.id
    )
    if message.from_user.id != result:  # проверка на нового юзера
        msg_new_user_start = 'New user start bot'
        print_log_info(message, msg_new_user_start)

        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f"{message.from_user.full_name}"
                 f", к сожалению у вас нет доступа к данному боту",
            reply_markup=markup_new_user
        )

        response = mh.Response.authorization_handler
    else:
        result = await dbw.get_data(
            field='id',
            what_need='post',
            value=message.chat.id
        )
        logger.info(f'Logged user post | {result}')

        markup_to_handlers = {  # noqa
            'doctor': {
                'markup': markup_doctor,
                'response': doch.Response.doctor_handler
            },
            'admin': {
                'markup': markup_admin,
                'response': ah.Response.admin_message_handler
            },
            'director': {
                'markup': markup_director,
                'response': dirh.Response.register_director_handler
            },
        }
        command_dict = markup_to_handlers.get(result)  # noqa
        if not command_dict:
            command_dict = markup_to_handlers[None]
        markup = command_dict.get('markup')
        response = command_dict.get('response')

        fio = await dbw.get_data('id', message.chat.id)
        appeal = f"{fio[2]} {fio[3]}"
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f"{appeal}, добро пожаловать в бот клиники ИТА!",
            parse_mode='Markdown',
            reply_markup=markup
        )

        await dbw.login_user(message.chat.id)
        msg_log_in = 'User log in'
        print_log_info(message, msg_log_in)

    await response.set()


def register_handlers_default_commands(dp: Dispatcher):  # noqa
    """ Регистратор данных для main_bot.py """
    dp.register_message_handler(
        start_message,
        commands=['start']
    )
