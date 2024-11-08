from sqlalchemy import DateTime
from sqlalchemy import BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from decouple import config

# Получаем строку подключения из конфигурации
SQLALCHEMY_URL = config('SQLALCHEMY_URL')
engine = create_async_engine(SQLALCHEMY_URL)

# Создание асинхронной сессии
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    sub: Mapped[str] = mapped_column()
    key: Mapped[str] = mapped_column()
    key_id: Mapped[str] = mapped_column()
    buy_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True)


# Функция для создания таблиц в бд
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
