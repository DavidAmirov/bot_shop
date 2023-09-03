from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from create_bot import bot
from utils import save_subscriber, delete_all_cart_items
from states.client_states import CheckoutState


async def start_checkout(callback: CallbackQuery, state: FSMContext):
    total_amount = callback.data.split(':')[1]
    await CheckoutState.start_checkout.set()
    async with state.proxy() as data:
        data['total_amount'] = total_amount
    ikb = InlineKeyboardMarkup(resize_keyboard=True)
    ikb.add(InlineKeyboardButton(
        'Отмена',
        callback_data='cancel_chekout_processing:'
    ))
    await bot.send_message(
        callback.from_user.id,
        "Давайте уточним данные для доставки.\nПожалуйста, введите имя:",
        reply_markup=ikb
    )


async def checkout_name(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await CheckoutState.user_phone.set()
    ikb = InlineKeyboardMarkup(resize_keyboard=True)
    ikb.add(InlineKeyboardButton(
        'Отмена',
        callback_data='cancel_chekout_processing:'
    ))
    await message.reply('Введите номер телеофна', reply_markup=ikb)


async def checkout_phone(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
    await CheckoutState.user_adress.set()
    ikb = InlineKeyboardMarkup(resize_keyboard=True)
    ikb.add(InlineKeyboardButton(
        'Отмена',
        callback_data='cancel_chekout_processing:'
    ))
    await message.reply('Введите адрес доставки', reply_markup=ikb)


async def checkout_adress(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['adress'] = message.text

        name = data['name']
        phone = data['phone']
        adress = data['adress']
        total_amount = data['total_amount']
    
    save_subscriber(message.from_user.id, name, phone, adress)

    ikb = InlineKeyboardMarkup(resize_keyboard=True)
    ikb.add(InlineKeyboardButton(
        'Заказать',
        callback_data=f'process_order:{message.from_user.id}'
    ))
    ikb.add(InlineKeyboardButton(
        'Отменить',
        callback_data='cancel_chekout_processing:'
    ))
    await bot.send_message(
        message.from_user.id,
        f'Ваш данные приняты: {name}, {adress}, {phone}',
        reply_markup=ikb
    )

    await state.finish()


def register_chekout_handler(dp: Dispatcher):
    dp.register_callback_query_handler(start_checkout, Text(startswith='confirm_checkout:'), state=None)
    dp.register_message_handler(checkout_name, state=CheckoutState.start_checkout)
    dp.register_message_handler(checkout_phone, state=CheckoutState.user_phone)
    dp.register_message_handler(checkout_adress, state=CheckoutState.user_adress)