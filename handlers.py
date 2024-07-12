from aiogram import types
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import re

# Импортируем клавиатуру
from kb_bot import kb_reg, kb_profile, kb_delete_profile, kb_admin
from state.register import RegisterState 

from database.core import insert_data, select_user, delete_user, select_users

# Обработчик команды /start
async def cmd_start(message: types.Message):
    user_id = message.from_user.id

    if user_id == 894963514:
        await message.answer(f"🤩Приветствую, {message.from_user.full_name}!\nЯ заметил, что вы являетесь администратором!🤩\n\nВам доступен особый список команд.", reply_markup=kb_admin)
    else:
        await message.answer(f"🤩Приветствую, {message.from_user.full_name}!\nДля начала взаимодействия со мной отправьте мне команду!🤩", reply_markup=kb_reg)

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
                         "чтобы быть на связи!\n📱 Формат телефона: +7хххххххххх\n\n⚠️ " + 
                         "Внимание! Я чувствителен к формату!")
    await state.update_data(regname=message.text)
    await state.set_state(RegisterState.regPhone)

async def register_phone(message: types.Message, state: FSMContext):
    if(re.findall(r"^\+[7][-\(]?\d{3}\)?-?\d{3}-?\d{2}-?\d{2}$", message.text)):
        await state.update_data(regphone=message.text)
        reg_data = await state.get_data()

        # Получаем введенные данные
        reg_name = reg_data.get("regname")
        reg_phone = reg_data.get("regphone")
        reg_tgid = message.from_user.id
        
        result = insert_data(reg_name, reg_phone, reg_tgid)

        # Отправляем сообщение в зависимости от результата
        await message.answer(result, reply_markup=kb_profile)
        await state.clear()
    else:
        await message.answer(f"😡 Номер указан в неправильном формате!")

async def get_profile(message: types.Message):
    tgid = message.from_user.id

    # Получаем данные пользователя из бд
    result = select_user(tgid)
    await message.answer(result, reply_markup=kb_delete_profile)
    await message.answer("🥳Отлично!\n\nВам осталось лишь ожидать сообщения от меня!")
    
async def exit_profile(call: types.CallbackQuery):
    # Удаление профиля
    tgid = call.from_user.id

    # Получаем данные пользователя из бд
    result = delete_user(tgid)

    # Удаляем предыдущее сообщение
    await call.message.delete()

    # Отправляем новое сообщение
    await call.message.answer("Профиль удален", reply_markup=None)
    await call.answer(result, show_alert=True)
    
# Админ панель
# Кнопки админ панели
async def get_clients(message: types.Message):
    result = select_users()
    
    await message.answer(result)
    
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
    