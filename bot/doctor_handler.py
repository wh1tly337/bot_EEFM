from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from auxiliary.all_markups import *
from auxiliary.req_data import *
from workers import (
    db_worker as dbw,
    file_worker as fw,
)


# класс для регистрации состояния сообщений пользователя (используется везде,
# где нужно обрабатывать текстовые сообщения от пользователя)
class Response(StatesGroup):
    doctor_handler = State()
    doctor_schedule_handler = State()
    doctor_week_handler = State()


async def doctor_handler(message: types.Message, state: FSMContext):
    """ Стартовая функция-обработчик сообщений от доктора """
    doctor_response = message.text
    await state.update_data(user_response=doctor_response)

    if doctor_response == 'Получить расписание':
        fio = await dbw.get_data('id', message.chat.id)
        appeal = f"{fio[2]} {fio[3]}"

        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f"{appeal}, на какой период вы хотите посмотреть расписание?",
            parse_mode='Markdown',
            reply_markup=markup_doctor_watch_schedule
        )
        await Response.doctor_schedule_handler.set()
    else:
        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text='Такой команды нет',
            parse_mode='Markdown',
            reply_markup=markup_doctor
        )


async def doctor_schedule_handler(message: types.Message, state: FSMContext):
    """ Функция-обработчик сообщений доктора для получения расписания """
    doctor_schedule_response = message.text  # noqa
    await state.update_data(user_response=doctor_schedule_response)

    doctor_handlers = {
        'Сегодня': {
            'markup': markup_doctor,
            'response': Response.doctor_handler,
            'func': 'today',
        },
        'Неделя': {
            'markup': markup_doctor,
            'response': Response.doctor_handler,
            'func': 'week',
        },
        'Определенный день': {
            'markup': markup_week_doctor,
            'response': Response.doctor_week_handler,
            'message': 'Какой день текущей недели вас интересует?',
        },
        'Отмена': {
            'markup': markup_doctor,
            'response': Response.doctor_handler,
            'message': 'Выберите команду',
        },
        None: {
            'markup': markup_admin_watch_schedule,
            'response': Response.doctor_schedule_handler,
            'message': 'Такой команды нет, воспользуйтесь кнопками ниже',
        }
    }

    command_dict = doctor_handlers.get(doctor_schedule_response)  # noqa
    if not command_dict:
        command_dict = doctor_handlers[None]

    if command_dict.get('func'):
        text = await get_data_form_schedule(message, command_dict.get('func'))
    else:
        text = command_dict.get('message')

    # вариант одним сообщением
    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode='Markdown',
        reply_markup=command_dict.get('markup')
    )
    # вариант несколькими сообщениями
    # for i in range(len(text)):
    #     await bot_aiogram.send_message(
    #         chat_id=message.chat.id,
    #         text=str(text[i]),
    #         parse_mode='Markdown',
    #         reply_markup=command_dict.get('markup')
    #     )

    await command_dict.get('response').set()


async def doctor_week_handler(message: types.Message, state: FSMContext):
    """ Функция-обработчик сообщений доктора для выбора определенного дня """
    doctor_week_response = message.text  # noqa
    await state.update_data(user_response=doctor_week_response)

    day_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница',
                   'Суббота', 'Воскресенье']
    if doctor_week_response in day_of_week:
        day_index = day_of_week.index(doctor_week_response)
    # noinspection PyUnboundLocalVariable
    doctor_handlers = {
        f"{day_of_week[day_index]}": {
            'markup': markup_doctor,
            'response': Response.doctor_handler,
            'day': f"{day_of_week[day_index]}",
        },
        'Отмена': {
            'markup': markup_doctor_watch_schedule,
            'response': Response.doctor_schedule_handler,
            'message': 'Хорошо',
        },
        None: {
            'markup': markup_week_doctor,
            'response': Response.doctor_week_handler,
            'message': 'Такой команды нет, воспользуйтесь кнопками ниже',
        }
    }

    command_dict = doctor_handlers.get(doctor_week_response)  # noqa
    if not command_dict:
        command_dict = doctor_handlers[None]

    if command_dict.get('day'):
        text = await get_data_form_schedule(message, command_dict.get('day'))
    else:
        text = command_dict.get('message')

    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode='Markdown',
        reply_markup=command_dict.get('markup')
    )

    await command_dict.get('response').set()


async def get_data_form_schedule(message, time_period):
    """ Функция-обработчик информации с расписанием для вызвавшего доктора """
    fio = await dbw.get_data('id', message.chat.id),
    fio = f"{fio[0][1]} {fio[0][2]} {fio[0][3]}"

    result = await fw.get_schedule(fio, time_period)

    return result


def register_handlers_doctor(dp: Dispatcher):  # noqa
    """ Регистратор данных для main_bot.py """
    dp.register_message_handler(
        doctor_handler,
        state=Response.doctor_handler
    )
    dp.register_message_handler(
        doctor_schedule_handler,
        state=Response.doctor_schedule_handler
    )
    dp.register_message_handler(
        doctor_week_handler,
        state=Response.doctor_week_handler
    )
