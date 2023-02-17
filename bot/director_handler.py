import random

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from auxiliary.all_markups import markup_director, markup_director_emp
from auxiliary.req_data import *
from workers import db_worker as dbw


class Response(StatesGroup):
    register_director_handler = State()
    register_director_emp_manage = State()
    register_director_create_handler = State()
    register_director_find_handler = State()


async def register_director_handler(message: types.Message, state: FSMContext):
    """ Handler для стартовой страницы администратора """
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


async def register_director_emp_manage(message: types.Message,
                                       state: FSMContext):
    """ Handler для страницы управления сотрудников администратора """
    director_response = message.text
    await state.update_data(user_response=director_response)

    match director_response:
        case 'Добавить сотрудника':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Введите ФИО и должность в формате:'
                     ' Фамилия Имя Отчество должность',
                parse_mode='Markdown',
                reply_markup=markup_director_emp
            )
            await Response.register_director_create_handler.set()
        case 'Найти сотрудника':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Введите фамилию сотрудника. :)',
                parse_mode='Markdown',
                reply_markup=markup_director_emp
            )
            await Response.register_director_find_handler.set()
        case 'Удалить сотрудника':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Удалил!',
                parse_mode='Markdown',
                reply_markup=markup_director_emp
            )
        case 'Передать права директора':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Теперь ты никто!',
                parse_mode='Markdown',
                reply_markup=markup_director_emp
            )
        case _:
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Такой команды нет',
                parse_mode='Markdown',
                reply_markup=markup_director_emp
            )


async def register_director_create_handler(message: types.Message,
                                           state: FSMContext):
    """ Handler для страницы добавления сотрудников администратора """
    director_response = message.text
    # Добавит строчку ниже во время рефакторинга, если не работает, то из-за нее
    await state.update_data(user_response=director_response)
    emp_data = director_response.split()
    if len(emp_data) != 4:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f'Данные введены неверное, попробуйте ещё раз',
            parse_mode='Markdown',
            reply_markup=markup_director_emp
        )
        await Response.register_director_create_handler.set()
        return

    surname = emp_data[0]
    name = emp_data[1]
    patronymic = emp_data[2]
    post = emp_data[3]
    posts = ['director', 'admin', 'doctor']
    if post not in posts:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f'Такой должности нет!',
            parse_mode='Markdown',
            reply_markup=markup_director_emp
        )
        await Response.register_director_create_handler.set()
        return
    if post == 'director':
        # TODO реализовать метод передачи директора
        ...
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
        first_name=name,
        username=surname,
        post=post,
    )


async def register_director_find_handler(message: types.Message,
                                         state: FSMContext):
    """ Handler для страницы поиска сотрудников администратора """
    username = message.text
    await state.update_data(user_response=username)
    emp_data = await dbw.get_data(
        field='username',
        what_need='all',
        value=username
    )
    if emp_data:
        name = emp_data[2]
        surname = emp_data[1]
        post = emp_data[3]
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f"""Сотрудник найден, его данные.
            Имя: {name}
            Фамилия: {surname}
            Должность: {post}""",
            parse_mode='Markdown',
            reply_markup=markup_director_emp
        )
    else:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f'Сотрудник не найден!',
            parse_mode='Markdown',
            reply_markup=markup_director_emp
        )


def register_handlers_director(dp: Dispatcher):  # noqa
    """ Регистратор handler'ов передает данные в main_bot.py"""
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
    dp.register_message_handler(
        register_director_find_handler,
        state=Response.register_director_find_handler
    )
