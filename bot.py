import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import ADMIN_PASSWORD, BOT_TOKEN, CHANNELS, MAX_ATTEMPTS
from database import Database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class AdminLogin(StatesGroup):
    waiting_password = State()


class AdminPanel(StatesGroup):
    idle = State()
    upload_name = State()
    upload_file = State()
    broadcast_message = State()


router = Router()
db = Database("gamebot.db")


async def safe_edit_text(message: Message, text: str, **kwargs) -> None:
    try:
        await message.edit_text(text, **kwargs)
    except TelegramBadRequest as e:
        err = (getattr(e, "message", None) or str(e) or "").lower()
        if "not modified" not in err:
            raise


def subscription_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for channel in CHANNELS:
        if channel["type"] == "telegram":
            buttons.append([InlineKeyboardButton(text="📢 Telegram Kanal", url=channel["url"])])
        elif channel["type"] == "instagram":
            buttons.append([InlineKeyboardButton(text="📸 Instagram", url=channel["url"])])
    buttons.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def games_keyboard(games: list) -> InlineKeyboardMarkup:
    buttons = []
    for game in games:
        buttons.append(
            [InlineKeyboardButton(text=f"🎮 {game['name']}", callback_data=f"game_{game['id']}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📁 Fayl qo'shish", callback_data="admin_upload")],
            [InlineKeyboardButton(text="📨 Xabar yuborish", callback_data="admin_broadcast")],
            [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton(text="🗑 Fayl o'chirish", callback_data="admin_delete")],
            [InlineKeyboardButton(text="🚪 Chiqish", callback_data="admin_logout")],
        ]
    )


def admin_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Admin panelga", callback_data="admin_back")],
        ]
    )


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    tg_channel = CHANNELS[0]["id"]
    try:
        member = await bot.get_chat_member(tg_channel, user_id)
        return member.status not in ("left", "kicked", "banned")
    except Exception:
        return False


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    db.add_user(user.id, user.username or "", user.full_name)
    subscription_status = db.get_subscription(user.id)

    if subscription_status is None:
        await message.answer(
            f"👋 <b>Salom, {user.first_name}!</b>\n\n"
            "🎮 <b>GameHub Bot</b>ga xush kelibsiz!\n"
            "Bu yerda siz mashhur o'yinlarni <b>bepul</b> yuklab olishingiz mumkin.\n\n"
            "📌 Davom etish uchun quyidagi kanallarga obuna bo'ling:",
            parse_mode=ParseMode.HTML,
            reply_markup=subscription_keyboard(),
        )
    elif subscription_status:
        games = db.get_all_games()
        if not games:
            await message.answer(
                f"👋 <b>Salom, {user.first_name}!</b>\n\n"
                "✅ <b>Obuna tasdiqlandi!</b>\n\n"
                "📭 Hozircha hech qanday o'yin mavjud emas.\n"
                "Tez orada qo'shiladi!",
                parse_mode=ParseMode.HTML,
            )
        else:
            await message.answer(
                f"👋 <b>Salom, {user.first_name}!</b>\n\n"
                "✅ <b>Obuna tasdiqlandi!</b>\n\n"
                "🎮 <b>Mavjud o'yinlar:</b>\nQaysi o'yinni tanlaysiz?",
                parse_mode=ParseMode.HTML,
                reply_markup=games_keyboard(games),
            )
    else:
        await message.answer(
            f"👋 <b>Salom, {user.first_name}!</b>\n\n"
            "❌ <b>Obuna talab qilinadi!</b>\n\n"
            "🎮 GameHub Bot'dan foydalanish uchun avval kanallarga obuna bo'ling:",
            parse_mode=ParseMode.HTML,
            reply_markup=subscription_keyboard(),
        )


