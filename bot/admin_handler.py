import asyncio
import os
import shutil
from datetime import datetime as dt

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

from auxiliary.all_markups import *
from auxiliary.req_data import *
from bot import (
    bot_commands as bc,
)
from workers import (
    db_worker as dbw,
    file_worker as fw
)

# глобальные переменные для работы автоматической загрузке расписания
deep_counter = 0
need_check = False
deferred = False


# класс для регистрации состояния сообщений пользователя (используется везде,
# где нужно обрабатывать текстовые сообщения от пользователя)
class Response(StatesGroup):
    admin_message_handler = State()
    admin_schedule_handler = State()
    admin_send_messages_handler = State()
    admin_mailing_handler = State()
    admin_to_director_handler = State()
    admin_deferred_handler = State()


async def admin_message_handler(message: types.Message, state: FSMContext):
    """ Функция-обработчик сообщений стартовой страницы админа """
    admin_response = message.text
    await state.update_data(user_response=admin_response)

    admin_handlers = {
        'Расписание': {
            'markup': markup_admin_make_schedule,
            'response': Response.admin_schedule_handler,
            'message': 'Что вы хотите сделать с расписанием',
        },
        'Отправить сообщение': {
            'markup': markup_admin_message,
            'response': Response.admin_send_messages_handler,
            'message': 'Кому вы хотите отправить сообщение?',
        },
        None: {
            'markup': markup_admin,
            'response': Response.admin_message_handler,
            'message': 'Такой команды нет, воспользуйтесь кнопками ниже',
        }
    }
    command_dict = admin_handlers.get(admin_response)  # noqa
    if not command_dict:
        command_dict = admin_handlers[None]
    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=command_dict.get('message'),
        parse_mode='Markdown',
        reply_markup=command_dict.get('markup')
    )
    await command_dict.get('response').set()


async def admin_schedule_handler(message: types.Message, state: FSMContext):
    """ Функция-обработчик сообщений второй страницы расписания для админа """
    admin_schedule_response = message.text
    await state.update_data(user_response=admin_schedule_response)

    admin_handlers = {
        'Получить шаблон': {
            'markup': markup_admin,
            'response': Response.admin_message_handler,
            'message': 'Шаблон расписания:',
            'func': src_schedule_template,
        },
        'Загрузить расписание': {
            'markup': markup_admin_load_schedule,
            'response': Response.admin_deferred_handler,
            'message': 'Как вы хотите отправить расписание?\n'
                       '"Сразу" - расписание загружается вами сейчас и '
                       'применяется тоже сейчас\n'
                       '"Отложено" - расписание загружается вами сейчас, но '
                       'становится активным в следующий понедельник утром '
                       '(чтобы загружать расписание на следующую неделю '
                       'заранее)',
        },
        'Получить расписание': {
            'markup': markup_admin,
            'response': Response.admin_message_handler,
            'message': 'Расписание:',
            'func': src_current_schedule,
        },
        'Отмена': {
            'markup': markup_admin,
            'response': Response.admin_message_handler,
            'message': 'Выберите команду',
        },
        None: {
            'markup': markup_admin_make_schedule,
            'response': Response.admin_schedule_handler,
            'message': 'Такой команды нет, воспользуйтесь кнопками ниже',
        }
    }

    command_dict = admin_handlers.get(admin_schedule_response)  # noqa
    if not command_dict:
        command_dict = admin_handlers[None]
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
        logger.info('Current schedule was sent to admin')

    if command_dict.get('response'):
        await command_dict.get('response').set()


