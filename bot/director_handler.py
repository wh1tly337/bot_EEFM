import random

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from auxiliary.all_markups import (
    markup_director,
    markup_director_emp,
    markup_cancel
)
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

    director_handlers = {
        'Управление персоналом': {
            'markup': markup_director_emp,
            'response': Response.register_director_emp_manage,
            'message': 'Доступные команды',
        },
        None: {
            'markup': markup_director,
            'response': Response.register_director_handler,
            'message': 'Такой команды нет, воспользуйтесь кнопками ниже',
        }
    }
    command_dict = director_start_handlers.get(director_response)  # noqa
    if not command_dict:
        command_dict = director_handlers[None]
    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=command_dict.get('message'),
        parse_mode='Markdown',
        reply_markup=command_dict.get('markup')
    )
    await command_dict.get('response').set()


async def register_director_emp_manage(message: types.Message,
                                       state: FSMContext):
    """ Handler для страницы управления сотрудников администратора """
    director_response = message.text
    await state.update_data(user_response=director_response)

    director_handlers = {
        'Добавить сотрудника': {
            'markup': markup_cancel,
            'response': Response.register_director_create_handler,
            'message': 'Введите ФИО и должность в формате:'
                       'Фамилия Имя Отчество должность',
        },
        'Найти сотрудника': {
            'markup': markup_cancel,
            'response': Response.register_director_find_handler,
            'message': 'Введите фамилию сотрудника. :)',
        },
        'Удалить сотрудника': {
            'markup': markup_director_emp,
            'response': Response.register_director_emp_manage,
            'message': 'Введите фамилию сотрудника. :)',
        },
        'Передать права директора': {
            'markup': markup_director_emp,
            'response': Response.register_director_emp_manage,
            'message': 'Теперь ты никто!',
        },
        'Отмена': {
            'markup': markup_director,
            'response': Response.register_director_handler,
            'message': 'Выберите команду',
        },
        None: {
            'markup': markup_director_emp,
            'response': Response.register_director_emp_manage,
            'message': 'Такой команды нет, воспользуйтесь кнопками ниже',
        }
    }

    command_dict = director_emp_handlers.get(director_response)  # noqa
    if not command_dict:
        command_dict = director_handlers[None]

    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=command_dict.get('message'),
        parse_mode='Markdown',
        reply_markup=command_dict.get('markup')
    )
    await command_dict.get('response').set()


# TODO нужно как-то сделать один .set() на всю функцию
#  (см пример в admin_handler)
async def register_director_create_handler(message: types.Message,
                                           state: FSMContext):
    """ Handler для страницы добавления сотрудников администратора """
    director_response = message.text
    await state.update_data(user_response=director_response)
    if director_response == 'Отмена':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Выберите функцию',
            parse_mode='Markdown',
            reply_markup=markup_director_emp
        )
        await Response.register_director_emp_manage.set()
        return
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
    posts = {
        'doctor': ['doctor', 'доктор', 'док'],
        'director': ['director', 'директор'],
        'admin': ['admin', 'админ', 'администратор']
    }
    for key, names in posts.items():
        if post in names:
            post = key
            break
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
    # TODO проверить работоспособность
    await dbw.add_new_user(
        id_tg=temporary_password,
        surname=surname,
        name=name,
        patronymic=patronymic,
        username=surname,
        post=post,
    )
    await Response.register_director_emp_manage.set()
    return


# TODO нужно как-то сделать один .set() на всю функцию
#  (см пример в admin_handler)
async def register_director_find_handler(message: types.Message,
                                         state: FSMContext):
    """ Handler для страницы поиска сотрудников администратора """
    username = message.text
    await state.update_data(user_response=username)
    if username == 'Отмена':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Выберите функцию',
            parse_mode='Markdown',
            reply_markup=markup_director_emp
        )
        await Response.register_director_emp_manage.set()
        return
    emp_data = await dbw.get_data(
        field='username',
        what_need='all',
        value=username
    )
    if not emp_data:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f'Сотрудник не найден!',
            parse_mode='Markdown',
            reply_markup=markup_cancel
        )
        await Response.register_director_emp_manage.set()
        return
    name = emp_data[2]
    surname = emp_data[1]
    post = emp_data[3]
    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=f'''Сотрудник найден, его данные.
        Имя: {name}
        Фамилия: {surname}
        Должность: {post}''',
        parse_mode='Markdown',
        reply_markup=markup_director_emp
    )
    await Response.register_director_emp_manage.set()


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
