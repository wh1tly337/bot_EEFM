from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from auxiliary.all_markups import *
from auxiliary.req_data import *
from auxiliary.req_data import director_name
from bot import (
    doctor_handler as doch,
    admin_handler as ah
)
from bot.funcs import print_log_info
from workers import db_worker as dbw


# класс для регистрации состояния сообщений пользователя
# (можете сильно не вникать это просто необходимо для правильной работы,
# просто копируйте и меняйте названия переменных под свою задачу)
class Response(StatesGroup):
    authorization_handler = State()
    authorization_password_handler = State()


# функция для обработки сообщения после нажатия кнопки "Получить доступ",
# вызывается из файла bot_commands.py строка 16
async def authorization_handler(message: types.Message, state: FSMContext):
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


# функция для обработки временного пароля, вызывается в 40 строке этого файла
async def authorization_password_handler(message: types.Message,
                                         state: FSMContext):
    authorization_password_response = message.text
    await state.update_data(user_response=authorization_password_response)
    try:
        authorization_password_response = int(authorization_password_response)
    except:
        ...
    if authorization_password_response == 'Отмена':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Хорошо',
            parse_mode='Markdown',
            reply_markup=markup_new_user
        )
        await Response.authorization_handler.set()
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
            if result == 'doctor':
                markup = markup_doctor
                await doch.Response.register_doctor_handler.set()
            elif result == 'admin':
                markup = markup_admin
                await ah.Response.register_admin_handler.set()
            else:
                markup = markup_director

            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                # TODO поменять вывод на вывод фио из бд
                text=f"{message.from_user.full_name}"
                     f", добро пожаловать в бот клиники ИТА!",
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
            await Response.authorization_handler.set()


# регистратор передающий данные в main_bot.py
def register_handlers_authorization(dp: Dispatcher):  # noqa
    dp.register_message_handler(
        authorization_handler,
        state=Response.authorization_handler
    )
    dp.register_message_handler(
        authorization_password_handler,
        state=Response.authorization_password_handler
    )
