from aiogram.fsm.state import StatesGroup, State

class OrderState(StatesGroup):
    ordName = State()
    ordPhone = State()
    ordTime = State()