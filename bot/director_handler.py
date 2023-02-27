import random
import time

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *
from bot import doctor_handler as dh
from workers import db_worker as dbw

# переменная для функции добавления документов
current_employee_id = 0

# переменная для фукнции смены директора
check_fio = ''


# TODO написать функцию по обновлению информации персонала
#  (вдруг опечатка в фамилии и тп)

class Response(StatesGroup):
    register_director_handler = State()
    register_director_emp_manage = State()
    register_director_create_handler = State()
    register_director_find_handler = State()
    director_change_director = State()
    director_finder_id = State()
    director_add_documents = State()
    director_remove_user = State()


async def register_director_handler(message: types.Message, state: FSMContext):
    """ Handler для стартовой страницы администратора """
    director_response = message.text
    await state.update_data(user_response=director_response)
    fio = await dbw.get_data('id', message.chat.id)
    logger.info(f'Стартовая страница директора | {fio}')
    appeal = f"{fio[2]} {fio[3]}"
    director_handlers = {
        'Управление персоналом': {
            'markup': markup_director_emp,
            'response': Response.register_director_emp_manage,
            'message': 'Доступные команды',
        },
        'Получить расписание': {
            'markup': markup_director,
            'response': Response.register_director_handler,
            'message': 'Расписание:',
            'func': src_current_schedule,
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
    if command_dict.get('func'):
        await bot_aiogram.send_document(
            chat_id=message.chat.id,
            document=open(f"{command_dict.get('func')}", 'rb')
        )
    await command_dict.get('response').set()


async def register_director_emp_manage(message: types.Message,
                                       state: FSMContext):
    """ Handler для страницы управления сотрудников директора """
    logger.info('Страница управления сотрудниками')
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
            'message': 'Введите фамилию сотрудника, информацию которого хотите увидеть',
        },
        'Удалить сотрудника': {
            'markup': markup_cancel,
            'response': Response.director_remove_user,
            'message': 'Введите ФИО сотрудника, которого хотите удалить.',
        },
        'Добавить документы сотруднику': {
            'markup': markup_cancel,
            'response': Response.director_finder_id,
            'message': 'Введите ФИО сотрудника, которому хотите добавить документ',
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


async def register_director_create_handler(message: types.Message,
                                           state: FSMContext):
    """ Handler для страницы добавления сотрудников администратора """
    global check_fio
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
            'message': 'Если вы действительно хотите сменить директора '
                       'введите его ФИО повторно',
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
            'doctor': ['doctor', 'доктор', 'док', 'врач'],
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
            check_fio = f'{surname} {name} {patronymic}'
            logger.info(f'Redefine check_fio | check_fio: {check_fio}')
        temporary_password = random.randint(100000, 1000000)
        if not command_dict:
            command_dict = director_handlers['Добавление пользователя']
            command_dict['message'] = command_dict.get('message') + str(
                temporary_password)
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
    global check_fio
    logger.info(f'Director try to change | check_fio: {check_fio}')
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
            'response': Response.register_director_create_handler,
        },
    }
    while True:
        current_handler = ''
        if director_response == 'Отмена':
            current_handler = director_handlers.get('Отмена')
            break
        dir_data = director_response.split(' ')
        if len(dir_data) != 3 and not current_handler:
            current_handler = director_handlers.get('Неверные данные')
            break

        if director_response != check_fio:
            current_handler = director_handlers.get('Неверные данные')
            break

        dir_data = director_response.split(' ')
        surname = dir_data[0]
        name = dir_data[1]
        patronymic = dir_data[2]
        temporary_password = random.randint(100000, 1000000)
        current_handler = director_handlers.get('Смена директора')
        current_handler['message'] = current_handler.get('message') + str(
            temporary_password)
        await dbw.update_user('post', 'director', 'doctor')
        await dbw.add_new_user(
            id_tg=temporary_password,
            surname=surname,
            name=name,
            patronymic=patronymic,
            username=surname,
            post='director',
        )
        break

    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=current_handler.get('message'),
        parse_mode='Markdown',
        reply_markup=current_handler.get('markup'),
    )
    await current_handler.get('response').set()


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
        field='surname',
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
    id = emp_data[0]
    documents = await dbw.get_documents(id)
    surname = emp_data[1]
    name = emp_data[2]
    patronymic = emp_data[3]
    post = emp_data[5]
    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=f'''Сотрудник найден, общие данные данные.
        Имя: {name}
        Фамилия: {surname}
        Отчество: {patronymic}
        Должность: {post}''',
        parse_mode='Markdown',
        reply_markup=markup_director_emp
    )
    print(documents)
    if documents:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Название  Дата начала  Дата окончания',
            parse_mode='Markdown',
        )
        for document in documents:
            await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f'"{document[2]}" {document[0]} {document[1]}',
            parse_mode='Markdown',
        )

    await Response.register_director_emp_manage.set()


