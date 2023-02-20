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

# создание/открытие и запись данных в логгер при запуске бота
logger.add(
    f"{src_logger}logger.txt",
    format='{time} | {level} | {message}',
    rotation='00:00',
    compression='zip'
)

# регистрация команд в боте (берутся из других файлов, смотреть в импорте)
bc.register_handlers_default_commands(dp)
mh.register_handlers_authorization(dp)
doch.register_handlers_doctor(dp)
ah.register_handlers_admin(dp)
dirh.register_handlers_director(dp)

if __name__ == '__main__':
    logger.info('Bot successfully started')
    # TODO сделать рассылку на все id в бд чтобы написали /start
    executor.start_polling(dp)
