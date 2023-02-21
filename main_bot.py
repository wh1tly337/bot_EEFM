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

# TODO убрать оповещение/незначительную ошибку, которая вылезает
#  при старте программы/нажатиях на клавиши (сама ошибка ниже)

# C:\Users\wh1tly337\AppData\Local\Programs\Python\Python311\Lib\site-packages
# \aiogram\dispatcher\handler.py:117: RuntimeWarning: coroutine 'State.set'
# was never awaited
#   response = await handler_obj.handler(*args, **partial_data)
# RuntimeWarning: Enable tracemalloc to get the object allocation traceback

# создание/открытие и запись данных в логгер при запуске бота
logger.add(
    f"{src_logger}logger.txt",
    format='{time} | {level} | {message}',
    rotation='1 week',
    compression='zip'
)

# регистрация команд в боте (берутся из других файлов, смотреть в импорте)
bc.register_handlers_default_commands(dp)
mh.register_handlers_authorization(dp)
doch.register_handlers_doctor(dp)
ah.register_handlers_admin(dp)
dirh.register_handlers_director(dp)


# функция для отправки стартового сообщения всем пользователям
async def startup_message(_):
    # рабочий вариант
    # all_ids = await dbw.get_all_ids()
    # for i in range(len(all_ids)):
    #     await bot_aiogram.send_message(
    #         all_ids[i],
    #         'Бот был перезапущен, для его работы необходимо ввести /start')

    # тестовый вариант
    user_id = 726420734
    await bot_aiogram.send_message(
        user_id,
        'Бот был перезапущен, для его работы необходимо ввести /start')


if __name__ == '__main__':
    logger.info('Bot successfully started')
    executor.start_polling(dp, on_startup=startup_message)
