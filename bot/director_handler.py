from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import types
import datetime
import random

from auxiliary.all_markups import markup_director, markup_director_emp
from auxiliary.req_data import *

from workers import db_worker as dbw


class Response(StatesGroup):
    register_director_handler = State()
    register_director_emp_manage = State()
    register_director_create_handler = State()


async def register_director_handler(message: types.Message, state: FSMContext):
    ''' Обработка стратовой страницы директора '''
    print('enter director start ')
    director_response = message.text
    await state.update_data(user_response=director_response)
    if director_response == 'Управление персоналом':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Доступные команды',
            parse_mode='Markdown',
            reply_markup=markup_director_emp
        )
        await Response.register_director_emp_manage.set()
    else:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Такой команды нет',
            parse_mode='Markdown',
            reply_markup=markup_director
        )
        await Response.register_director_handler.set()

async def register_director_emp_manage(message: types.Message, state: FSMContext):
    ''' Обработка Управление персоналом '''
    director_response = message.text
    await state.update_data(user_response=director_response)

    if director_response == 'Добавить сотрудника':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Введите ФИО и должность в формате: Фамилия Имя Отчество должность',
            parse_mode='Markdown',
            reply_markup=markup_director_emp
        )
        await Response.register_director_create_handler.set()

    elif director_response == 'Найти сотрудника':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Нашел!',
            parse_mode='Markdown',
            reply_markup=markup_director_emp
        )
    elif director_response == 'Удалить сотрудника':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Удалил!',
            parse_mode='Markdown',
            reply_markup=markup_director_emp
        )
    elif director_response == 'Передать права директора':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Теперь ты никто!',
            parse_mode='Markdown',
            reply_markup=markup_director_emp
        )
    else:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Такой команды нет',
            parse_mode='Markdown',
            reply_markup=markup_director_emp
        )

async def register_director_create_handler(message: types.Message, state: FSMContext):
    director_response = message.text
    print(director_response)
    emp_data = director_response.split()
    print(emp_data)
    temporary_password = random.randint(100000, 1000000)
    await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f'Сотрудник добавлен, его код {temporary_password}',
            parse_mode='Markdown',
            reply_markup=markup_director_emp
        )
    # TODO Исправить БД, изменить поля, добавить Отчество.
    await dbw.add_new_user(
        id_tg=temporary_password,
        first_name=emp_data[0],
        username=emp_data[1],
        post=emp_data[3],
    )

# регистратор передающий данные в main_bot.py
def register_handlers_director(dp: Dispatcher):  # noqa
    dp.register_message_handler(
        register_director_handler,
        state=Response.register_director_handler
    )
    dp.register_message_handler(
        register_director_emp_manage,
        state=Response.register_director_emp_manage
    )
    dp.register_message_handler(
        register_director_create_handler,
        state=Response.register_director_create_handler
    )