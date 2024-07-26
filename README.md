# ServiceHub
  Этот проект представляет собой пример использования библиотеки Aiogram для создания Telegram-бота и библиотеки SQLAlchemy для работы с базой данных. В проекте реализованы базовые функции регистрации пользователей, управления профилем и админ-панели для     просмотра клиентов и записей.

# Содержание
  1) Установка
  2) Использование
  3) Описание структуры

  # Установка
    1) Клонируйте репозиторий
      git clone https://github.com/yourusername/yourproject.git

    2) Перейдите в директорию проекта
      cd yourproject

    3) Создайте и активируйте виртуальное окружение (опционально)
      python3 -m venv venv
      source venv/bin/activate

    4) Установите зависимости
      pip install -r requirements.txt

  # Использование
    1) Запустите файл bot.py, чтобы запустить Telegram-бота
      python bot.py

  # Описание структуры
    Таблицы базы данных 
    Таблица users
    Таблица содержит информацию о пользователях:
      id (Integer): первичный ключ.
      username (String): имя пользователя.
      userphone (String): номер телефона пользователя.
      usertgid (Integer): идентификатор пользователя в Telegram.
      
    Таблица orders
    Таблица содержит информацию о записях:
      id (Integer): первичный ключ.
      client_name (String): имя клиента.
      client_phone (String): номер телефона клиента.
      client_tgid (String): идентификатор клиента в Telegram.
      client_time (String): время записи клиента.

    Основная логика бота (main.py)
    Файл main.py содержит основную логику и настройки для запуска бота.
    Пример настройки и запуска бота:
    API_TOKEN = 'YOUR_API_TOKEN_HERE'

    # Инициализация бота и диспетчера
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot)
    
    # Регистрация обработчиков
    register_handlers(dp)
    
    # Запуск процесса поллинга новых апдейтов
    async def main():
        await dp.start_polling(bot)
    
    if __name__ == "__main__":
        asyncio.run(main())
    
    Логика обработки (handlers.py)
    Файл handlers.py содержит функции для обработки различных команд и сообщений от пользователей.
    Пример функции обработки команды старт:
      from aiogram import types
      from aiogram.dispatcher import Dispatcher
      
      async def start_command(message: types.Message):
          await message.answer("Добро пожаловать! Пожалуйста, зарегистрируйтесь.", reply_markup=kb_reg)
      
      def register_handlers(dp: Dispatcher):
          dp.register_message_handler(start_command, commands=["start"])
