from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from auxiliary.all_markups import *
from auxiliary.req_data import *


# класс для регистрации состояния сообщений пользователя
# (можете сильно не вникать это просто необходимо для правильной работы,
# просто копируйте и меняйте названия переменных под свою задачу)
class Response(StatesGroup):
    register_doctor_handler = State()


# функция для обработки временного пароля, вызывается в 26 строке этого файла
async def register_doctor_handler(message: types.Message, state: FSMContext):
    doctor_response = message.text
    await state.update_data(user_response=doctor_response)

    if doctor_response == 'Получить расписание':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Ваше расписание:',
            parse_mode='Markdown',
            reply_markup=markup_doctor
        )
    else:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Такой команды нет',
            parse_mode='Markdown',
            reply_markup=markup_doctor
        )


# регистратор передающий данные в main_bot.py
def register_handlers_doctor(dp: Dispatcher):  # noqa
    dp.register_message_handler(
        register_doctor_handler,
        state=Response.register_doctor_handler
    )
