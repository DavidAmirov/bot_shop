from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery

from create_bot import bot, dp
from utils import delete_all_cart_items, get_cart_by_user, get_subscriber, save_order_to_excel

async def successful_order(callback: CallbackQuery):
    user_id = callback.data.split(':')[1]
    username, phone, adress = get_subscriber(user_id)
    cart_products = get_cart_by_user(user_id)
    text = 'Ваш заказ:\n'
    total_amount = 0
    for product in cart_products:
        product_amount = product['quantity'] * product['price']

        text += f'{product["name"]}    {product["quantity"]} * {product["price"]} = {product_amount}\n'

        total_amount += product_amount
    
    text += f'Общая сумма к оплате: {total_amount}\n'
    text += 'Техподдержка: @Dtalish'

    await bot.send_message(
        user_id,
        f'{username}, ваш заказ успешно принят.\nОжидайте заказ по адресу {adress}\n'
        f'{text}'
    )
    await bot.send_message(
        394131423,
        f'{adress}, {phone}, {username}\n{text}'
    )
    save_order_to_excel(username, phone, adress, total_amount)
    delete_all_cart_items(user_id)


def register_order_handler(dp: Dispatcher):
    dp.register_callback_query_handler(successful_order, Text(startswith='process_order'))
