import asyncio
import os
from datetime import (
    datetime as dt,
    timedelta as td,
)

from aiogram import executor
from loguru import logger

from auxiliary.req_data import *
from bot import (
    bot_commands as bc,
    message_handler as mh,
    doctor_handler as doch,
    admin_handler as ah,
    director_handler as dirh
)
from workers import (
    db_worker as dbw,
    file_worker as fw
)

# TODO добавить logger в функцию (осталось только Саше в director_handler
#  и свои функции в db_worker)

# TODO проработать комментарии (осталось только Саше в director_handler
#  и свои функции в db_worker)

# TODO вывод расписания для админа и директора в формате pdf


# создание/открытие и запись данных в логгер при запуске бота
logger.add(
    f"{src_logger}logger.txt",
    format='{time} | {level} | {message}',
    rotation='1 week',
    compression='zip'
)

# регистрация команд/сообщений в боте
bc.register_handlers_default_commands(dp)
mh.register_handlers_authorization(dp)
doch.register_handlers_doctor(dp)
ah.register_handlers_admin(dp)
dirh.register_handlers_director(dp)

# TODO сделать удаление директором документов, у которых вышел срок

deep_counter = 0
today = None


async def admin_schedule_notification():
    """Функция для напоминания админу о необходимости обновления расписания."""
    global deep_counter, today

    if (
            dt.weekday(dt.now()) == 6 and
            os.path.exists('auxiliary/deferred_schedule.xlsx') is False and
            dt.now != today and
            int(dt.now().strftime('%H')) > 10
    ):
        admin_id = await dbw.get_data('post', 'admin', 'id')
        await bot_aiogram.send_message(
            admin_id,
            "Не забудьте, завтра расписание перестанет быть актуальным.\n"
            "Для вашего удобства в боте реализована функция отложенной "
            "загрузки расписания, благодаря ей вы точно не забудете его "
            "обновить, а если вы не доверяете боту, то просто сами загрузите "
            "расписание в понедельник\n"
            "P.S. Это автоматическое напоминание и оно приходит только в том "
            "случае, если вы не загрузили расписание отложено"
        )
        today = dt.now().strftime('%d.%m.%Y')
    else:
        doctor = await dbw.get_data('post', 'doctor')
        doctor = f"{doctor[1]} {doctor[2]} {doctor[3]}"
        result = fw.get_data_from_schedule(doctor)

        if (
                dt.weekday(dt.now()) == 0 and
                result == (dt.now() - td(days=2)).strftime('%d.%m.%Y') and
                dt.now != today and
                int(dt.now().strftime('%H')) > 8
        ):
            admin_id = await dbw.get_data('post', 'admin', 'id')
            await bot_aiogram.send_message(
                admin_id,
                "Вы не обновили расписание, доктора в растерянности, они не "
                "знают что сегодня им нужно работать"
            )
            today = dt.now().strftime('%d.%m.%Y')

    if deep_counter == 1:
        deep_counter = 0
        return
    while True:
        await asyncio.sleep(1800)
        deep_counter += 1
        await admin_schedule_notification()


async def check_documents():
    global deep_counter
    documents = await dbw.get_all_documents()
    now_time = dt.now()
    director_id = await dbw.get_data('post', 'director', 'id')
    for document in documents:
        doc_time = dt.strptime(document[2], '%d.%m.%Y')
        delta_time = (doc_time - now_time).days
        if delta_time < 100:
            emp_fio = await dbw.get_data('id', document[0])

            await bot_aiogram.send_message(
                director_id,
                f"Документ: {document[1]}\n"
                f"Сотрудник: {emp_fio[1]} {emp_fio[2]} {emp_fio[3]}\n"
                f"До конца действия: {delta_time} дней\n"
                f"Истекает: {doc_time.strftime('%d.%m.%Y')}"
            )
    if deep_counter == 1:
        deep_counter = 0
        return
    while True:
        await asyncio.sleep(10)
        deep_counter += 1
        await check_documents()


async def startup_message(_):
    """Функция для отправки стартового сообщения о перезапуске всем юзерам."""
    try:
        # TODO поменять на рабочий вариант

        # рабочий вариант
        # all_ids = await dbw.get_all_ids()
        # for i in range(len(all_ids)):
        #     await bot_aiogram.send_message(
        #         all_ids[i],
        #         'Бот был перезапущен, для его работы необходимо ' \
        #         'отправить /start или любое сообщение боту'

        # тестовый вариант
        user_id = 726420734
        # user_id = 577906481
        await bot_aiogram.send_message(
            user_id,
            'Бот был перезапущен, для его работы необходимо отправить /start '
            'или любое сообщение боту'
        )
        logger.info('The initial mailing was made successfully')
    except Exception as ex:
        logger.error(ex)


async def shutdown_move(_):
    """Функция для logout user для корректной работы admin_file_handler."""
    try:
        await dbw.logout_user()
        logger.info('All users have been successfully logged out')
    except Exception as ex:
        logger.error(ex)


if __name__ == '__main__':
    logger.info('Bot successfully started')

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # TODO не забыть включить вызов функций проверки
        # asyncio.ensure_future(check_documents(), loop=loop)
        asyncio.ensure_future(admin_schedule_notification(), loop=loop)
        asyncio.ensure_future(executor.start_polling(
            dp,
            on_startup=startup_message,
            on_shutdown=shutdown_move
        ), loop=loop)
        loop.run_forever()
    except Exception:
        pass
