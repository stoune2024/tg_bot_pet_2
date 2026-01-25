from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from create_bot import kb_list
from utils.db import get_user_by_id, add_user, update_bot_open_status
from keyboards.kb import channels_kb, main_contact_kb
from utils.utils import is_user_subscribed

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    telegram_id = message.from_user.id
    user_data = await get_user_by_id(telegram_id)

    if user_data is None:
        # Если пользователь не найден, добавляем его в базу данных
        await add_user(
            telegram_id=telegram_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )
        bot_open = False
    else:
        # Получаем статус bot_open для пользователя
        bot_open = user_data.get(
            "bot_open", False
        )  # Второй параметр по умолчанию False

    if bot_open:
        # Если пользователь подписался на все каналы
        await message.answer("Тут основная логика бота, чуть позже напишем")
    else:
        # Иначе показываем клавиатуру с каналами для подписки
        await message.answer(
            "Для пользования ботом необходимо подписаться на следующие каналы:",
            reply_markup=channels_kb(kb_list),
        )


@router.callback_query(F.data == "check_subscription")
async def check_subs_func(call: CallbackQuery):
    await call.answer("Запускаю проверку подписок на каналы")

    for channel in kb_list:
        label = channel.get("label")
        channel_url = channel.get("url")
        telegram_id = call.from_user.id
        check = await is_user_subscribed(channel_url, telegram_id)
        if check is False:
            await call.message.answer(
                f"❌ вы не подписались на канал 👉 {label}",
                reply_markup=channels_kb(kb_list),
            )
            return False

    await update_bot_open_status(telegram_id=call.from_user.id, bot_open=True)
    await call.message.answer(
        "Спасибо за подписки на все каналы! Теперь можете воспользоваться функционалом бота",
        reply_markup=main_contact_kb(call.from_user.id),
    )


@router.message(F.text == "🆔 MY INFO")
async def handle_my_id(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or "Не указано"
    username = message.from_user.username or "Не указано"

    await message.answer(
        f"🔍 Ваши данные:\n\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"👤 Имя: {first_name} {last_name}\n"
        f"🔗 Username: @{username}"
    )


@router.message(F.user_shared)
async def handle_user(message: Message):
    user_id = message.user_shared.user_id
    request_id = message.user_shared.request_id

    if request_id == 1:
        await message.answer(f"👤 Вы выбрали пользователя с ID: <code>{user_id}</code>")
    elif request_id == 4:
        await message.answer(f"🤖 Вы выбрали бота с ID: <code>{user_id}</code>")


@router.message(F.chat_shared)
async def handle_chat_or_channel(message: Message):
    chat_id = message.chat_shared.chat_id
    request_id = message.chat_shared.request_id

    if request_id == 2:
        await message.answer(f"👥 Вы выбрали группу с ID: <code>{chat_id}</code>")
    elif request_id == 3:
        await message.answer(f"📢 Вы выбрали канал с ID: <code>{chat_id}</code>")
