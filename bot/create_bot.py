import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

load_dotenv()

bot = Bot(os.getenv('TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
