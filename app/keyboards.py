from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👨‍💼 Личный кабинет', callback_data='lk'),
     InlineKeyboardButton(text='🛒 Купить', callback_data='buy')],
    [InlineKeyboardButton(text='📔 Инструкция', callback_data='instruction'),
     InlineKeyboardButton(text='🔧 Поддержка', callback_data='support')]
])

helper = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Наш ТГ канал', url='https://t.me/persecvpn')]
])

back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='←  Назад к меню', callback_data='go_back')]
])

forpay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='На месяц (30 дней)', callback_data='monthly'),
     InlineKeyboardButton(text='На год (пока недоступно)', callback_data='annual')],
    [InlineKeyboardButton(text='←  Назад к меню', callback_data='go_back')]
])

checker = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подписаться на канал', url='https://t.me/persecvpn')]
])
