import logging

from aiogram.utils import executor

from create_bot import dp, storage
from handlers import menu

async def on_startup(_):
    logging.basicConfig(level=logging.INFO)
    menu.register_client_handlers(dp)

async def shutdown(_):
    await storage.close()

if __name__=='__main__':
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=shutdown
    )
