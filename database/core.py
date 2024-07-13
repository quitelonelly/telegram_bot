from sqlalchemy import text, insert, select, delete
from database.db import sync_engine
from database.models import metadata_obj, users_table
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_tables():
    metadata_obj.create_all(sync_engine)
    
def insert_data(name, phone, tgid):
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
        
def check_user(phone):
    with sync_engine.connect() as conn:
        stmt = select(users_table).where(users_table.c.userphone == phone)
        result = conn.execute(stmt).fetchone()
        
        if result:
            return True
        else:
            return False
        
def select_user_profile(tgid):
    with sync_engine.connect() as conn:
        stmt = select(users_table).where(users_table.c.usertgid == tgid)
        result = conn.execute(stmt).fetchone()
        
        if result:
            return f"Ваш профиль:\n\n👩‍🦳Логин: {result[1]}\n📞Телефон: {result[2]}"
        else: 
            return f"Вы еще не зарегистрировались!"
        
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
            
            return f"Ваш профиль был успешно удален:\n\n👩‍🦳Логин: {result[1]}\n📞Телефон: {result[2]}"
        else: 
            return f"Вашего профиля не существует."
        
def select_users():
    with sync_engine.connect() as conn:
        # Получим всех юзеров из БД
        stmt = select(users_table)
        result = conn.execute(stmt).fetchall()
        
        # Создадим список для извлечение всех пользователей
        users_list = ""
        for row in result:
            user = f"Имя: {row[1]}\nТелефон: {row[2]}\n\n"
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

async def get_username_by_tgid(tgid: int) -> str:
    with sync_engine.connect() as conn:
        stmt = select(users_table).where(users_table.c.usertgid == tgid)
        result = conn.execute(stmt).fetchone()
        if result:
            return result[1]
        else:
            return "Неизвестный пользователь"  
