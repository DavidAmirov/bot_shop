from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from create_bot import bot
from utils import get_cart_by_user, change_cart_quantity


async def process_cart(message: types.Message):
    user_cart = get_cart_by_user(message.from_user.id)

    if len(user_cart) < 1:
        await message.answer('Ваша корзина пуста.')
    else:
        for product in user_cart:
            name = product['name']
            price = product['price']
            quantity = product['quantity']
            cart_id = product['cart_id']

            ikb = InlineKeyboardMarkup(resize_keyboard=True)

            ikb.row(InlineKeyboardButton(
                f'Кол-во:{quantity}    ➕',
                callback_data=f'increase:{message.from_user.id}:{cart_id}:{name}:{price}'
            ),
            InlineKeyboardButton(
                f'Кол-во:{quantity}     ➖',
                callback_data=f'decrease:{message.from_user.id}:{cart_id}:{name}:{price}'
            ))
            ikb.add(InlineKeyboardButton(
                f'Удалить товар из корзины\n кол-во:{quantity}',
                callback_data=f'del:{message.from_user.id}:{cart_id}:{name}:{price}'
                ))
            await bot.send_message(message.from_user.id, f'{name} {price}₽', reply_markup=ikb)
        ikb2 = InlineKeyboardMarkup(resize_keyboard=True)
        ikb2.add(InlineKeyboardButton(
            'Оформить заказ',
            callback_data=f'checkout:{message.from_user.id}'
        ))
        await bot.send_message(message.from_user.id, 'Оформить заказ?', reply_markup=ikb2)


async def change_quantity(callback: types.CallbackQuery):
    data = callback.data.split(':')
    action = data[0]
    cart_id = data[2]
    name = data[3]
    price = data[4]

    quantity = change_cart_quantity(cart_id, action)

    if quantity in (0, None):
        await callback.answer('Товар удален из корзины')
        await callback.message.delete()
    else:
        ikb = InlineKeyboardMarkup(resize_keyboard=True)

        ikb.row(InlineKeyboardButton(
            f'Кол-во:{quantity}     ➕',
            callback_data=f'increase:{callback.from_user.id}:{cart_id}:{name}:{price}'
        ),
        InlineKeyboardButton(
            f'Кол-во:{quantity}     ➖',
            callback_data=f'decrease:{callback.from_user.id}:{cart_id}:{name}:{price}'
        ))
        ikb.add(InlineKeyboardButton(
            f'Удалить товар из корзины\n кол-во:{quantity}',
            callback_data=f'del:{callback.from_user.id}:{cart_id}:{name}:{price}'
        ))
        await callback.message.edit_reply_markup(ikb)


async def confirm_checkout(message: types.Message):
    cart_products = get_cart_by_user(message.from_user.id)
    text = 'Ваш заказ:\n'
    total_amount = 0
    for product in cart_products:
        product_amount = product['quantity'] * product['price']

        text += f'{product["name"]}    {product["quantity"]} * {product["price"]} = {product_amount}\n'

        total_amount += product_amount
    
    text +=f'Общая сумма к оплате: {total_amount}'
    await bot.send_message(message.from_user.id, text)
    ikb = InlineKeyboardMarkup(resize_keyboard=True)
    ikb.add(InlineKeyboardButton(
        'Все верно, продолжить',
        callback_data=f'confirm_checkout:{total_amount}'
    ))
    ikb.add(InlineKeyboardButton(
        'Вернуться в корзину',
        callback_data=f'back_to_cart:'
    ))
    await bot.send_message(message.from_user.id, 'Все указано верно?', reply_markup=ikb)


def register_cart_handlers(dp: Dispatcher):
    dp.register_message_handler(process_cart, text='Корзина')
    dp.register_callback_query_handler(process_cart, Text(startswith='back_to_cart:'))
    dp.register_callback_query_handler(
        change_quantity, lambda callback_query: callback_query.data.startswith('increase:')
        or callback_query.data.startswith('decrease:') or callback_query.data.startswith('del:')
    )
    dp.register_callback_query_handler(confirm_checkout, Text(startswith='checkout:'))