from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from auxiliary.all_markups import *
from auxiliary.req_data import *
from bot import (
    bot_commands as bc,
)
from workers import (
    db_worker as dbw,
    file_worker as fw
)


class Response(StatesGroup):
    admin_message_handler = State()
    admin_schedule_handler = State()
    admin_watch_schedule_handler = State()
    admin_send_messages_handler = State()
    admin_mailing_handler = State()
    admin_to_director_handler = State()


# TODO подумать над проверкой должности

# функция-обработчик сообщений стартовой страницы админа
async def admin_message_handler(message: types.Message, state: FSMContext):
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


# функция-обработчик сообщений второй страницы расписания для админа
async def admin_schedule_handler(message: types.Message, state: FSMContext):
    admin_schedule_response = message.text
    await state.update_data(user_response=admin_schedule_response)

    admin_handlers = {
        'Получить шаблон': {
            'markup': markup_admin,
            'response': Response.admin_message_handler,
            'message': 'Шаблон расписания:',
            'func': bot_aiogram,
        },
        'Загрузить расписание': {
            'markup': markup_cancel,
            'finish': state,
            'message': 'Отправьте мне Excel файл с расписанием',
        },
        'Посмотреть расписание': {
            'markup': markup_admin_watch_schedule,
            'response': Response.admin_watch_schedule_handler,
            'message': 'На какой период вы хотите посмотреть расписание?',
        },
        'Отмена': {
            'markup': markup_admin,
            'response': Response.admin_message_handler,
            'message': 'Хорошо',
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
        await command_dict.get('func').send_document(
            chat_id=message.chat.id,
            document=open(f"{src_schedule_template}", 'rb')
        )

    if command_dict.get('response'):
        await command_dict.get('response').set()
    elif command_dict.get('finish'):
        await command_dict.get('finish').finish()


# функция-обработчик файла расписания от админа
async def admin_file_handler(message: types.Message):
    # TODO в этой проверке ошибка
    #  (загрузить расписание -> отмена -> заново регистрирует)
    #  (не включается второй else, тк проходит проверку текст из первого if)
    if message.text:
        await bc.start_message(message)
    else:
        if message.document and (
                message.document.file_name[-4:] == 'xlsx' or
                message.document.file_name[-3:] == 'xls'
        ):
            await message.document.download(
                destination_file=f"{src_files}{message.document.file_name}")

            filename = message.document.file_name.split('.')
            ender = filename[1]
            filename = filename[0]
            fw.all_cycle(filename, ender)

            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Расписание получено!',
                parse_mode='Markdown',
                reply_markup=markup_admin
            )
            response = Response.admin_message_handler

            # TODO возможно сделать рассылку всему персоналу о том
            #  что расписание обновилось
        else:
            if message.text == 'Отмена':
                message_text = 'Хорошо'
            else:
                message_text = 'Это не является расписанием, попробуйте еще раз'

            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text=message_text,
                parse_mode='Markdown',
                reply_markup=markup_admin_make_schedule
            )
            response = Response.admin_schedule_handler

        await response.set()


# функция-обработчик сообщений третьей страницы расписания для админа
async def admin_watch_schedule_handler(message: types.Message,
                                       state: FSMContext):
    admin_watch_schedule_response = message.text  # noqa
    await state.update_data(user_response=admin_watch_schedule_response)

    admin_handlers = {
        'На сегодня': {
            'markup': markup_admin,
            'response': Response.admin_message_handler,
            'message': 'Расписание на сегодня:',
            'func': ...,
            # TODO добавить возможность смотреть расписание на сегодня
        },
        'На неделю': {
            'markup': markup_admin,
            'response': Response.admin_message_handler,
            'message': 'Расписание на наделю:',
            'func': ...,
            # TODO добавить возможность смотреть расписание на неделю
        },
        'Отмена': {
            'markup': markup_admin_make_schedule,
            'response': Response.admin_schedule_handler,
            'message': 'Хорошо',
        },
        None: {
            'markup': markup_admin_watch_schedule,
            'response': Response.admin_watch_schedule_handler,
            'message': 'Такой команды нет, воспользуйтесь кнопками ниже',
        }
    }

    command_dict = admin_handlers.get(admin_watch_schedule_response)  # noqa
    if not command_dict:
        command_dict = admin_handlers[None]
    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=command_dict.get('message'),
        parse_mode='Markdown',
        reply_markup=command_dict.get('markup')
    )

    if command_dict.get('func'):
        await command_dict.get('func')

    await command_dict.get('response').set()


# функция-обработчик сообщений второй страницы рассылки для админа
async def admin_send_messages_handler(message: types.Message,
                                      state: FSMContext):
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
            'message': 'Хорошо',
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


# функция-обработчик сообщений от админа для перенаправления получателю
async def admin_mailing_handler(message: types.Message, state: FSMContext):
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


# регистратор передающий данные в main_bot.py
def register_handlers_admin(dp: Dispatcher):  # noqa
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
        admin_watch_schedule_handler,
        state=Response.admin_watch_schedule_handler
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
