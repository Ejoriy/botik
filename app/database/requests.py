from aiogram.types import CallbackQuery

from app.database.models import async_session
from app.database.models import User
from sqlalchemy import select
from config import botik
from aiogram.exceptions import TelegramAPIError

from config import client
from app.keyboards import checker


# Добавление нового пользователя в базу данных, если он еще не существует
async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id, sub='нет', key='нет', key_id='нет', buy_time=None, end_time=None))
            await session.commit()


# Обновление информации о подписке пользователя
async def update_subscription(tg_id, sub, payment_date, end_date):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.sub = sub
            user.buy_time = payment_date
            user.end_time = end_date
            await session.commit()


# Обновление информации о VPN-ключе пользователя
async def set_user_key(tg_id, key, key_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.key = key
            user.key_id = key_id
            await session.commit()


# Создание нового VPN-ключа через API Outline
async def create_new_key(key_id: str = None, name: str = None):
    key_data = client.create_key(key_id=key_id, name=name)
    return key_data.access_url, key_data.key_id  # Возвращаем оба параметра


async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await botik.get_chat_member('@persecvpn', user_id)
        return member.status in ['member', 'administrator', 'creator']
    except TelegramAPIError:
        return False


async def check_subscription(user_id: int, callback: CallbackQuery) -> bool:
    if not await is_user_subscribed(user_id):
        await callback.message.answer(
            'Для использования бота необходимо подписаться на канал: \n\n После подписки нажмите на /start',
            reply_markup=checker
        )
        await callback.answer()
        return False
    return True


# Удаление ключа по key_id
async def delete_key(key_id: str):
    return client.delete_key(key_id)


status_delete_key = delete_key('')
