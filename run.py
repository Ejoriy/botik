import asyncio
import logging
from aiogram import Dispatcher
from app.handlers import router
from app.database.models import async_main
from app.database.requests import delete_key
from app.database.models import async_session, User
from sqlalchemy import select
from config import botik  # Импортируем bot из config.py

from datetime import datetime


# Функция для проверки истекших подписок и удаления ключей
async def check_and_delete_expired_keys():
    while True:
        # Текущая дата и время
        current_time = datetime.now()

        async with async_session() as session:
            # Получаем всех пользователей с истекшей подпиской
            result = await session.execute(
                select(User).where(User.end_time <= current_time)
            )
            expired_users = result.scalars().all()

            for user in expired_users:
                # Удаляем ключ из Outline Manager
                status_delete_key = await delete_key(user.key_id)
                print(f"Удаление ключа для пользователя {user.tg_id}: {status_delete_key}")

                # Обновляем поля пользователя через ORM
                user.sub = 'нет'
                user.key = 'нет'
                user.key_id = 'нет'
                user.buy_time = None
                user.end_time = None

            # Сохраняем все изменения в базе данных одной транзакцией
            await session.commit()

        # Пауза перед следующей проверкой
        await asyncio.sleep(60)  # 3600 секунд = 1 час


async def main():
    await async_main()
    dp = Dispatcher()
    dp.include_router(router)

    # Запускаем функцию для проверки подписок параллельно с ботом
    asyncio.create_task(check_and_delete_expired_keys())

    await dp.start_polling(botik)  # Используем bot из config.py


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот отключен')
