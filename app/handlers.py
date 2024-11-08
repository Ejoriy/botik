from aiogram import F, Router, Bot
from aiogram.enums import ContentType
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.exceptions import TelegramAPIError

import app.keyboards as kb
import app.database.requests as rq
import app.database.models as mods
from app.database.models import async_session
from app.database.requests import create_new_key
from decouple import config
from datetime import datetime, timedelta
from sqlalchemy import select
from config import botik

router = Router()


# Обработка команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    channel_link = '@persecvpn'  # Ваш канал

    try:
        # Проверяем, подписан ли пользователь на канал
        member = await botik.get_chat_member(channel_link, user_id)

        if member.status in ['member', 'administrator', 'creator']:
            # Пользователь подписан, показываем информацию
            await rq.set_user(user_id)
            await message.answer(
                'Привет 👋🏻\n\nЗдесь ты можешь легко и быстро получить доступ к высокоскоростному VPN-соединению, '
                'которое обеспечит безопасность и свободу в интернете. Выбери подходящий тариф, следуй подсказкам бота и получи '
                'свой личный VPN-ключ.',
                reply_markup=kb.main
            )
        else:
            # Пользователь не подписан на канал
            await message.answer(
                'Для использования бота необходимо подписаться на канал: \n\n После подписки нажмите на /start',
                reply_markup=kb.checker
            )
    except TelegramAPIError as e:
        # Ошибка с API Telegram (например, канал не найден или бот заблокирован)
        await message.answer(
            f'Произошла ошибка API: {str(e)}\n\nВозможно вы заблокировали бота, разблокируйте и повторите попытку')
    except Exception as e:
        # Другие ошибки
        await message.answer(f'Произошла ошибка: {str(e)}')


# Обработка команды /help
@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Вот список команд для взаимодействия:\n/help - помощь\n/start - начать',
                         reply_markup=kb.helper)


# Показ информации о личном кабинете
@router.callback_query(F.data == 'lk')
async def lk(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.full_name

    if not await rq.check_subscription(user_id, callback):
        return

    async with async_session() as session:
        result = await session.scalar(select(mods.User.sub).where(mods.User.tg_id == user_id))
        end_sub = await session.scalar(select(mods.User.end_time).where(mods.User.tg_id == user_id))

    end_sub_str = end_sub.strftime("%d\\.%m\\.%Y %H:%M") if end_sub else "Не указано"

    await callback.answer()
    await callback.message.edit_text(
        f'Привет, {username}\n\nID: {user_id}\n\n*Активная подписка:* {result}\n\n*Дата окончания подписки:* {end_sub_str}',
        parse_mode="MarkdownV2",
        reply_markup=kb.back
    )


# Покупка VPN
@router.callback_query(F.data == 'buy')
async def buy(callback: CallbackQuery):
    user_id = callback.from_user.id

    if not await rq.check_subscription(user_id, callback):
        return

    await callback.answer()
    await callback.message.edit_text('Выберите товар для покупки:', reply_markup=kb.forpay)


# Инструкция по подключению к VPN
@router.callback_query(F.data == 'instruction')
async def instruction(callback: CallbackQuery):
    user_id = callback.from_user.id

    if not await rq.check_subscription(user_id, callback):
        return

    await callback.answer()
    await callback.message.edit_text(
        '*Чтобы подключиться к серверу выполните 3 простых шага:*\n\n1️⃣ _Скачай приложение:_'
        '\n\n[Android](https://play.google.com/store/apps/details?id=org.outline.android.client)'
        '\n\n[IOS](https://apps.apple.com/ru/app/outline-app/id1356177741)\n\n2️⃣ _Скопируй выданный после покупки ключ_\n\n'
        '3️⃣ _Зайди в приложение:_\n\nвставь скопированный ключ в появившееся поле ввода, после чего нажми _"Добавить сервер"_ '
        'и разреши приложению добавить конфигурацию\n\n"Если вдруг поле для ввода ключа не появится, нажми на ✚ в правом '
        'верхнем углу"\n\n\n*Поздравляю 🥳, все готово*\\!',
        reply_markup=kb.back,
        parse_mode="MarkdownV2",
        disable_web_page_preview=True
    )


@router.callback_query(F.data == 'go_back')
async def back_to_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        'Привет 👋🏻\n\nЗдесь ты можешь легко и быстро получить доступ к высокоскоростному VPN-соединению, '
        'которое обеспечит безопасность и свободу в интернете. Выбери подходящий тариф, следуй подсказкам бота и получи свой личный VPN-ключ.',
        reply_markup=kb.main
    )


# Обработка поддержки
@router.callback_query(F.data == 'support')
async def support(callback: CallbackQuery):
    user_id = callback.from_user.id

    if not await rq.check_subscription(user_id, callback):
        return

    await callback.answer()
    await callback.message.edit_text(
        'Если у вас возникли вопросы в процессе использования сервиса, вы можете задать их нам:\n\n@ejoriy\n@Jnbehdb',
        reply_markup=kb.back
    )


# Обработка покупки подписки на месяц
@router.callback_query(F.data == 'monthly')
async def process_monthly_payment(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id

    if not await rq.check_subscription(user_id, callback):
        return

    await callback.answer()
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Подписка на месяц",
        description="Оплата подписки на месяц 150 рублей",
        payload="monthly_subscription",
        provider_token=config('PAYMENT_TOKEN'),
        currency="RUB",
        prices=[LabeledPrice(label="Подписка на месяц", amount=150 * 100)],  # 150 рублей в копейках
        start_parameter="monthly_subscription",
    )


# Проверка перед оплатой
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# Обработка успешной оплаты
@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: Message):
    await message.answer('✅ Операция прошла успешно ✅\nВаша подписка на месяц активирована.')

    # Генерация VPN-ключа
    access_url, key_id = await create_new_key()

    # Дата начала и окончания подписки
    payment_date = datetime.now()
    end_date = payment_date + timedelta(minutes=2)

    # Обновление подписки и ключа
    await rq.update_subscription(message.from_user.id, "Месяц", payment_date, end_date)
    await rq.set_user_key(message.from_user.id, access_url, key_id)

    await message.answer(access_url)
    await message.answer(
        '🔑 `Это ваш VPN-ключ` 🔑\n\nДля корректного подключения вернитесь в главное меню и откройте раздел "📔 Инструкция"',
        parse_mode='MarkdownV2',
        reply_markup=kb.back
    )


# введем когда раскрутимся

@router.callback_query(F.data == 'annual')
async def support(callback: CallbackQuery):
    await callback.answer()
