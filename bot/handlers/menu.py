from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup

from create_bot import bot, dp
from utils import add_to_cart, get_categories, get_subcategories, get_products

MAIN_MENU = ["Каталог", "Корзина"]


async def cmd_start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
    for item in MAIN_MENU:
        markup.add(item)
    text = 'Добро пожаловать в наш бот, который поможет вам сделать покупки в любое время суток.'
    text += 'Для этого просто выберите продуткы с каталога(при нажатии на цену добавляется один продукт в корзину),'
    text += ' перейдите в корзину, убедитесь что количество товара указано верно,'
    text += ' укажите свои данные и ожидайте свой заказ.'
    text += ' Техподдержка: @Dtalish'
    await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=markup)


async def process_category(message: types.Message):
    ikb = InlineKeyboardMarkup(row_width=2)
    for cat in get_categories():
        name = cat['name']
        category_id = cat['id']
        ikb.insert(InlineKeyboardButton(text=name, callback_data=f'category_id:{category_id}'))
    await bot.send_message(
        message.from_user.id, f'Пожалуйста, выберите категорию', reply_markup=ikb
    )


async def process_subcategory(callback: CallbackQuery):
    data = callback.data
    category_id = data.split(':')[1]
    ikb = InlineKeyboardMarkup(row_width=2)
    ikb.insert(InlineKeyboardButton('Вернуться назад', callback_data='katalog:'))
    for subcat in get_subcategories(category_id):
        name = subcat['name']
        subcategory_id = subcat['id']
        ikb.insert(InlineKeyboardButton(text=name, callback_data=f'subcat_id:{subcategory_id}'))
    #await bot.send_message(
    #    callback.from_user.id, f'Выберите подкатегорию', reply_markup=ikb
    #)
    await callback.message.edit_reply_markup(ikb)  
    await callback.answer()


async def process_products(callback: CallbackQuery):
    subcategory_id = callback.data.split(':')[1]
    products = get_products(subcategory_id)
    if len(products) < 1:
        await bot.send_message(callback.from_user.id, 'Тут пока пусто.')
    else:
        for product in products:
            product_id = product['id']
            name = product['name']
            price = product['price']
            ikb = InlineKeyboardMarkup(resize_keyboard=True)
            ikb.add(
                InlineKeyboardButton(f'{price}₽',
                callback_data=f'added:{product_id}:{name}')
            )
            await bot.send_message(callback.from_user.id, f'{name}', reply_markup=ikb)


async def process_to_cart(callback: CallbackQuery):
    product_id = callback.data.split(':')[1]
    name = callback.data.split(':')[2]
    result = add_to_cart(callback.from_user.id, product_id)
    await callback.answer(f'{name} добавлен в количестве {result}')


def register_client_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start')
    dp.register_message_handler(process_category, text='Каталог')
    dp.register_callback_query_handler(process_category, Text(startswith='katalog'))
    dp.register_callback_query_handler(process_subcategory, Text(startswith='category_id'))
    dp.register_callback_query_handler(process_products, Text(startswith='subcat_id'))
    dp.register_callback_query_handler(process_to_cart, Text(startswith='added'))
