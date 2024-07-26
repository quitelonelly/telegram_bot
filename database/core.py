from sqlalchemy import insert, select, delete, func
import pytz
from datetime import datetime, timedelta
import asyncio
from aiogram import Bot
from database.db import sync_engine
from database.models import metadata_obj, users_table, orders_table
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))

# Функция создания таблиц
def create_tables():
    metadata_obj.create_all(sync_engine)
    
# Добавление пользователя в бд
def insert_user(name, phone, tgid):
    # Проверяем, существует ли пользователь с таким телефоном
    if check_user(phone):
        return f"Пользователь с номером {phone} уже существует!"
    
    with sync_engine.connect() as conn:
        # Если пользователь не найден, добавляем новые данные
        stmt = insert(users_table).values(
            [
                {"username": name, "userphone": phone, "usertgid": tgid}
            ]
        )
        conn.execute(stmt)
        conn.commit()
        
        return f"☺️ Приятно познакомиться {name}!\n\nПривязанный телефон: {phone}"
        
# Функция проверки, есть ли пользователь с номером телефона
def check_user(phone):
    with sync_engine.connect() as conn:
        stmt = select(users_table).where(users_table.c.userphone == phone)
        result = conn.execute(stmt).fetchone()
        
        if result:
            return True
        else:
            return False
        
def check_order(time):
    with sync_engine.connect() as conn:
        stmt = select(orders_table).where(orders_table.c.client_time == time)
        result = conn.execute(stmt).fetchone()
        
        if result:
            return True
        else: 
            return False

# Функция возвращает логин и пароль пользователя 
def select_user_profile(tgid):
    with sync_engine.connect() as conn:
        stmt = select(users_table).where(users_table.c.usertgid == tgid)
        result = conn.execute(stmt).fetchone()
        
        if result:
            return f"Ваш профиль:\n\n👤Логин: {result[1]}\n📞Телефон: {result[2]}"
        else: 
            return f"Вы еще не зарегистрировались!"

# Функция удаляет пользователя
def delete_user(tgid):
    with sync_engine.connect() as conn:
        # Сначала получаем данные пользователя
        stmt = select(users_table).where(users_table.c.usertgid == tgid)
        result = conn.execute(stmt).fetchone()
        
        if result:
            # Если пользователь найден, удаляем его
            delete_stmt = delete(users_table).where(users_table.c.usertgid == tgid)
            conn.execute(delete_stmt)
            conn.commit()
            
            return f"Ваш профиль был успешно удален:\n\n👤Логин: {result[1]}\n📞Телефон: {result[2]}"
        else: 
            return f"Вашего профиля не существует."

# Функция возвращает список клиентов для админ панели
def select_users():
    with sync_engine.connect() as conn:
        # Получим всех юзеров из БД
        stmt = select(users_table)
        result = conn.execute(stmt).fetchall()
        
        # Создадим список для извлечение всех пользователей
        users_list = ""
        for row in result:
            user = f"👤Имя: <b>{row[1]}</b>\n📞Телефон: <b>{row[2]}</b>\n\n"
            users_list += user
        return f"📝Вот список ваших клиентов:\n\n{users_list}"
    
# Функция возвращает список пользователей для инлайн клавиатуры
def select_users_order():
    with sync_engine.connect() as conn:
        stmt = select(users_table).order_by(users_table.c.username)
        result = conn.execute(stmt).fetchall()
        
        users_list = []
        for row in result:
            user = {
                "username": row[1],
                "userphone": row[2],
                "usertgid": row[3]
            }
            users_list.append(user)
        
        return users_list

# Создадим инлайн клавиатуру со всеми пользователями
def create_kb(user_list):
    inline_keyboard = []

    row = []
    for user in user_list:
        button = InlineKeyboardButton(text=user['username'], callback_data=str(user['usertgid']))
        row.append(button)
        
        if len(row) == 2:
            inline_keyboard.append(row)
            row = []
    if row:
        inline_keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

# Поиск пользователя по tgid
async def get_username_by_tgid(tgid: int) -> str:
    with sync_engine.connect() as conn:
        stmt = select(users_table).where(users_table.c.usertgid == tgid)
        result = conn.execute(stmt).fetchone()
        if result:
            return result[1]
        else:
            return "Неизвестный пользователь"  
        
async def get_userphone_by_tgid(tgid: int) -> str:
    with sync_engine.connect() as conn:
        stmt = select(users_table).where(users_table.c.usertgid == tgid)
        result = conn.execute(stmt).fetchone()
        if result:
            return result[2]
        else:
            return "Неизвестный пользователь"  
        
