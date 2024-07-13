from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# Основная клавиатура
kb_reg = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Зарегистрироваться')]
    ],
    resize_keyboard=True
)
    
# Клавиатура после регистрации
kb_profile = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Профиль')]
    ],
    resize_keyboard=True
)

# Инлайн клавиатура профиля
kb_delete_profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Удалить профиль', callback_data='exit')]
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
