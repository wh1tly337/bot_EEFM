from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *


# класс для регистрации состояния сообщений пользователя 
# (можете сильно не вникать это просто необходимо для правильной работы, 
# просто копируйте и меняйте названия переменных под свою задачу)
class Response(StatesGroup):
         = State()
    authorization_password_handler = State()


# функция для обработки сообщения после нажатия кнопки "Получить доступ", 
# вызывается из файла bot_commands.py строка 
async def authorization_handler(message: types.Message, state: FSMContext):
    authorization_response = message.text
    await state.update_data(user_response=authorization_response)

    if authorization_response == 'Отмена':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Хорошо',
            parse_mode='Markdown',
            reply_markup=markup_new_user
        )
        await state.finish()
    else:
        message_text = f"Введите временный пароль. Его нужно уточнить у {boss}"
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=message_text,
            parse_mode='Markdown',
            reply_markup=markup_cancel
        )
        await Response.authorization_password_handler.set()


# функция для обработки временного пароля, вызывается в 26 строке этого файла
async def authorization_password_handler(message: types.Message, state: FSMContext):
    authorization_password_response = message.text
    await state.update_data(
        user_response=authorization_password_response
    )

    if authorization_password_response == 'Отмена':
        await bot_aiogram.send_message(
            chat_id=message.chat.id, text='Хорошо',
            parse_mode='Markdown',
            reply_markup=markup_new_user
        )
        await state.finish()
    else:
        if authorization_password_response == temporary_password:
            msg_hello_new_user = " , добро пожаловать в бот клиники ИТА!"
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text=message.from_user.full_name + msg_hello_new_user,
                parse_mode='Markdown',
                reply_markup=markup_test
            )
            logger.info((
                "New user log in and added to database |",
                message.from_user.id,
                message.from_user.full_name,
                message.from_user.username
            ))
        else:
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Пароль введен неверно',
                parse_mode='Markdown',
                reply_markup=markup_new_user
            )
            logger.info((
                "User unsuccessfully tried to log in |",
                message.from_user.id,
                message.from_user.full_name,
                message.from_user.username
            ))

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
