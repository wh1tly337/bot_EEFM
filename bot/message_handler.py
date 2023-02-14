from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger
from datetime import datetime

from auxiliary.all_markups import *
from auxiliary.req_data import *
from workers import db_worker as dbw
from .funcs import print_log_info


# класс для регистрации состояния сообщений пользователя (можете сильно не вникать это просто необходимо для правильной работы,
# просто копируйте и меняйте названия переменных под свою задачу)
class Response(StatesGroup):
    authorization_handler = State()  # нельзя менять название переменной, иначе ничего не работает
    authorization_password_handler = State()  # нельзя менять название переменной, иначе ничего не работает




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
    else:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Хорошо',
            parse_mode='Markdown',
            reply_markup=markup_new_user
        )
        await state.finish()


# функция для обработки временного пароля, вызывается в 26 строке этого файла
async def authorization_password_handler(message: types.Message, state: FSMContext):
    authorization_password_response = message.text
    await state.update_data(user_response=authorization_password_response)

    if authorization_password_response == 'Отмена':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Хорошо',
            parse_mode='Markdown',
            reply_markup=markup_new_user
        )
        await state.finish()
    else:
        if authorization_password_response == temporary_password:

            result = await dbw.get_data('post', message.chat.id)
            if result == 'doctor':
                markup = markup_doctor
            elif result == 'admin':
                markup = markup_admin
            else:
                markup = markup_director

            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text=f"{message.from_user.full_name}, добро пожаловать в бот клиники ИТА!",
                parse_mode='Markdown',
                reply_markup=markup
            )
            await dbw.add_new_user(
                message.from_user.id,
                message.from_user.full_name,
                message.from_user.username,
                'doctor',
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                '-'
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
    await state.finish()


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
