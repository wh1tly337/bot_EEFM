from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# файл для хранения каких-либо данных

# токен и диспетчер бота
bot_aiogram = Bot(token='5951899941:AAFS1oW1HLkIxR8AQP8i9sSGNEQ0YRtGh50')
dp = Dispatcher(bot_aiogram, storage=MemoryStorage())

# путь логгера
src_logger = 'logger/'

# временный пароль создаваемый директором
temporary_password = '123'

# ФИО директора, для удобной смены в коде. Файл message_handler.py строка 24
boss = 'Шешенина Ивана Владимировича'