async def director_finder_id(message: types.Message,
                             state: FSMContext):
    """ Handler поиска ид для добавления документов сотруднику """
    global current_employee_id
    emp_fio = message.text
    await state.update_data(user_response=emp_fio)
    director_handlers = {
        'Отмена': {
            'message': 'Выберите функцию',
            'markup': markup_director_emp,
            'response': Response.register_director_emp_manage,
        },
        'Сотрудник найден': {
            'message': 'Сотрудник найден, введите даты начала'
                       ', окончания действия документа в формате'
                       'дд.мм.гггг и имя документа',
            'markup': markup_cancel,
            'response': Response.director_add_documents,
        },
        'Сотрудник не найден': {
            'message': 'Сотрудник не найден, попробуйте ещё раз',
            'markup': markup_cancel,
            'response': Response.director_finder_id,
        },
        'Неверные данные': {
            'message': 'Данные введены неверно, попробуйте ещё раз',
            'markup': markup_cancel,
            'response': Response.director_finder_id,
        },
    }
    while True:
        current_handler = ''
        if emp_fio == 'Отмена':
            current_handler = director_handlers.get('Отмена')
            break
        emp_fio = emp_fio.split(' ')
        if len(emp_fio) != 3:
            current_handler = director_handlers.get('Неверные данные')
            break
        id = await dbw.get_id_with_fio(emp_fio)
        if not id:
            current_handler = director_handlers.get('Сотрудник не найден')
            break
        current_employee_id = id[0][0]
        current_handler = director_handlers.get('Сотрудник найден')
        break
    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=current_handler.get('message'),
        parse_mode='Markdown',
        reply_markup=current_handler.get('markup')
    )
    await current_handler.get('response').set()


async def director_remove_user(message: types.Message,
                               state: FSMContext):
    """ Handler удаления сотрудника """
    emp_fio = message.text
    await state.update_data(user_response=emp_fio)
    director_handlers = {
        'Отмена': {
            'message': 'Выберите функцию',
            'markup': markup_director_emp,
            'response': Response.register_director_emp_manage,
        },
        'Сотрудник удалён': {
            'message': 'Сотрудник был удалён',
            'markup': markup_director,
            'response': Response.register_director_handler,
        },
        'Неверные данные': {
            'message': 'Данные введены неверно, попробуйте ещё раз',
            'markup': markup_cancel,
            'response': Response.director_finder_id,
        },
    }
    while True:
        current_handler = ''
        if emp_fio == 'Отмена':
            current_handler = director_handlers.get('Отмена')
            break
        emp_fio = emp_fio.split(' ')
        if len(emp_fio) != 3:
            current_handler = director_handlers.get('Неверные данные')
            break
        id = await dbw.get_id_with_fio(emp_fio)
        id = id[0][0]
        await dbw.remove_user(id)
        current_handler = director_handlers.get('Сотрудник удалён')
        current_handler['message'] = current_handler['message'] + str(id)
        break
    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=current_handler.get('message'),
        parse_mode='Markdown',
        reply_markup=current_handler.get('markup')
    )
    await current_handler.get('response').set()


async def director_add_documents(message: types.Message,
                                 state: FSMContext):
    global current_employee_id
    """ Handler добавления документов сотруднику """
    document_data = message.text
    await state.update_data(user_response=document_data)
    director_handlers = {
        'Отмена': {
            'message': 'Выберите функцию',
            'markup': markup_director,
            'response': Response.register_director_handler,
        },
        'Добавление документа': {
            'message': 'Документ добавлен, введите информацию следующего документа',
            'markup': markup_cancel,
            'response': Response.director_add_documents,
        },
        'Неверные данные': {
            'message': 'Данные введены неверно, попробуйте ещё раз',
            'markup': markup_cancel,
            'response': Response.director_add_documents,
        },
    }
    while True:
        current_handler = ''
        if document_data == 'Отмена':
            current_handler = director_handlers.get('Отмена')
            break
        document_data = document_data.split(' ')

        # Проверка, что даты указаны в нужном формате
        try:
            id = current_employee_id
            date_start = document_data[0]
            date_finish = document_data[1]
            name = document_data[2]
            time.strptime(date_start, '%d.%m.%Y')
            time.strptime(date_finish, '%d.%m.%Y')
        except Exception as ex:
            logger.error(ex)
            current_handler = director_handlers.get('Неверные данные')
            break

        await dbw.add_new_document(id, date_start, date_finish, name)
        current_handler = director_handlers.get('Добавление документа')
        break
    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=current_handler.get('message'),
        parse_mode='Markdown',
        reply_markup=current_handler.get('markup')
    )
    await current_handler.get('response').set()


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
    dp.register_message_handler(
        director_finder_id,
        state=Response.director_finder_id
    )
    dp.register_message_handler(
        director_add_documents,
        state=Response.director_add_documents
    )
    dp.register_message_handler(
        director_remove_user,
        state=Response.director_remove_user
    )