@router.callback_query(F.data == "check_sub")
async def check_subscription(call: CallbackQuery):
    user_id = call.from_user.id
    ban_until = db.get_ban(user_id)
    if ban_until:
        remaining = ban_until - datetime.now()
        hours = int(remaining.total_seconds() // 3600)
        mins = int((remaining.total_seconds() % 3600) // 60)
        await call.answer(f"⛔ Siz {hours}s {mins}d ban ostisiz!", show_alert=True)
        return

    tg_ok = await is_subscribed(call.bot, user_id)
    db.set_subscription(user_id, tg_ok)

    if not tg_ok:
        await call.answer(
            "❌ Siz hali Telegram kanalga obuna bo'lmagansiz!\n"
            "Iltimos, barcha kanallarga obuna bo'lib qaytadan tekshiring.",
            show_alert=True,
        )
        return

    await call.answer()
    games = db.get_all_games()
    if not games:
        await call.message.edit_text(
            "✅ <b>Obuna tasdiqlandi!</b>\n\n"
            "📭 Hozircha hech qanday o'yin mavjud emas.\n"
            "Tez orada qo'shiladi!",
            parse_mode=ParseMode.HTML,
        )
        return

    await call.message.edit_text(
        "✅ <b>Obuna tasdiqlandi!</b>\n\n"
        "🎮 <b>Mavjud o'yinlar:</b>\nQaysi o'yinni tanlaysiz?",
        parse_mode=ParseMode.HTML,
        reply_markup=games_keyboard(games),
    )


@router.callback_query(F.data.startswith("game_"))
async def send_game_file(call: CallbackQuery):
    user_id = call.from_user.id
    tg_ok = await is_subscribed(call.bot, user_id)
    if not tg_ok:
        await call.answer("❌ Avval obuna bo'ling!", show_alert=True)
        return

    game_id = int(call.data.split("_")[1])
    game = db.get_game(game_id)
    if not game:
        await call.answer("❌ O'yin topilmadi!", show_alert=True)
        return

    await call.answer(f"📤 {game['name']} yuborilmoqda...", show_alert=False)
    try:
        await call.bot.send_document(
            chat_id=user_id,
            document=game["file_id"],
            caption=f"🎮 <b>{game['name']}</b>\n\n📥 Yuklab oling va o'ynang!",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.error("Fayl yuborishda xato: %s", e)
        await call.message.answer("❌ Fayl yuborishda xato yuz berdi.")


@router.message(Command("jasur"))
async def admin_cmd(message: Message, state: FSMContext):
    await state.set_state(AdminLogin.waiting_password)
    await state.update_data(attempts=0)
    await message.answer(
        "🔐 <b>Admin paneli</b>\n\nParolni kiriting:",
        parse_mode=ParseMode.HTML,
    )


@router.message(AdminLogin.waiting_password)
async def check_admin_password(message: Message, state: FSMContext):
    data = await state.get_data()
    attempts = data.get("attempts", 0)
    user_id = message.from_user.id

    if message.text == ADMIN_PASSWORD:
        await state.set_state(AdminPanel.idle)
        await message.answer(
            "✅ <b>Admin panelga xush kelibsiz!</b>\n\nNima qilmoqchisiz?",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_main_keyboard(),
        )
    else:
        attempts += 1
        remaining = MAX_ATTEMPTS - attempts
        if remaining <= 0:
            ban_until = datetime.now() + timedelta(hours=24)
            db.set_ban(user_id, ban_until)
            await state.clear()
            await message.answer(
                "⛔ <b>Noto'g'ri parol!</b>\n\nSiz <b>24 soatga</b> bloklandingiz!",
                parse_mode=ParseMode.HTML,
            )
        else:
            await state.update_data(attempts=attempts)
            await message.answer(
                f"❌ <b>Noto'g'ri parol!</b>\nQolgan urinishlar: <b>{remaining}</b>",
                parse_mode=ParseMode.HTML,
            )


@router.callback_query(StateFilter(AdminPanel), F.data == "admin_upload")
async def admin_upload_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(AdminPanel.upload_name)
    await safe_edit_text(
        call.message,
        "📁 <b>Yangi o'yin qo'shish</b>\n\nO'yin nomini kiriting:\n<i>Misol: GTA 5, Minecraft, FIFA 25</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_back_keyboard(),
    )


@router.message(AdminPanel.upload_name)
async def admin_upload_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(game_name=name)
    await state.set_state(AdminPanel.upload_file)
    await message.answer(
        f"✅ Nom: <b>{name}</b>\n\n📎 Endi faylni yuboring (ixtiyoriy format):",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_back_keyboard(),
    )


@router.message(AdminPanel.upload_file, F.document)
async def admin_upload_file(message: Message, state: FSMContext):
    data = await state.get_data()
    game_name = data["game_name"]
    file_id = message.document.file_id
    db.add_game(game_name, file_id)
    await state.set_state(AdminPanel.idle)
    await message.answer(
        f"✅ <b>{game_name}</b> muvaffaqiyatli qo'shildi!",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_main_keyboard(),
    )


@router.message(AdminPanel.upload_file)
async def admin_upload_wrong(message: Message):
    await message.answer(
        "❗ Iltimos, fayl yuboring (document sifatida).",
        reply_markup=admin_back_keyboard(),
    )


@router.callback_query(StateFilter(AdminPanel), F.data == "admin_broadcast")
async def admin_broadcast_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(AdminPanel.broadcast_message)
    await safe_edit_text(
        call.message,
        "📨 <b>Xabar yuborish</b>\n\nBarcha foydalanuvchilarga yuboriladigan xabarni kiriting:",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_back_keyboard(),
    )


@router.message(AdminPanel.broadcast_message)
async def admin_broadcast_send(message: Message, state: FSMContext):
    users = db.get_all_users()
    sent = 0
    failed = 0
    status_msg = await message.answer(f"📤 Yuborilmoqda... (0/{len(users)})")

    for i, u in enumerate(users):
        try:
            await message.bot.copy_message(
                chat_id=u["user_id"],
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )
            sent += 1
        except Exception:
            failed += 1
        if (i + 1) % 20 == 0:
            try:
                await status_msg.edit_text(f"📤 Yuborilmoqda... ({i + 1}/{len(users)})")
            except Exception:
                pass
        await asyncio.sleep(0.05)

    await state.set_state(AdminPanel.idle)
    await status_msg.edit_text(
        f"✅ <b>Xabar yuborildi!</b>\n\n"
        f"✔️ Muvaffaqiyatli: <b>{sent}</b>\n"
        f"❌ Xato: <b>{failed}</b>",
        parse_mode=ParseMode.HTML,
    )
    await message.answer(
        "✅ <b>Admin panel</b>\n\nNima qilmoqchisiz?",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_main_keyboard(),
    )


@router.callback_query(StateFilter(AdminPanel), F.data == "admin_stats")
async def admin_stats(call: CallbackQuery):
    await call.answer()
    users_count = db.count_users()
    games_count = db.count_games()
    await safe_edit_text(
        call.message,
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users_count}</b>\n"
        f"🎮 O'yinlar: <b>{games_count}</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_main_keyboard(),
    )


@router.callback_query(StateFilter(AdminPanel), F.data == "admin_delete")
async def admin_delete_list(call: CallbackQuery):
    games = db.get_all_games()
    if not games:
        await call.answer("📭 O'yin mavjud emas!", show_alert=True)
        return

    await call.answer()
    buttons = [
        [InlineKeyboardButton(text=f"🗑 {g['name']}", callback_data=f"del_{g['id']}")]
        for g in games
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Admin panelga", callback_data="admin_back")])
    await safe_edit_text(
        call.message,
        "🗑 <b>O'chiriladi:</b> Qaysi o'yinni o'chirasiz?",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(StateFilter(AdminPanel), F.data.startswith("del_"))
async def admin_delete_game(call: CallbackQuery, state: FSMContext):
    game_id = int(call.data.split("_")[1])
    game = db.get_game(game_id)
    if game:
        db.delete_game(game_id)
        await call.answer(f"✅ {game['name']} o'chirildi!", show_alert=True)
    else:
        await call.answer("❌ O'yin topilmadi!", show_alert=True)
    await state.set_state(AdminPanel.idle)
    await safe_edit_text(
        call.message,
        "✅ <b>Admin panel</b>\n\nNima qilmoqchisiz?",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_main_keyboard(),
    )


@router.callback_query(StateFilter(AdminPanel), F.data == "admin_back")
async def admin_back(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(AdminPanel.idle)
    await safe_edit_text(
        call.message,
        "✅ <b>Admin panel</b>\n\nNima qilmoqchisiz?",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_main_keyboard(),
    )


@router.callback_query(StateFilter(AdminPanel), F.data == "admin_logout")
async def admin_logout(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.clear()
    await safe_edit_text(call.message, "🚪 Admin paneldan chiqdingiz.")


async def main():
    db.init_db()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    logger.info("Bot ishga tushdi")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
