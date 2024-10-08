# Импорт необходимых библиотек
from aiogram import types
from aiogram import Dispatcher, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from database.config import settings

from dotenv import load_dotenv
import os

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))

import re

# Импортируем клавиатуру
from kb_bot import kb_reg, kb_profile, kb_delete_profile, kb_admin
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Импорт состояния
from state.register import RegisterState
from state.order import OrderState
from state.admin import AdminStates

# Импорт функций для работы с БД
from database.core import (
    insert_user, select_user_profile, delete_user, select_users, 
    create_kb, select_users_order, get_username_by_tgid, 
    get_userphone_by_tgid, insert_order, fetch_all_orders,
    delete_order_by_time, delete_order_by_id, get_order_info_by_id,
    get_all_users
    )

# Обработчик команды /start
async def cmd_start(message: types.Message):
    user_id = message.from_user.id

    admin_ids = settings.admin_ids
    if user_id in admin_ids:
        await message.answer(f"🤩Приветствую, <b>{message.from_user.full_name}</b>!\nЯ заметил, что вы являетесь администратором!🤩\n\nВам доступен особый список команд.", reply_markup=kb_admin, parse_mode="HTML")
    else:
        await message.answer(f"🤩Приветствую, <b>{message.from_user.full_name}</b>!\nДля начала взаимодействия со мной отправьте мне команду!🤩", reply_markup=kb_reg, parse_mode="HTML")

# Обработчик команды /help
async def cmd_help(message: types.Message):
    await message.answer("Вам нужна помощь?😲 По всем вопросам вы можете обращаться сюда\n\nhttps://t.me/AnastasiyaG_1983 📱")

# Обработчик команды /desc
async def cmd_desc(message: types.Message):
    await message.answer(
        "Я бот для записи клиентов на различные процедуры. 💅\n\n"
            "С моей помощью вы можете:\n\n"
            "🔹 Узнать о доступных процедурах\n"
            "🔹 Вас запишут на удобное для вас время\n"
            "🔹 Получить напоминание о предстоящей записи\n\n"
            "Если у вас есть вопросы, просто напишите мне!"
    )
    
# Обработчик команды /services
async def cmd_serv(message: types.Message):
    await message.answer(
        "📋Список предоставляемых услуг\n\n"
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

# Фукнция проверяет есть ли пользователь в БД и выдает ему профиль
async def get_profile(message: types.Message):
    tgid = message.from_user.id

    # Получаем данные пользователя из бд
    result = select_user_profile(tgid)
    if result == "Вы еще не зарегистрировались!":
        await message.answer(result)
    else:
        await message.answer(result, reply_markup=kb_delete_profile)
        await message.answer("✅Отлично!\n\nВам осталось лишь ожидать сообщения от меня!")
    
# Функция удаляет профиль пользователя
async def exit_profile(call: types.CallbackQuery):
    # Удаление профиля
    tgid = call.from_user.id

    # Получаем данные пользователя из бд
    result = delete_user(tgid)

    # Удаляем предыдущее сообщение
    await call.message.delete()

    # Отправляем новое сообщение
    await call.message.answer("Профиль удален", reply_markup=kb_reg)
    await call.answer(result, show_alert=True)
    
# Админ панель
# Кнопки админ панели
async def get_clients(message: types.Message):
    result = select_users()
    
    await message.answer(result, parse_mode="html")
    
# Обработка кнопки "Записать"
async def set_order(message: types.Message, state: FSMContext):
    users = select_users_order()
    keyboard = create_kb(users)
    
    await message.answer("Давайте запишем клиента на процедуру! Выберите клиента из клавиатуры.", reply_markup=keyboard)
    await state.set_state(OrderState.ordName)

# Сообщение с подтверждением выбранного клиента
async def handle_client_selection(callback: types.CallbackQuery, state: FSMContext):
    selected_user_tgid = int(callback.data)
    selected_user_name = await get_username_by_tgid(selected_user_tgid)
    
    await state.update_data(selected_user_tgid=selected_user_tgid)
    
    confirmation_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data="confirm"),
                InlineKeyboardButton(text="Нет", callback_data="cancel")
            ]
        ]
    )

    # Подтверждение на выбор клиента
    await callback.message.answer(f"Вы хотите выбрать клиента: <b>{selected_user_name}</b>?", reply_markup=confirmation_keyboard, parse_mode="html")

