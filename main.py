import asyncio
import json
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest

from config import BOT_TOKEN, ADMIN_IDS, CHANNEL_USERNAME, OWNER_USERNAME

USERS_FILE = "users.json"


class BroadcastState(StatesGroup):
    waiting_for_text = State()


def load_users() -> list[int]:
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return [int(x) for x in data]
        except Exception:
            return []


def save_user(user_id: int) -> None:
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def check_sub(bot: Bot, user_id: int) -> bool:
    if not CHANNEL_USERNAME:
        return True
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ("creator", "administrator", "member")
    except TelegramBadRequest:
        return False
    except Exception:
        return False


def sub_keyboard() -> InlineKeyboardMarkup:
    clean_channel = CHANNEL_USERNAME.lstrip("@")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Kanalga a'zo bo'lish",
                    url=f"https://t.me/{clean_channel}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Tekshirish",
                    callback_data="check_subscription",
                )
            ],
        ]
    )


def main_menu(user_id: int) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="🎬 Kinolar / Bo'limlar"), KeyboardButton(text="👑 Owner")],
    ]
    if is_admin(user_id):
        rows.append([KeyboardButton(text="🛠 Admin panel")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📣 Xabar yuborish (Broadcast)", callback_data="admin_broadcast")],
        ]
    )


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    save_user(user_id)

    if not await check_sub(bot, user_id):
        await message.answer(
            f"Botdan foydalanish uchun avval {CHANNEL_USERNAME} kanaliga a'zo bo'ling!",
            reply_markup=sub_keyboard(),
        )
        return

    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}!\n"
        f"Botga xush kelibsiz.\n\n"
        f"Kanal: {CHANNEL_USERNAME}\n"
        f"Owner: {OWNER_USERNAME}",
        reply_markup=main_menu(user_id),
    )


@dp.callback_query(F.data == "check_subscription")
async def cb_check_sub(callback: CallbackQuery):
    user_id = callback.from_user.id
    save_user(user_id)

    if await check_sub(bot, user_id):
        await callback.message.delete()
        await callback.message.answer(
            "✅ Obuna tasdiqlandi! Endi menyudan foydalanishingiz mumkin.",
            reply_markup=main_menu(user_id),
        )
    else:
        await callback.answer(
            f"❌ Hali {CHANNEL_USERNAME} kanaliga a'zo emassiz!",
            show_alert=True,
        )


@dp.message(F.text == "👑 Owner")
async def btn_owner(message: Message):
    save_user(message.from_user.id)
    await message.answer(
        f"👑 Loyiha egasi (Owner): {OWNER_USERNAME}\n"
        f"📢 Rasmiy kanal: {CHANNEL_USERNAME}"
    )


@dp.message(F.text == "🎬 Kinolar / Bo'limlar")
async def btn_catalog(message: Message):
    user_id = message.from_user.id
    save_user(user_id)
    if not await check_sub(bot, user_id):
        await message.answer(
            f"Avval {CHANNEL_USERNAME} kanaliga obuna bo'ling!",
            reply_markup=sub_keyboard(),
        )
        return

    await message.answer(
        f"🎬 Yangi kinolar va yangiliklar {CHANNEL_USERNAME} kanalida e'lon qilinadi.\n"
        f"Savollar bo'yicha murojaat: {OWNER_USERNAME}"
    )


@dp.message(Command("admin"))
@dp.message(F.text == "🛠 Admin panel")
async def open_admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Siz admin emassiz.")
        return
    await message.answer("🛠 Admin boshqaruv paneli:", reply_markup=admin_panel_keyboard())


@dp.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    users = load_users()
    await callback.message.answer(f"📊 Jami foydalanuvchilar soni: <b>{len(users)}</b> ta", parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await state.set_state(BroadcastState.waiting_for_text)
    await callback.message.answer("📣 Barcha foydalanuvchilarga yuboriladigan xabar matnini yozing:")
    await callback.answer()


@dp.message(BroadcastState.waiting_for_text)
async def process_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    users = load_users()
    sent = 0
    failed = 0

    for uid in users:
        try:
            await bot.send_message(chat_id=uid, text=message.text)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    await state.clear()
    await message.answer(
        f"✅ Xabar yuborish yakunlandi:\n"
        f"• Yuborildi: {sent}\n"
        f"• Yuborilmadi (bloklagan/topilmadi): {failed}"
    )


async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
