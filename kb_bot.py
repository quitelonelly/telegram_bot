from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# Клавиатура профиля
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Зарегистрироваться'),
         KeyboardButton(text='Профиль')],
    ],
    resize_keyboard=True
)

# Инлайн клавиатура профиля
kb_profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Выйти', callback_data='exit')]
    ]
)

# Админ клавиатура
kb_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Клиенты'),
         KeyboardButton(text='Записать')]
    ],
    resize_keyboard=True
)