# Функция для обработки подтверждения выбора клиента
async def handle_confirmation(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data

    if action == "confirm":
        state_data = await state.get_data()
        selected_user_tgid = state_data.get("selected_user_tgid")
        selected_user_name = await get_username_by_tgid(selected_user_tgid)

        # Отправляем сообщение о выборе клиента
        await callback.message.answer(
            f"🥳Отлично!\nВы выбрали клиента: <b>{selected_user_name}</b>👤\n\n⌚️Теперь введите дату и время записи.\nФормат даты: DD.MM.YYYY HH:MM",
            parse_mode="html")
        await state.set_state(OrderState.ordTime)

    elif action == "cancel":
        # Удаляем только сообщение с подтверждением
        await callback.answer("Выбор клиента отменен.", show_alert=True)

    await callback.message.delete()

# Функция записывает клиента на процедуру
async def register_order_time(message: types.Message, state: FSMContext):
    order_time = message.text
    date_time_pattern = r"^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$"

    if re.findall(date_time_pattern, order_time):
        state_data = await state.get_data()
        selected_user_tgid = state_data.get("selected_user_tgid")
        selected_user_name = await get_username_by_tgid(selected_user_tgid)
        
        # Получение номера телефона пользователя по TGID
        user_phone = await get_userphone_by_tgid(selected_user_tgid)

        # Вставка заказа в базу данных
        result = await insert_order(selected_user_name, user_phone, selected_user_tgid, order_time)

        await message.answer(result, parse_mode="HTML")
        await state.clear()
    else:
        await message.answer("😡Дата и время указаны в неправильном формате!\n\nПожалуйста, введите в формате <b>DD.MM.YYYY HH:MM</b>", parse_mode="HTML")
    
# Фукнция извлечения заказов 
async def get_orders(message: types.Message):
    # Извлекаем все заказы из базы данных
    orders = fetch_all_orders()
    
    # Если заказы найдены, выводим их
    if orders:
        await message.answer(orders, parse_mode="html")
    else:
        await message.answer("Записей не найдено")
    
# Команда удаляет запись 
async def cmd_delete(message: types.Message, command: CommandObject):
    if message.from_user.id in settings.admin_ids:
        time = command.args.strip()
        if time:
            result = delete_order_by_time(time)
            await message.answer(result, parse_mode="HTML")
        else:
            await message.answer("Пожалуйста, укажите время для удаления записи. \n\nПример: /delete 01.01.2024 12:00")
    else:
        await message.answer("❌У вас нет прав для выполнения этой команды.")
        
async def handle_confirm_reminder(callback: types.CallbackQuery):
    try:
        data = callback.data.split('_')
        
        if len(data) == 3 and data[0] == "confirm" and data[1] == "reminder":
            order_id = data[2]
            
            order_info = get_order_info_by_id(order_id)
            if order_info:
                client_name, order_time = order_info
                await callback.message.answer("✅ Запись подтверждена!")
                
                # Уведомление администраторов
                await notify_admins_about_confirmation(client_name, order_time)
            else:
                await callback.message.answer("❌ Запись не найдена!")
        else:
            await callback.message.answer("❌ Некорректные данные для подтверждения записи.")
    except Exception as e:
        await callback.message.answer("❌ Произошла ошибка при обработке запроса.")
    finally:
        # Удаление сообщения с кнопками
        await callback.message.delete()
        await callback.answer()

async def handle_cancel_reminder(callback: types.CallbackQuery):
    try:
        data = callback.data.split('_')

        if len(data) == 3 and data[0] == "cancel" and data[1] == "reminder":
            order_id = data[2]
            
            order_info = get_order_info_by_id(order_id)
            if order_info:
                client_name, order_time = order_info
                if delete_order_by_id(order_id):
                    await callback.message.answer("❌ Запись отменена!")
                    await notify_admins_about_cancellation(client_name, order_time)
                else:
                    await callback.message.answer("❌ Запись не найдена!")
            else:
                await callback.message.answer("❌ Запись не найдена!")
        else:
            await callback.message.answer("❌ Некорректные данные для отмены записи.")
    except Exception as e:
        await callback.message.answer("❌ Произошла ошибка при обработке запроса.")
    finally:
        # Удаление сообщения с кнопками
        await callback.message.delete()
        await callback.answer()
        
# Отправка уведомления администраторам об отмене записи
async def notify_admins_about_cancellation(client_name, order_time):
    admin_ids = settings.admin_ids
    message = f"👤Клиент <b>{client_name}</b>\nотменил запись на <b>{order_time}</b>"
    for admin_id in admin_ids:
        await bot.send_message(admin_id, message, parse_mode="HTML")
        
# Отправка уведомления администраторам о подтверждении записи   
async def notify_admins_about_confirmation(client_name, order_time):
    admin_ids = settings.admin_ids
    message = f"👤Клиент <b>{client_name}</b>\nподтвердил запись на <b>{order_time}</b>"
    for admin_id in admin_ids:
        await bot.send_message(admin_id, message, parse_mode="HTML")
        
# Отправка сообщения всем клиентам
async def send_message_prompt(message: types.Message, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_message)
    await message.answer("✉️ Для отправки напишите сообщение\nОно отправится всем пользователям✅")

async def process_admin_message(message: types.Message, state: FSMContext):
    admin_message = message.text
    
    # Получите список всех пользователей из вашей базы данных
    users = get_all_users()
    
    # Рассылка сообщения всем пользователям
    for user_id in users:
        try:
            await bot.send_message(user_id, f"👁Сообщение от администратора\n\n{admin_message}")
        except Exception as e:
            await message.answer(f"Не удалось отправить сообщение пользователю {user_id}")
    
    # Подтверждение администратору
    await message.answer("✅Сообщение успешно отправлено всем пользователям.")
    
    # Завершите состояние
    await state.finish()
        

# Функция для регистрации хэндлеров
def reg_handlers(dp: Dispatcher):
    # Команды
    dp.message.register(cmd_start, Command(commands=["start"]))
    dp.message.register(cmd_help, Command(commands=["help"]))
    dp.message.register(cmd_desc, Command(commands=["desc"]))
    dp.message.register(cmd_serv, Command(commands=["services"]))
    dp.message.register(cmd_delete, Command(commands=["delete"]))

    # Регистрация и профиль
    dp.message.register(cmd_reg, F.text == "Зарегистрироваться")
    dp.message.register(register_name, RegisterState.regName)
    dp.message.register(register_phone, RegisterState.regPhone)
    dp.message.register(get_profile, F.text == "Профиль")
    dp.callback_query.register(exit_profile, F.data == 'exit')

    # Кнопки админ панели
    dp.message.register(get_clients, F.text == "Просмотреть клиентов")
    dp.message.register(set_order, F.text == "Записать клиента")
    dp.message.register(get_orders, F.text == "Просмотреть записи")
    dp.message.register(send_message_prompt, F.text == "Отправить сообщение")
    dp.message.register(process_admin_message, AdminStates.waiting_for_message)
    
    # Запись клиентов(подтверждение выбора)
    dp.callback_query.register(handle_client_selection, lambda c: c.data.isdigit())
    dp.callback_query.register(handle_confirmation, lambda c: c.data in ["confirm", "cancel"])
    dp.message.register(register_order_time, OrderState.ordTime)
    
    # Хэндлеров напоминания
    dp.callback_query.register(handle_confirm_reminder, lambda c: c.data.startswith("confirm_reminder_"))
    dp.callback_query.register(handle_cancel_reminder, lambda c: c.data.startswith("cancel_reminder_"))
    

    