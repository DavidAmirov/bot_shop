from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup

from create_bot import bot, dp

MAIN_MENU = ["Каталог", "Корзина", "FAQ"]


async def cmd_start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for item in MAIN_MENU:
        markup.add(item)
    await bot.send_message(chat_id=message.chat.id, text="Добро пожаловать!", reply_markup=markup)


async def process_category(message: types.Message):
    await bot.send_message(
        message.from_user.id, f'Пожалуйста, выберите категорию')




def register_client_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start')
    dp.register_message_handler(process_category, text='Каталог')