async def admin_deferred_handler(message: types.Message, state: FSMContext):
    """Функция-обработчик для выбора когда загружать расписание."""
    global need_check, deferred

    admin_deferred_response = message.text
    await state.update_data(user_response=admin_deferred_response)

    admin_handlers = {
        'Сразу': {
            'markup': markup_cancel,
            'finish': state,
            'message': 'Отправьте мне Excel файл с расписанием',
            'deferred_value': False,
            'value': False,
        },
        'Отложено': {
            'markup': markup_cancel,
            'finish': state,
            'message': 'Отправьте мне Excel файл с расписанием '
                       '(сам загрузится утром в пн)',
            'deferred_value': True,
            'value': True,
        },
        'Отмена': {
            'markup': markup_admin_make_schedule,
            'response': Response.admin_schedule_handler,
            'message': 'Хорошо',
        },
        None: {
            'markup': markup_admin_load_schedule,
            'response': Response.admin_deferred_handler,
            'message': 'Такой команды нет, воспользуйтесь кнопками ниже',
        }
    }

    command_dict = admin_handlers.get(admin_deferred_response)  # noqa
    if not command_dict:
        command_dict = admin_handlers[None]
    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=command_dict.get('message'),
        parse_mode='Markdown',
        reply_markup=command_dict.get('markup')
    )

    if command_dict.get('response'):
        await command_dict.get('response').set()
    elif command_dict.get('finish'):
        await command_dict.get('finish').finish()
        deferred = command_dict.get('deferred_value')
        need_check = command_dict.get('value')


async def admin_deferred_doc_handler():
    """Рекурсивная функция для автоматической загрузки расписания."""

    global deep_counter, need_check

    if (
            dt.weekday(dt.now()) == 0 and  # проверка на пн
            dt.now().strftime('%H') == '08' and  # проверка на время
            os.path.exists('auxiliary/deferred_schedule.xlsx') is True and
            need_check is True
    ):
        fw.file_delete('now')  # удаление текущего расписания
        shutil.copyfile(
            f"{src_deferred_schedule}deferred_schedule.xlsx",
            f"{src_current_schedule}"
        )  # копирования файла с расписанием в нужную директорию
        fw.file_delete('monday')  # удаление файла который теперь лежит в
        # другой директории
        admin_id = await dbw.get_data('post', 'admin', 'id')
        await bot_aiogram.send_message(
            admin_id,
            "Расписание автоматически загружено на текущую неделю"
        )
        need_check = False

    if deep_counter == 1:
        deep_counter = 0
        return
    while need_check is True:
        await asyncio.sleep(1800)
        deep_counter += 1
        await admin_deferred_doc_handler()


async def admin_file_handler(message: types.Message):
    """ Функция-обработчик файла расписания загружаемого админом """
    all_ids = await dbw.get_all_ids()
    # если пользователь не залогиненный, то этот try избавит от ошибки
    try:
        log_stat = (await dbw.get_data('id', message.chat.id))[6]
    except Exception:
        log_stat = 0
    # эта проверка нужна для исправления бага, при котором если пользователь
    # не введет /start после старта бота то юзер будет считаться админом, даже
    # если его не было в бд
    if (message.chat.id not in all_ids) or (log_stat == 0):
        await bc.start_message(message)
    elif message.text:
        text = 'Хорошо' if message.text == 'Отмена' else \
            'Это не является расписанием'
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='Markdown',
            reply_markup=markup_admin_make_schedule
        )
        await Response.admin_schedule_handler.set()
    elif message.document:
        # проверка на формат документа
        if message.document.file_name[-4:] == 'xlsx' or \
                message.document.file_name[-3:] == 'xls':

            if deferred is False:
                src_docs = src_files
                message_text = 'Расписание получено!'
                when = 'now'
            else:
                src_docs = src_deferred_schedule
                message_text = 'Расписание получено! Оно будет ' \
                               'автоматически загружено в понедельник утром'
                when = 'monday'

            await message.document.download(
                destination_file=f"{src_docs}"
                                 f"{message.document.file_name}")

            filename = message.document.file_name.split('.')
            ender = filename[1]
            filename = filename[0]
            fw.all_cycle(filename, ender, when)

            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text=message_text,
                parse_mode='Markdown',
                reply_markup=markup_admin
            )
            response = Response.admin_message_handler
        else:
            message_text = 'Неверный формат файла расписания'

            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text=message_text,
                parse_mode='Markdown',
                reply_markup=markup_admin_make_schedule
            )
            response = Response.admin_schedule_handler

        await response.set()

        # вызов рекурсивной функции для автоматической загрузки расписания
        if deferred:
            await admin_deferred_doc_handler()