# Московская временная зона
moscow_tz = pytz.timezone('Europe/Moscow')
# Планирование напоминания
async def schedule_reminder(tgid, name, time, order_id):
    try:
        client_time_msk = moscow_tz.localize(datetime.strptime(time, '%d.%m.%Y %H:%M'))
        reminder_time_msk = client_time_msk - timedelta(days=1)
        reminder_time_msk = reminder_time_msk.replace(hour=10, minute=0, second=0, microsecond=0)

        now_msk = datetime.now(moscow_tz)

        if reminder_time_msk < now_msk:
            return

        delay = (reminder_time_msk - now_msk).total_seconds()
        await asyncio.sleep(delay)

        inline_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Подтвердить запись", callback_data=f"confirm_reminder_{order_id}"),
                    InlineKeyboardButton(text="Отменить запись", callback_data=f"cancel_reminder_{order_id}")
                ]
            ]
        )

        await bot.send_message(
            tgid,
            f"Привет, <b>{name}</b>!\n📅 Напоминаем, что у вас назначена процедура на <b>{time}</b>.\n\nНе забудьте прийти вовремя!😊",
            parse_mode="HTML",
            reply_markup=inline_keyboard
        )
    except ValueError as e:
        print(f"Ошибка формата времени: {e}")
    
# Функция добавления записи в БД
async def insert_order(name, phone, tgid, time):
    if check_order(time):
        return "😶Вы уже записали клиента на это время"

    with sync_engine.connect() as conn:
        stmt = insert(orders_table).values(
            client_name=name, 
            client_phone=phone, 
            client_tgid=tgid, 
            client_time=time
        ).returning(orders_table.c.id)
        result = conn.execute(stmt)
        conn.commit()
        order_id = result.fetchone()[0]
        await bot.send_message(tgid, f"Привет, <b>{name}</b>!\n📅 Вы записаны на <b>{time}</b>.\n\nСпасибо за использование нашего сервиса!😊", parse_mode="HTML")
        asyncio.create_task(schedule_reminder(tgid, name, time, order_id))
        return f"🥳Отлично!\n\nВы записали клиента \n<b>👤{name}</b> \nна <b>⏰{time}</b>"

# функция удаляет запись, если она достигла своего времени
def delete_past_orders():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sync_engine.connect() as conn:
        stmt = delete(orders_table).where(
            func.to_timestamp(orders_table.c.client_time, 'DD.MM.YYYY HH24:MI') < func.to_timestamp(current_time, 'YYYY-MM-DD HH24:MI:SS')
        )
        conn.execute(stmt)
        conn.commit()
        
# Просмотр всех записей
def fetch_all_orders():
    with sync_engine.connect() as conn:
        stmt = select(orders_table.c.client_name, orders_table.c.client_phone, orders_table.c.client_time)
        result = conn.execute(stmt).fetchall()
        
        if not result:
            return "😴У вас нет активных записей"

        formatted_results = []
        for row in result:
            formatted_results.append(f"👤Имя: <b>{row[0]}</b>\n📞Телефон: <b>{row[1]}</b>\n⌚️Время: <b>{row[2]}</b>")
        
        return "Для удаления записи напишите\n<b>/delete время</b>\n\n" + "\n\n".join(formatted_results)
    
# Удаление записи по времени
def delete_order_by_time(time):
    with sync_engine.connect() as conn:
        stmt = delete(orders_table).where(orders_table.c.client_time == time)
        result = conn.execute(stmt)
        conn.commit()

        if result.rowcount > 0:
            return f"✅Запись на время <b>{time}</b> была успешно удалена"
        else:
            return f"❌Запись на время {time} не найдена"

# Удаление записи по id       
def delete_order_by_id(order_id):
    with sync_engine.connect() as conn:
        # Приведение order_id к целому числу
        order_id = int(order_id)
        stmt = delete(orders_table).where(orders_table.c.id == order_id)
        result = conn.execute(stmt)
        conn.commit()
        return result.rowcount > 0
    
# Получение информации о записи по id
def get_order_info_by_id(order_id):
    with sync_engine.connect() as conn:
        # Приведение order_id к целому числу
        order_id = int(order_id)
        
        # Получение информации о записи
        select_stmt = select(orders_table.c.client_name, orders_table.c.client_time).where(orders_table.c.id == order_id)
        result = conn.execute(select_stmt).fetchone()
        
        return result
    
# Получение tgid каждого клиента
def get_all_users():
    try:
        with sync_engine.connect() as conn:
            stmt = select(users_table.c.usertgid)  # Получаем только tgid
            results = conn.execute(stmt).fetchall()
            
            # Возвращаем список tgid
            tgid_list = [row[0] for row in results]
            
            return tgid_list
    except Exception as e:
        print(f"Ошибка: {e}")
        return []
    