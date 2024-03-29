import logging

from aiogram.utils import executor

from create_bot import dp, storage
from handlers import menu, cart, checkout, other, order

async def on_startup(_):
    logging.basicConfig(level=logging.INFO)
    menu.register_client_handlers(dp)
    cart.register_cart_handlers(dp)
    checkout.register_chekout_handler(dp)
    other.register_other_handlers(dp)
    order.register_order_handler(dp)

async def shutdown(_):
    await storage.close()

if __name__=='__main__':
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=shutdown
    )
