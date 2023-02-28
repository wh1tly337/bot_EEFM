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
from workers import db_worker as dbw

# TODO отрефакторить код по pep8 через flake8

# TODO добавить logger в функцию

# TODO проработать комментарии (осталось только Саше в director_handler
#  и свои функции в db_worker)

# TODO добавить связь докторов с директором/администратором (ждем ответ от Вани)

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


async def startup_message(_):
    """ Функция для отправки стартового сообщения о перезапуске всем юзерам """

    # TODO поменять на рабочий вариант

    # рабочий вариант
    # all_ids = await dbw.get_all_ids()
    # for i in range(len(all_ids)):
    #     await bot_aiogram.send_message(
    #         all_ids[i],
    #         'Бот был перезапущен, для его работы необходимо ввести /start')

    # тестовый вариант
    user_id = 726420734
    # user_id = 577906481
    await bot_aiogram.send_message(
        user_id,
        'Бот был перезапущен, для его работы необходимо отправить /start '
        'или любое сообщение боту'
    )


async def shutdown_move(_):
    """ Функция для logout user для корректной работы admin_file_handler """
    await dbw.logout_user()


if __name__ == '__main__':
    logger.info('Bot successfully started')
    executor.start_polling(
        dp,
        on_startup=startup_message,
        on_shutdown=shutdown_move
    )
