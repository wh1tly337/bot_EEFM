from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# файл для хранения константных данных

# токен и диспетчер бота
bot_aiogram = Bot(token='5951899941:AAFS1oW1HLkIxR8AQP8i9sSGNEQ0YRtGh50')
dp = Dispatcher(bot_aiogram, storage=MemoryStorage())

# пути до файлов
src_logger = 'logger/'
src_files = 'workers/'
src_deferred_schedule = 'auxiliary/'
src_current_schedule = 'workers/current_schedule.xlsx'
src_schedule_template = 'auxiliary/schedule_template.xlsx'
src_db = 'auxiliary/employee.db'


# ФИО директора, для удобной смены в коде
director_name = 'Шешенина Ивана Владимировича'

# код создания таблицы бд
# CREATE TABLE users
# (
#     id           INTEGER,
#     surname      VARCHAR(255),
#     name         VARCHAR(255),
#     patronymic   VARCHAR(255),
#     username     VARCHAR(255),
#     post         VARCHAR(13),
#     log_stat     INTEGER DEFAULT 0,
#     date_added   DATE,
#     date_removed DATE
# );
