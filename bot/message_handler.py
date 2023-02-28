from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from auxiliary.all_markups import *
from auxiliary.funcs import print_log_info
from auxiliary.req_data import *
from auxiliary.req_data import director_name
from bot import (
    doctor_handler as doch,
    admin_handler as ah,
    director_handler as dirh,

)
from workers import db_worker as dbw


# класс для регистрации состояния сообщений пользователя (используется везде,
# где нужно обрабатывать текстовые сообщения от пользователя)
class Response(StatesGroup):
    authorization_handler = State()
    authorization_password_handler = State()


async def authorization_handler(message: types.Message, state: FSMContext):
    """ Функция-обработчик сообщения после нажатия кнопки "Получить доступ" """
    authorization_response = message.text
    await state.update_data(user_response=authorization_response)

    if authorization_response == 'Получить доступ':
        message_text = f"Введите временный пароль. " \
                       f"Его нужно уточнить у {director_name}"
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=message_text,
            parse_mode='Markdown',
            reply_markup=markup_cancel
        )
        await Response.authorization_password_handler.set()
    elif authorization_response == 'Отмена':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Хорошо',
            parse_mode='Markdown',
            reply_markup=markup_new_user
        )
        await state.finish()


async def authorization_password_handler(message: types.Message,
                                         state: FSMContext):
    """ Функция-обработчик временного пароля и добавления пользователя в бд """
    authorization_password_response = message.text
    await state.update_data(user_response=authorization_password_response)
    # try для корректной обработки/работы данных из бд
    try:
        authorization_password_response = int(authorization_password_response)
    except Exception:
        pass
    if authorization_password_response == 'Отмена':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Хорошо',
            parse_mode='Markdown',
            reply_markup=markup_new_user
        )
        response = Response.authorization_handler
    else:
        temporary_password = await dbw.get_data(
            field='id',
            what_need='id',
            value=authorization_password_response)
        if authorization_password_response == temporary_password:
            await dbw.update_user('id', temporary_password, message.chat.id)
            result = await dbw.get_data(
                field='id',
                what_need='post',
                value=message.chat.id
            )

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
            msg_new_user = 'New user log in and added to database'
            print_log_info(message, msg_new_user)
        else:
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Пароль введен неверно',
                parse_mode='Markdown',
                reply_markup=markup_new_user
            )
            msg_new_user = 'User unsuccessfully tried to log in'
            print_log_info(message, msg_new_user)
            response = Response.authorization_handler

    await response.set()


def register_handlers_authorization(dp: Dispatcher):  # noqa
    """ Регистратор данных для main_bot.py """
    dp.register_message_handler(
        authorization_handler,
        state=Response.authorization_handler
    )
    dp.register_message_handler(
        authorization_password_handler,
        state=Response.authorization_password_handler
    )
