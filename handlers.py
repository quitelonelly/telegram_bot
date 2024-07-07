from aiogram import types
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
import re

# Импортируем клавиатуру
from kb_bot import kb, kb_profile, kb_admin 
from state.register import RegisterState 

# Обработчик команды /start
async def cmd_start(message: types.Message):
    user_id = message.from_user.id

    if user_id == 894963514:
        await message.answer(f"🤩Приветствую, {message.from_user.full_name}!\nЯ заметил, что вы являетесь администратором!🤩\n\nВам доступен особый список команд.", reply_markup=kb_admin)
    else:
        await message.answer(f"🤩Приветствую, {message.from_user.full_name}!\nДля начала взаимодействия со мной отправьте мне команду!🤩", reply_markup=kb)

# Обработчик команды /help
async def cmd_help(message: types.Message):
    await message.answer("Вам нужна помощь?😲 По всем вопросам вы можете обращаться сюда\nтут будет номер...📱")

# Обработчик команды /desc
async def cmd_desc(message: types.Message):
    await message.answer(
         "Я бот для записи клиентов на различные процедуры. 💅\n\n"
            "С моей помощью вы можете:\n\n"
            "🔹 Узнать о доступных процедурах\n"
            "🔹 Записаться на удобное для вас время\n"
            "🔹 Получить напоминание о предстоящей записи\n\n"
            "Если у вас есть вопросы, просто напишите мне!"
    )

# Обработчик команды 'Зарегистрироваться'
async def cmd_reg(message: types.Message, state: FSMContext):
    await message.answer("⭐️Давайте начнем регистрацию!⭐️\nПодскажите, как к вам обращаться?")
    await state.set_state(RegisterState.regName)

async def register_name(message: types.Message, state: FSMContext):
    await message.answer(f"☺️ Приятно познакомиться {message.text}!\nТеперь укажите номер телефона, " + 
                         "чтобы быть на связи\n📱 Формат телефона: +7хххххххххх\n\n⚠️ " + 
                         "Внимание! Я чувствителен к формату!")
    await state.update_data(regname=message.text)
    await state.set_state(RegisterState.regPhone)

async def register_phone(message: types.Message, state: FSMContext):
    if(re.findall(r"^\+?[7][-\(]?\d{3}\)?-?\d{3}-?\d{2}-?\d{2}$", message.text)):
        await state.update_data(regphone=message.text)
        reg_data = await state.get_data()

        # Получаем введенные данные
        reg_name = reg_data.get("regname")
        reg_phone = reg_data.get("regphone")

        # Сообщение об успешном прохождении регистрации
        msg = f"Приятно познакомиться {reg_name}! \n\nТелефон: {reg_phone}"
        await message.answer(msg)
        await state.clear()
    else:
        await message.answer(f"😡 Номер указан в неправильном формате!")

async def get_profile(message: types.Message, state: FSMContext):
    reg_data = await state.get_data()

    # Получаем данные от регистрации (Нужно добавить соединение с бд)
    name = reg_data.get("rename")
    phone = reg_data.get("regphone")

    await message.answer(f"Ваш профиль:\n\n🙍‍♀️ Логин: {name}\n📞 Телефон: {phone}", reply_markup=kb_profile)
    
async def exit_profile(callback_query: CallbackQuery):
    # Тут будет логика выхода из аккаунта
    await callback_query.message.edit_text("Вы вышли из профиля. Надеюсь, скоро увидимся снова!")

# Кнопки админ панели (Нужно добавить БД)
async def get_clients(message: types.Message):
    await message.answer(f"📝Вот список ваших клиетов:\n\nКЛИЕНТЫ")
    
async def set_order(message: types.Message):
    # Добавить логику добавления записи (нужна БД)
    await message.answer(f"Пожалуйста, введите ФИО клиента.")

# Функция для регистрации хэндлеров
def reg_handlers(dp: Dispatcher):
    # Команды
    dp.message.register(cmd_start, Command(commands=["start"]))
    dp.message.register(cmd_help, Command(commands=["help"]))
    dp.message.register(cmd_desc, Command(commands=["desc"]))

    # Регистрация и профиль
    dp.message.register(cmd_reg, F.text == "Зарегистрироваться")
    dp.message.register(register_name, RegisterState.regName)
    dp.message.register(register_phone, RegisterState.regPhone)
    dp.message.register(get_profile, F.text == "Профиль")
    dp.callback_query.register(exit_profile, F.data == 'exit')

    # Кнопки админ панели
    dp.message.register(get_clients, F.text == "Клиенты")
    