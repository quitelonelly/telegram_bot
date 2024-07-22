from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

import asyncio
import os

from handlers import reg_handlers
from database.core import create_tables, delete_past_orders

delete_past_orders()

# Настройка планировщика
scheduler = AsyncIOScheduler()

# Планирование функции для выполнения каждую минуту
scheduler.add_job(delete_past_orders, 'interval', minutes=1)

# Запуск планировщика
scheduler.start()

# Загрузка переменного окружения
load_dotenv()

# Получение токена из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Вызываем функцию для создания таблиц
create_tables()

reg_handlers(dp)

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())