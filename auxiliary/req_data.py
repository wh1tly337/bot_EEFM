from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# файл для хранения каких-либо данных

# токен и диспетчер бота
bot_aiogram = Bot(token='5951899941:AAFS1oW1HLkIxR8AQP8i9sSGNEQ0YRtGh50')
dp = Dispatcher(bot_aiogram, storage=MemoryStorage())

# пути до файлов
src_logger = 'logger/'
src_db = 'auxiliary/employee.db'

# ФИО директора, для удобной смены в коде. Файл message_handler.py строка 24
director_name = 'Шешенина Ивана Владимировича'
director_id = ''

