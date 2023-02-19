from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from auxiliary.all_markups import *
from auxiliary.req_data import *
from workers import db_worker as dbw


# TODO match/case работают медленнее чем if/else,
#  так что нужно поменять на что-то другое

class Response(StatesGroup):
    admin_message_handler = State()
    admin_schedule_handler = State()
    admin_file_handler = State()
    admin_watch_schedule_handler = State()
    admin_send_messages_handler = State()
    admin_mailing_handler = State()
    admin_to_director_handler = State()


# функция-обработчик сообщений стартовой страницы админа
async def admin_message_handler(message: types.Message, state: FSMContext):
    admin_response = message.text
    await state.update_data(user_response=admin_response)
    admin_start_handlers = {
        'Расписание': {
            'markup': markup_admin_make_schedule,
            'response': Response.admin_schedule_handler.set(),
            'message': 'Что вы хотите сделать с раписанием',
        },
        'Отправить сообщение': {
            'markup': markup_admin_message,
            'response': Response.admin_send_messages_handler.set(),
            'message': 'Кому вы хотите отправить сообщение?',
        },
        None: {
            'markup': markup_admin,
            'response': Response.admin_message_handler.set(),
            'message': 'Такой команды нет, воспользуйтесь кнопками ниже',
        }
    }
    command_dict = admin_start_handlers.get(admin_response)
    if not command_dict:
        command_dict = admin_start_handlers[None]
    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=command_dict.get('message'),
        parse_mode='Markdown',
        reply_markup=command_dict.get('markup')
    )
    await command_dict.get('response')


# функция-обработчик сообщений второй страницы расписания для админа
async def admin_schedule_handler(message: types.Message,
                                 state: FSMContext):
    admin_schedule_response = message.text
    await state.update_data(user_response=admin_schedule_response)
    match admin_schedule_response:
        case 'Получить шаблон':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Шаблон расписания:',
                parse_mode='Markdown',
                reply_markup=markup_admin
            )
            await bot_aiogram.send_document(
                chat_id=message.chat.id,
                document=open(f"{src_schedule_template}", 'rb')
            )
        case 'Загрузить расписание':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Отправьте мне Excel файл с расписанием',
                parse_mode='Markdown',
                reply_markup=markup_admin
            )
            await Response.admin_file_handler.set()
        case 'Посмотреть расписание':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='На какой период вы хотите посмотреть расписание?',
                parse_mode='Markdown',
                reply_markup=markup_admin_watch_schedule
            )
            await Response.admin_watch_schedule_handler.set()
        case 'Отмена':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Хорошо',
                parse_mode='Markdown',
                reply_markup=markup_admin
            )
            await Response.admin_message_handler.set()
        case _:
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Нет такой команды, воспользуйтесь кнопками ниже',
                parse_mode='Markdown',
                reply_markup=markup_admin_make_schedule
            )


# функция-обработчик файла расписания от админа
async def admin_file_handler(message: types.Message, state: FSMContext):
    admin_file_response = message.text
    await state.update_data(user_response=admin_file_response)
    # TODO функция обработке присылаемого файла расписания и загрузка его в бд

    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text='Расписание получено!',
        parse_mode='Markdown',
        reply_markup=markup_admin
    )
    await Response.admin_message_handler.set()


# функция-обработчик сообщений третьей страницы расписания для админа
async def admin_watch_schedule_handler(message: types.Message,
                                       state: FSMContext):
    admin_watch_schedule_response = message.text
    await state.update_data(user_response=admin_watch_schedule_response)

    match admin_watch_schedule_response:
        case 'На сегодня':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Расписание на сегодня:',
                parse_mode='Markdown',
                reply_markup=markup_admin
            )
            await Response.admin_message_handler.set()
            # TODO добавить возможность смотреть расписание на сегодня
        case 'На неделю':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Расписание на наделю:',
                parse_mode='Markdown',
                reply_markup=markup_admin
            )
            await Response.admin_message_handler.set()
            # TODO добавить возможность смотреть расписание на неделю
        case 'Отмена':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Хорошо',
                parse_mode='Markdown',
                reply_markup=markup_admin_make_schedule
            )
            await Response.admin_schedule_handler.set()
        case _:
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Нет такой команды, воспользуйтесь кнопками ниже',
                parse_mode='Markdown',
                reply_markup=markup_admin_watch_schedule
            )


# функция-обработчик сообщений второй страницы рассылки для админа
async def admin_send_messages_handler(message: types.Message,
                                      state: FSMContext):
    admin_mailing_response = message.text
    await state.update_data(user_response=admin_mailing_response)

    match admin_mailing_response:
        case 'Рассылка':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Отправьте мне сообщение, которое вы хотите разослать'
                     ' всем сотрудникам',
                parse_mode='Markdown',
                reply_markup=markup_cancel
            )
            await Response.admin_mailing_handler.set()
        case 'Директору':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Отправьте мне сообщение для директора',
                parse_mode='Markdown',
                reply_markup=markup_cancel
            )
            await Response.admin_to_director_handler.set()
        case 'Отмена':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Хорошо',
                parse_mode='Markdown',
                reply_markup=markup_admin
            )
            await Response.admin_message_handler.set()
        case _:
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Нет такой команды, воспользуйтесь кнопками ниже',
                parse_mode='Markdown',
                reply_markup=markup_admin_message
            )


# функция-обработчик сообщений от админа для перенаправления получателю
async def admin_mailing_handler(message: types.Message, state: FSMContext):
    admin_sending_response = message.text
    await state.update_data(user_response=admin_sending_response)

    match admin_sending_response:
        case 'Отмена':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Хорошо',
                parse_mode='Markdown',
                reply_markup=markup_admin_message
            )
            await Response.admin_send_messages_handler.set()
        case _:
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
            await Response.admin_message_handler.set()


# функция-обработчик сообщений от админа для перенаправления получателю
async def admin_to_director_handler(message: types.Message, state: FSMContext):
    admin_director_sending_response = message.text
    await state.update_data(user_response=admin_director_sending_response)

    match admin_director_sending_response:
        case 'Отмена':
            await bot_aiogram.send_message(
                chat_id=message.chat.id,
                text='Хорошо',
                parse_mode='Markdown',
                reply_markup=markup_admin_message
            )
            await Response.admin_send_messages_handler.set()
        case _:
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
            await Response.admin_message_handler.set()


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
        state=Response.admin_file_handler
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