async def admin_send_messages_handler(message: types.Message,
                                      state: FSMContext):
    """ Функция-обработчик сообщений второй страницы рассылки для админа """
    admin_mailing_response = message.text
    await state.update_data(user_response=admin_mailing_response)

    admin_handlers = {
        'Рассылка': {
            'markup': markup_cancel,
            'response': Response.admin_mailing_handler,
            'message': 'Отправьте мне сообщение, которое вы хотите '
                       'разослать всем сотрудникам',
        },
        'Директору': {
            'markup': markup_cancel,
            'response': Response.admin_to_director_handler,
            'message': 'Отправьте мне сообщение для директора',
        },
        'Отмена': {
            'markup': markup_admin,
            'response': Response.admin_message_handler,
            'message': 'Выберите команду',
        },
        None: {
            'markup': markup_admin_message,
            'response': Response.admin_send_messages_handler,
            'message': 'Такой команды нет, воспользуйтесь кнопками ниже',
        }
    }

    command_dict = admin_handlers.get(admin_mailing_response)  # noqa
    if not command_dict:
        command_dict = admin_handlers[None]
    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=command_dict.get('message'),
        parse_mode='Markdown',
        reply_markup=command_dict.get('markup')
    )
    await command_dict.get('response').set()


async def admin_mailing_handler(message: types.Message, state: FSMContext):
    """ Функция-обработчик сообщений для рассылки персоналу """
    admin_sending_response = message.text
    await state.update_data(user_response=admin_sending_response)

    if admin_sending_response == 'Отмена':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Хорошо',
            parse_mode='Markdown',
            reply_markup=markup_admin_message
        )
        response = Response.admin_send_messages_handler
    else:
        # try на случай если id из бд по какой-то причине не существует
        try:
            all_ids = await dbw.get_all_ids()
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Рассылка произведена успешно!',
                parse_mode='Markdown',
                reply_markup=markup_admin
            )
            for i in range(len(all_ids)):
                await bot_aiogram.send_message(
                    chat_id=all_ids[i],
                    text='Рассылка от администратора:\n' +
                         admin_sending_response,
                    parse_mode='Markdown',
                    reply_markup=markup_admin
                )
            response = Response.admin_message_handler
        except Exception:
            response = Response.admin_message_handler

    await response.set()


# функция-обработчик сообщений от админа для перенаправления получателю
async def admin_to_director_handler(message: types.Message, state: FSMContext):
    """ Функция-обработчик сообщений для перенаправления директору """
    admin_director_sending_response = message.text
    await state.update_data(user_response=admin_director_sending_response)

    if admin_director_sending_response == 'Отмена':
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Хорошо',
            parse_mode='Markdown',
            reply_markup=markup_admin_message
        )
        response = Response.admin_send_messages_handler
    else:
        director_id = await dbw.get_data('post', 'director', 'id')
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Сообщение отправлено директору!',
            parse_mode='Markdown',
            reply_markup=markup_admin
        )
        await bot_aiogram.send_message(
            chat_id=director_id,
            text='Сообщение от администратора:\n' +
                 admin_director_sending_response,
            parse_mode='Markdown',
            reply_markup=markup_admin
        )
        response = Response.admin_message_handler

    await response.set()


def register_handlers_admin(dp: Dispatcher):  # noqa
    """ Регистратор данных для main_bot.py """
    dp.register_message_handler(
        admin_message_handler,
        state=Response.admin_message_handler
    )
    dp.register_message_handler(
        admin_schedule_handler,
        state=Response.admin_schedule_handler
    )
    dp.register_message_handler(
        admin_file_handler,
        content_types=types.ContentTypes.ANY
    )
    dp.register_message_handler(
        admin_send_messages_handler,
        state=Response.admin_send_messages_handler
    )
    dp.register_message_handler(
        admin_mailing_handler,
        state=Response.admin_mailing_handler
    )
    dp.register_message_handler(
        admin_to_director_handler,
        state=Response.admin_to_director_handler
    )
    dp.register_message_handler(
        admin_deferred_handler,
        state=Response.admin_deferred_handler
    )
