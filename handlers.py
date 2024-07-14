from aiogram import types
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv
import os

import re

from database.config import settings

# Импортируем клавиатуру
from kb_bot import kb_reg, kb_profile, kb_delete_profile, kb_admin
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from state.register import RegisterState 

from database.core import insert_user, select_user_profile, delete_user, select_users, create_kb, select_users_order, get_username_by_tgid

# Обработчик команды /start
async def cmd_start(message: types.Message):
    user_id = message.from_user.id

    admin_ids = settings.admin_ids
    if user_id in admin_ids:
        await message.answer(f"🤩Приветствую, {message.from_user.full_name}!\nЯ заметил, что вы являетесь администратором!🤩\n\nВам доступен особый список команд.", reply_markup=kb_admin)
    else:
        await message.answer(f"🤩Приветствую, {message.from_user.full_name}!\nДля начала взаимодействия со мной отправьте мне команду!🤩", reply_markup=kb_reg)

# Обработчик команды /help
async def cmd_help(message: types.Message):
    await message.answer("Вам нужна помощь?😲 По всем вопросам вы можете обращаться сюда\n\n... 📱")
    # https://t.me/AnastasiyaG_1983

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
    
# Обработчик команды /services
async def cmd_serv(message: types.Message):
    await message.answer(
        "📋Список предоставляемых услуг:\n\n"
            "💅Дизайн(1 ноготок) — 50-300💸\n"
            "Маникюр + укрепление + 1 тон:\nдлина S — 1400-1500💸\n"
                                                "длина M — 1500💸\n"
                                                "длина L — 1600💸\n"
            "______________________________________\n\n"
            "Маникюр без покрытия — 600💸\n"
            "______________________________________\n\n"
            "Наращивание, моделирование:\nдлина S —\n"
                                                "длина M — 2000💸\n"
                                                "длина L — 2500💸\n"
            "______________________________________\n\n"
            "Французский маникюр:\nдлина S — 1500💸\n"
                                                "длина M — 1600💸\n"
                                                "длина L — 1700💸\n"
            "______________________________________\n\n"
            "👣Педикюр полный — 2000💸\n"
            "Педикюр(пальчики/покрытие) — 1700💸\n"
            "Педикюр(полная обработка без покрытия) — 1700💸"
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
        
        result = insert_user(reg_name, reg_phone, reg_tgid)

        # Отправляем сообщение в зависимости от результата
        await message.answer(result, reply_markup=kb_profile)
        await state.clear()
    else:
        await message.answer(f"😡 Номер указан в неправильном формате!")

async def get_profile(message: types.Message):
    tgid = message.from_user.id

    # Получаем данные пользователя из бд
    result = select_user_profile(tgid)
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
    
# Обработка кнопки "Записать"
async def set_order(message: types.Message):
    users = select_users_order()
    keyboard = create_kb(users)
    
    await message.answer("Давайте запишем клиента на процедуру! Выберите клиента из клавиатуры.", reply_markup=keyboard)
    
# Сообщение с подтверждением выбранного клиента
async def handle_client_selection(callback: types.CallbackQuery):
    selected_user_tgid = int(callback.data)
    selected_user_name = await get_username_by_tgid(selected_user_tgid)
    
    confirmation_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data=f"confirm:{selected_user_tgid}"),
                InlineKeyboardButton(text="Нет", callback_data="cancel")
            ]
        ]
    )

    # Подтверждение на выбор клиента
    await callback.message.answer(f"Вы хотите выбрать клиента: <b>{selected_user_name}</b>?", reply_markup=confirmation_keyboard, parse_mode="html")
    
# Функция для обработки подтверждения выбора клиента
async def handle_confirmation(callback: types.CallbackQuery):
    if ":" in callback.data:
        action, selected_user_tgid = callback.data.split(":")
        selected_user_tgid = int(selected_user_tgid)
    else:
        action = callback.data
        selected_user_tgid = None

    if action == "confirm":
        if selected_user_tgid is not None:
            selected_user_name = await get_username_by_tgid(selected_user_tgid)
            # Отправляем сообщение о выборе клиента
            await callback.message.answer(
                f"🥳Отлично!\nВы выбрали клиента: <b>{selected_user_name}</b>👩‍🦳\n\n⌚️Теперь введите дату и время записи.\nФормат даты: DD.MM.YYYY HH:MM",
                parse_mode="html")
            # Удаляем сообщение с выбором клиента и подтверждением
            await callback.message.delete()
            
    elif action == "cancel":
        # Удаляем только сообщение с подтверждением
        await callback.answer("Выбор клиента отменен.", show_alert=True)
        await callback.message.delete()
        
    await callback.message.delete()


# Функция для регистрации хэндлеров
def reg_handlers(dp: Dispatcher):
    # Команды
    dp.message.register(cmd_start, Command(commands=["start"]))
    dp.message.register(cmd_help, Command(commands=["help"]))
    dp.message.register(cmd_desc, Command(commands=["desc"]))
    dp.message.register(cmd_serv, Command(commands=["services"]))

    # Регистрация и профиль
    dp.message.register(cmd_reg, F.text == "Зарегистрироваться")
    dp.message.register(register_name, RegisterState.regName)
    dp.message.register(register_phone, RegisterState.regPhone)
    dp.message.register(get_profile, F.text == "Профиль")
    dp.callback_query.register(exit_profile, F.data == 'exit')

    # Кнопки админ панели
    dp.message.register(get_clients, F.text == "Клиенты")
    dp.message.register(set_order, F.text == "Записать")
    dp.callback_query.register(handle_client_selection, lambda c: c.data.isdigit())
    dp.callback_query.register(handle_confirmation, lambda c: c.data.startswith(("confirm:", "cancel")))

    