from aiogram.dispatcher.filters.state import StatesGroup, State


class CheckoutState(StatesGroup):
    start_checkout = State()
    user_name = State()
    user_phone = State()
    user_adress = State()
