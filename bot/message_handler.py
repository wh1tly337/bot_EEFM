from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger
from datetime import datetime

from auxiliary.all_markups import *
from auxiliary.req_data import *
from workers import db_worker as dbw


# класс для регистрации состояния сообщений пользователя (можете сильно не вникать это просто необходимо для правильной работы, просто копируйте и меняйте названия переменных под свою задачу)
class Response(StatesGroup):
    authorization_handler = State()
    authorization_password_handler = State()


# функция для обработки сообщения после нажатия кнопки "Получить доступ", вызывается из файла bot_commands.py строка 16
async def authorization_handler(message: types.Message, state: FSMContext):
    authorization_response = message.text
    await state.update_data(user_response=authorization_response)

    if authorization_response == 'Отмена':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', parse_mode='Markdown', reply_markup=markup_new_user)
        await state.finish()
    else:
        message_text = f"Введите временный пароль. Его нужно уточнить у {director_name}"
        await bot_aiogram.send_message(chat_id=message.chat.id, text=message_text, parse_mode='Markdown', reply_markup=markup_cancel)
        await Response.authorization_password_handler.set()


# функция для обработки временного пароля, вызывается в 26 строке этого файла
async def authorization_password_handler(message: types.Message, state: FSMContext):
    authorization_password_response = message.text
    await state.update_data(user_response=authorization_password_response)

    if authorization_password_response == 'Отмена':
        await bot_aiogram.send_message(chat_id=message.chat.id, text='Хорошо', parse_mode='Markdown', reply_markup=markup_new_user)
        await state.finish()
    else:
        if authorization_password_response == temporary_password:
            await bot_aiogram.send_message(chat_id=message.chat.id, text=f"{message.from_user.full_name}, добро пожаловать в бот клиники ИТА!", parse_mode='Markdown', reply_markup=markup_test)
            await dbw.add_new_user(message.from_user.id, message.from_user.full_name, message.from_user.username, 'doctor', datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '-')
            logger.info(f"New user log in and added to database | {message.from_user.id}, {message.from_user.full_name}, {message.from_user.username}")
        else:
            await bot_aiogram.send_message(chat_id=message.chat.id, text='Пароль введен неверно', parse_mode='Markdown', reply_markup=markup_new_user)
            logger.info(f"User unsuccessfully tried to log in | {message.from_user.id}, {message.from_user.full_name}, {message.from_user.username}")

    await state.finish()


# регистратор передающий данные в main_bot.py
def register_handlers_authorization(dp: Dispatcher):  # noqa
    dp.register_message_handler(authorization_handler, state=Response.authorization_handler)
    dp.register_message_handler(authorization_password_handler, state=Response.authorization_password_handler)
