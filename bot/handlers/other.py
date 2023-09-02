from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup

async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Каталог").add('Корзина')
    
    await callback.message.reply('Отменено.', reply_markup=markup)


def register_other_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(cancel_handler, Text(startswith='cancel_chekout_processing'), state='*')
