from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from auxiliary.all_markups import *
from auxiliary.req_data import *


# TODO поменять имена переменных в этом файле на нормальные

# TODO поменять if/else на списки

class Response(StatesGroup):
    register_admin_handler = State()
    register_admin_schedule_handler = State()
    register_admin_mailing_handler = State()
    register_admin_sending_handler = State()
    register_admin_file_handler = State()
    register_admin_watch_schedule_handler = State()


async def register_admin_handler(message: types.Message, state: FSMContext):
    admin_response = message.text
    await state.update_data(user_response=admin_response)

    if admin_response == 'Расписание':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Что вы хотите сделать с расписанием?',
            parse_mode='Markdown',
            reply_markup=markup_admin_make_schedule
        )
        await Response.register_admin_schedule_handler.set()
    elif admin_response == 'Отправить сообщение':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Кому вы хотите отправить сообщение?',
            parse_mode='Markdown',
            reply_markup=markup_admin_message
        )
        await Response.register_admin_mailing_handler.set()
    else:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Нет такой команды, воспользуйтесь кнопками ниже ',
            parse_mode='Markdown',
            reply_markup=markup_admin
        )


async def register_admin_schedule_handler(message: types.Message,
                                          state: FSMContext):
    admin_schedule_response = message.text
    await state.update_data(user_response=admin_schedule_response)

    if admin_schedule_response == 'Получить шаблон':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Шаблон расписания:',
            parse_mode='Markdown',
            reply_markup=markup_admin
        )
        # TODO отправить шаблон расписания
    elif admin_schedule_response == 'Загрузить расписание':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Отправьте мне Excel файл с расписанием',
            parse_mode='Markdown',
            reply_markup=markup_admin
        )
        await Response.register_admin_file_handler.set()
    elif admin_schedule_response == 'Посмотреть расписание':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='На какой период вы хотите посмотреть расписание?',
            parse_mode='Markdown',
            reply_markup=markup_admin_watch_schedule
        )
        await Response.register_admin_watch_schedule_handler.set()
    elif admin_schedule_response == 'Отмена':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Хорошо',
            parse_mode='Markdown',
            reply_markup=markup_admin
        )
        await Response.register_admin_handler.set()
    else:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Нет такой команды, воспользуйтесь кнопками ниже ',
            parse_mode='Markdown',
            reply_markup=markup_admin_make_schedule
        )


async def register_admin_mailing_handler(message: types.Message,
                                         state: FSMContext):
    admin_mailing_response = message.text
    await state.update_data(user_response=admin_mailing_response)

    if admin_mailing_response == 'Рассылка':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Отправьте мне сообщение, которое вы хотите разослать'
                 ' всем сотрудникам',
            parse_mode='Markdown',
            reply_markup=markup_cancel
        )
        await Response.register_admin_sending_handler.set()
    elif admin_mailing_response == 'Директору':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Отправьте мне сообщение для директора',
            parse_mode='Markdown',
            reply_markup=markup_cancel
        )
        await Response.register_admin_sending_handler.set()
    elif admin_mailing_response == 'Отмена':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Хорошо',
            parse_mode='Markdown',
            reply_markup=markup_admin
        )
        await Response.register_admin_handler.set()
    else:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Нет такой команды, воспользуйтесь кнопками ниже ',
            parse_mode='Markdown',
            reply_markup=markup_admin_message
        )


async def register_admin_sending_handler(message: types.Message,
                                         state: FSMContext):
    admin_sending_response = message.text
    await state.update_data(user_response=admin_sending_response)
    # TODO функция по отправки сообщения директору или всему персоналу

    if admin_sending_response == 'Отмена':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Хорошо',
            parse_mode='Markdown',
            reply_markup=markup_admin_message
        )
        await Response.register_admin_mailing_handler.set()
    else:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Сообщение отправлено!',
            parse_mode='Markdown',
            reply_markup=markup_admin
        )
        await Response.register_admin_handler.set()


async def register_admin_file_handler(message: types.Message,
                                      state: FSMContext):
    admin_file_response = message.text
    await state.update_data(user_response=admin_file_response)
    # TODO функция обработке присылаемого файла расписания и загрузка его в бд

    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text='Расписание получено!',
        parse_mode='Markdown',
        reply_markup=markup_admin
    )
    await Response.register_admin_handler.set()


async def register_admin_watch_schedule_handler(message: types.Message,
                                                state: FSMContext):
    admin_watch_schedule_response = message.text
    await state.update_data(user_response=admin_watch_schedule_response)

    if admin_watch_schedule_response == 'На сегодня':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Расписание на сегодня:',
            parse_mode='Markdown',
            reply_markup=markup_admin
        )
        await Response.register_admin_handler.set()
        # TODO добавить возможность смотреть расписание на сегодня
    elif admin_watch_schedule_response == 'На неделю':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Расписание на наделю:',
            parse_mode='Markdown',
            reply_markup=markup_admin
        )
        await Response.register_admin_handler.set()
        # TODO добавить возможность смотреть расписание на неделю
    elif admin_watch_schedule_response == 'Отмена':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Хорошо',
            parse_mode='Markdown',
            reply_markup=markup_admin_make_schedule
        )
        await Response.register_admin_schedule_handler.set()
    else:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Нет такой команды, воспользуйтесь кнопками ниже ',
            parse_mode='Markdown',
            reply_markup=markup_admin_watch_schedule
        )


# регистратор передающий данные в main_bot.py
def register_handlers_admin(dp: Dispatcher):  # noqa
    dp.register_message_handler(
        register_admin_handler,
        state=Response.register_admin_handler
    )
    dp.register_message_handler(
        register_admin_schedule_handler,
        state=Response.register_admin_schedule_handler
    )
    dp.register_message_handler(
        register_admin_mailing_handler,
        state=Response.register_admin_mailing_handler
    )
    dp.register_message_handler(
        register_admin_sending_handler,
        state=Response.register_admin_sending_handler
    )
    dp.register_message_handler(
        register_admin_file_handler,
        state=Response.register_admin_file_handler
    )
    dp.register_message_handler(
        register_admin_watch_schedule_handler,
        state=Response.register_admin_watch_schedule_handler
    )
