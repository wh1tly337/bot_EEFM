from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from auxiliary.all_markups import *
from auxiliary.req_data import *
from workers import db_worker as dbw


class Response(StatesGroup):
    doctor_handler = State()
    doctor_schedule_handler = State()


async def doctor_handler(message: types.Message, state: FSMContext):
    doctor_response = message.text
    await state.update_data(user_response=doctor_response)

    if doctor_response == 'Получить расписание':
        fio = await dbw.get_data('id', message.chat.id)
        appeal = f"{fio[2]} {fio[3]}"

        await bot_aiogram.send_message(
            chat_id=message.chat.id,
            text=f"{appeal}, на какой период вы хотите посмотреть расписание?",
            parse_mode='Markdown',
            reply_markup=markup_admin_watch_schedule
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
    doctor_schedule_response = message.text  # noqa
    await state.update_data(user_response=doctor_schedule_response)

    doctor_handlers = {
        'На сегодня': {
            'markup': markup_doctor,
            'response': Response.doctor_handler,
            'message': 'Расписание на сегодня:',
            'func': ...,
            # TODO добавить возможность смотреть расписание на сегодня
        },
        'На неделю': {
            'markup': markup_doctor,
            'response': Response.doctor_handler,
            'message': 'Расписание на наделю:',
            'func': ...,
            # TODO добавить возможность смотреть расписание на неделю
        },
        'Отмена': {
            'markup': markup_doctor,
            'response': Response.doctor_handler,
            'message': 'Хорошо',
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
    await bot_aiogram.send_message(
        chat_id=message.chat.id,
        text=command_dict.get('message'),
        parse_mode='Markdown',
        reply_markup=command_dict.get('markup')
    )

    if command_dict.get('func'):
        await command_dict.get('func')

    await command_dict.get('response').set()


# регистратор передающий данные в main_bot.py
def register_handlers_doctor(dp: Dispatcher):  # noqa
    dp.register_message_handler(
        doctor_handler,
        state=Response.doctor_handler
    )
    dp.register_message_handler(
        doctor_schedule_handler,
        state=Response.doctor_schedule_handler
    )
