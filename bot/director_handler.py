import random

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from auxiliary.all_markups import (
    markup_director,
    markup_director_emp,
    markup_cancel,
    markup_yes_no,
    markup_doctor
)
from auxiliary.req_data import *
from workers import db_worker as dbw
from bot import doctor_handler as dh

class Response(StatesGroup):
    register_director_handler = State()
    register_director_emp_manage = State()
    register_director_create_handler = State()
    register_director_find_handler = State()
    director_change_director = State()


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
    command_dict = director_handlers.get(director_response)  # noqa
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

    command_dict = director_handlers.get(director_response)  # noqa
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
    command_dict = None
    director_handlers = {
        'Отмена': {
            'message': 'Выберите функцию',
            'markup': markup_director_emp,
            'response': Response.register_director_emp_manage,
        },
        'Некорректные данные': {
            'message': 'Данные введены неверное, попробуйте ещё раз',
            'markup': markup_cancel,
            'response': Response.register_director_create_handler,
        },
        'Неверная должность': {
            'message': 'Такой должности нет',
            'markup': markup_cancel,
            'response': Response.register_director_create_handler,
        },
        'Добавление пользователя': {
            'message': 'Сотрудник добавлен его код:',
            'markup': markup_director_emp,
            'response': Response.register_director_emp_manage,
        },
        'Смена директора': {
            'message': 'Если вы действительно хотите сменить директора введите его ФИО повторно',
            'markup': markup_cancel,
            'response': Response.director_change_director,
        }
    }

    if director_response == 'Отмена':
        command_dict = director_handlers['Отмена']

    emp_data = director_response.split()
    if len(emp_data) != 4 and not command_dict:
        command_dict = director_handlers['Некорректные данные']

    if not command_dict:
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
            command_dict = director_handlers['Неверная должность']

        if post == 'director':
            command_dict = director_handlers['Смена директора']

        temporary_password = random.randint(100000, 1000000)
        if not command_dict:
            command_dict = director_handlers['Добавление пользователя']
            command_dict['message'] = command_dict.get('message') + str(temporary_password)
            await dbw.add_new_user(
                id_tg=temporary_password,
                surname=surname,
                name=name,
                patronymic=patronymic,
                username=surname,
                post=post,
            )

    await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=command_dict.get('message'),
            parse_mode='Markdown',
            reply_markup=command_dict.get('markup'),
        )
    await command_dict.get('response').set()

async def director_change_director(message: types.Message,
                                   state: FSMContext):
    director_response = message.text
    await state.update_data(user_response=director_response)
    director_handlers = {
        'Отмена': {
            'message': 'Выберите функцию',
            'markup': markup_cancel,
            'response': Response.register_director_create_handler,
        },
        'Смена директора': {
            'message': 'Директор сменён, его код: ',
            'markup': markup_doctor,
            'response': dh.Response.doctor_handler,
        },
        'Неверные данные': {
            'message': 'Данные введены неверно, попробуйте ещё раз',
            'markup': markup_cancel,
            'response': Response.register_director_handler,
        },
    }
    while True:
        if director_response == 'Отмена':
            current_hendler = director_handlers['Отмена']
            break
        dir_data = director_response.split(' ')
        if len(dir_data) != 3 and not current_hendler:
            current_hendler = director_handlers['Неверные данные']
            break
        dir_data = director_response.split(' ')
        surname = dir_data[0]
        name = dir_data[1]
        patronymic = dir_data[2]
        temporary_password = random.randint(100000, 1000000)
        current_hendler = director_handlers['Смена директора']
        current_hendler['message'] = current_hendler.get('message') + str(temporary_password)
        await dbw.add_new_user(
            id_tg=temporary_password,
            surname=surname,
            name=name,
            patronymic=patronymic,
            username=surname,
            post='director',
        )
        await dbw.update_user('post', 'director', 'doctor')
        break

    await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=current_hendler.get('message'),
            parse_mode='Markdown',
            reply_markup=current_hendler.get('markup'),
        )
    await current_hendler.get('response').set()



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
    dp.register_message_handler(
        director_change_director,
        state=Response.director_change_director
    )
