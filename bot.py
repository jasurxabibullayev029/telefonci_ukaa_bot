import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import enums
import json
import sqlite3
from datetime import datetime

# Bot tokeningizni shu yerga kiriting
BOT_TOKEN = "8746729342:AAHfL47fiRjWCwXq1fVS5CmNVsSw2mGAwLw"  # @BotFather dan olingan to'g'ri tokenni kiriting

# Kanal username ( @ belgisiz )
CHANNEL_USERNAME = "jasurdvv"
CHANNEL_USERNAME_2 = "telefonci_ukaa"

# Admin Telegram user ID lari (@userinfobot orqali tekshiring)
ADMIN_IDS = {1209491758}

# Botni sozlash
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)
dp = Dispatcher()

# Kanalga obuna bo'lish tugmasi
async def get_channel_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📺 1-kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME}")],
        [InlineKeyboardButton(text="📺 2-kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME_2}")],
        [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription")]
    ])
    return keyboard

# Oyinlar yuklash tugmalari
async def get_gta_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 GTA 5ni yuklash", callback_data="download_gta5")],
        [InlineKeyboardButton(text="🥊 Mortal Kombatni yuklash", callback_data="download_mortal_kombat")],
        [InlineKeyboardButton(text="🏎 Forza Horizon 5ni yuklash", callback_data="download_forza_horizon_5")]
    ])
    return keyboard

# /start komandasi
@dp.message(CommandStart())
async def start_command(message: Message):
    # Foydalanuvchi bazaga qo'shamiz (faqat bir marta)
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
            # Agar foydalanuvchi bazada bo'lsa, qaytaramiz
            if str(message.from_user.id) in users:
                await message.answer(
                    "👋 Assalomu alaykum! O'yinlar yuklash botiga xush kelibsiz!\n\n"
                    "🎮 Bu bot orqali siz turli xil o'yinlarni yuklab olishingiz mumkin.\n"
                    "📥 Yuklashni boshlash uchun pastdagi tugmalarni bosing.",
                    reply_markup=await get_gta_keyboard()
                )
                return
    except:
        users = {}
    
    # Yangi foydalanuvchini qo'shamiz
    users[str(message.from_user.id)] = {
        "name": message.from_user.full_name,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)
    except:
        pass
    
    # Faqat yangi foydalanuvchilarga javob beramiz
    await message.answer(
        "👋 Assalomu alaykum! O'yinlar yuklash botiga xush kelibsiz!\n\n"
        "🎮 Bu bot orqali siz turli xil o'yinlarni yuklab olishingiz mumkin.\n"
        "📥 Yuklashni boshlash uchun pastdagi tugmalarni bosing.",
        reply_markup=await get_gta_keyboard()
    )

# Fayl yuklash komandasi (admin uchun)
@dp.message(F.document)
async def handle_document(message: Message):
    # Faqat admin fayl yuklashi mumkin
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("🚫 **Faqat adminlar fayl yuklashi mumkin!**")
        return
    
    # Faqat admin fayl yuklashi mumkin
    if message.from_user.id in ADMIN_IDS:  # Bot egasi ID
        file_info = message.document
        await message.answer(
            f"📄 Fayl qabul qilindi:\n\n"
            f"📝 Nomi: {file_info.file_name}\n"
            f"🆔 File ID: `{file_info.file_id}`\n"
            "🔧 Bu ID ni kodga qo'ying!"
        )
    else:
        await message.answer("❌ Faqat admin fayl yuklashi mumkin!")

# Admin paneli
@dp.message(F.text == "/admin")
async def admin_panel(message: Message):
    # Faqat adminlar kirishi mumkin
    if message.from_user.id not in ADMIN_IDS:
        await message.answer(
            "🚫 **Ruxsat berilmadi!**\n\n"
            "❌ Siz admin emassiz!\n"
            "🛡️ Faqat adminlar kirishi mumkin.\n\n"
            "📞 Agar xato bo'lsa, admin bilan bog'laning."
        )
        return
    
    # Parolni so'rash
    await message.answer(
        "🔐 **Admin panelga kirish**\n\n"
        "🔑 Parolni kiriting:",
        reply_markup=types.ForceReply()
    )

# Admin state lari uchun dictionary
admin_states = {}

# Admin session lari uchun dictionary
admin_sessions = {}

# Admin parolini tekshirish
@dp.message(F.text)
async def check_admin_password(message: Message):
    # Agar bu parol tekshiruvi bo'lsa
    if message.reply_to_message and "Parolni kiriting:" in message.reply_to_message.text:
        password = message.text.strip()
        
        if password == "vfx.jasur2010":
            # Parol to'g'ri - admin session yaratish
            admin_sessions[message.from_user.id] = True
            
            # Admin panelni ko'rsatish
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Statistika", callback_data="stats")],
                [InlineKeyboardButton(text="📄 Fayllar", callback_data="files")],
                [InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="broadcast")],
                [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")],
                [InlineKeyboardButton(text="➕ O'yin qo'shish", callback_data="add_game")]
            ])
            await message.answer(
                "👑 **Admin Panel**\n\n"
                "Kerakli bo'limni tanlang:",
                reply_markup=keyboard
            )
        else:
            # Parol noto'g'ri
            await message.answer(
                "❌ **Parol noto'g'ri!**\n\n"
                "🔑 Qayta urinib ko'ring:",
                reply_markup=types.ForceReply()
            )
        return
    
    # Agar bu admin state bo'lsa (o'yin qo'shish jarayoni)
    if message.from_user.id in admin_states and admin_states[message.from_user.id]["step"] == "waiting_game_name":
        game_name = message.text
        admin_states[message.from_user.id] = {
            "step": "waiting_video_link",
            "game_name": game_name
        }
        
        await message.answer(
            f"🎮 **O'yin nomi qabul qilindi:** {game_name}\n\n"
            "2️⃣ **Video linkini kiriting:**\n"
            "Masalan: https://youtu.be/example\n\n"
            "⏳ Video linkini kutayman..."
        )
        return  # Bu muhim - shu handlerni to'xtatish
    
    # Video linkini qabul qilish
    if message.from_user.id in admin_states and admin_states[message.from_user.id]["step"] == "waiting_video_link":
        video_link = message.text
        game_name = admin_states[message.from_user.id]["game_name"]
        
        # O'yinni database ga saqlash
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO games (name, video, file_id) VALUES (?, ?, ?)",
                (game_name, video_link, None)
            )
            conn.commit()
            
            # Admin state ni tozalash
            del admin_states[message.from_user.id]
            
            await message.answer(
                f"✅ **O'yin muvaffaqiyat qo'shildi!**\n\n"
                f"🎮 O'yin nomi: {game_name}\n"
                f"🎬 Video linki: {video_link}\n\n"
                f"📝 Endi o'yin uchun fayl yuboring.\n"
                f"Faylni shu o'yinga tegishli yuboring, bot uni avtomatik bog'laydi."
            )
        except sqlite3.IntegrityError:
            await message.answer("❌ Bu o'yin allaqachon mavjud!")
        finally:
            conn.close()
        return  # Bu muhim - shu handlerni to'xtatish
    
    # Boshqa xabarlar uchun odatiy ishlov
    pass

# Statistika
@dp.callback_query(F.data == "stats")
async def stats_callback(callback: types.CallbackQuery):
    # Faqat adminlar kirishi mumkin
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("🚫 Siz admin emassiz!", show_alert=True)
        return
    
    # Parol tekshiruvi o'rniga session yaratamiz
    if callback.from_user.id in admin_sessions:
        try:
            with open("users.json", "r") as f:
                users = json.load(f)
            total_users = len(users)
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Bugun kirgan foydalanuvchilar
            today_users = sum(1 for user in users.values() if user['date'].startswith(today))
            
            await callback.message.edit_text(
                f"📊 **Statistika**\n\n"
                f"👥 Jami foydalanuvchilar: {total_users}\n"
                f"📅 Bugun kirganlar: {today_users}\n"
                f"🎮 GTA 5 yuklanganlar: {users.get('downloads', 0)}\n\n"
                "🔄 Yangilash: /stats"
            )
        except FileNotFoundError:
            await callback.message.edit_text("📊 Statistika topilmadi")
        except Exception as e:
            await callback.message.edit_text(f"❌ Xatolik: {e}")
    else:
        await callback.answer("❌ Avval admin panelga kirishingiz kerak!", show_alert=True)

# Fayllarni ko'rish
@dp.callback_query(F.data == "files")
async def files_callback(callback: types.CallbackQuery):
    if callback.from_user.id in admin_sessions:
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM games ORDER BY created_at DESC")
            games = cursor.fetchall()
            
            if not games:
                await callback.message.edit_text("🎮 O'yinlar topilmadi")
                return
            
            games_text = "🎮 **O'yinlar ro'yxati**\n\n"
            for i, game in enumerate(games, 1):
                games_text += f"{i}. {game[1]}\n"
                games_text += f"   � Video: {game[2]}\n"
                games_text += f"   � Fayl: {'✅ Bor' if game[3] else '❌ Yo\'q'}\n"
                games_text += f"   📅 {game[4]}\n\n"
            
            await callback.message.edit_text(games_text)
        except Exception as e:
            await callback.message.edit_text(f"❌ Xatolik: {e}")
        finally:
            conn.close()
    else:
        await callback.answer("❌ Avval admin panelga kirishingiz kerak!", show_alert=True)

# Xabar yuborish
@dp.callback_query(F.data == "broadcast")
async def broadcast_callback(callback: types.CallbackQuery):
    if callback.from_user.id == 1209491758:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Barcha foydalanuvchilarga", callback_data="broadcast_all")],
            [InlineKeyboardButton(text="👥 Faqat obuna bo'lganlarga", callback_data="broadcast_subscribers")]
        ])
        await callback.message.edit_text(
            "📢 **Xabar yuborish**\n\n"
            "Qaysi guruhga yuborishni tanlang:",
            reply_markup=keyboard
        )
    else:
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)

# Sozlamalar
@dp.callback_query(F.data == "settings")
async def settings_callback(callback: types.CallbackQuery):
    if callback.from_user.id == 1209491758:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Kanal nomini o'zgartirish", callback_data="change_channel")],
            [InlineKeyboardButton(text="🎮 Faylni o'zgartirish", callback_data="change_file")],
            [InlineKeyboardButton(text="🎬 Videoni o'zgartirish", callback_data="change_video")]
        ])
        await callback.message.edit_text(
            "⚙️ **Sozlamalar**\n\n"
            "O'zgartirishni tanlang:",
            reply_markup=keyboard
        )
    else:
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
@dp.callback_query(F.data == "download_gta5")
async def download_gta5_callback(callback: types.CallbackQuery):
    # Avval botning kanaldagi holatini tekshiramiz
    try:
        bot_info = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", bot.id)
        bot_info2 = await bot.get_chat_member(f"@{CHANNEL_USERNAME_2}", bot.id)
        bot_is_admin = bot_info.status in ["administrator", "creator"] and bot_info2.status in ["administrator", "creator"]
        print(f"Bot 1-kanalda admin: {bot_info.status in ['administrator', 'creator']}")
        print(f"Bot 2-kanalda admin: {bot_info2.status in ['administrator', 'creator']}")
    except:
        bot_is_admin = False
        print("Bot kanallarda emas yoki admin emas")
    
    if not bot_is_admin:
        # Bot admin bo'lmasa, to'g'ridan-to'g'ri yechim taklif qilamiz
        try:
            await callback.message.edit_text(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} va @{CHANNEL_USERNAME_2} kanallariga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                "✅ Admin qilgach, qayta 'O'yinlarni yuklash' tugmasini bosing.",
                reply_markup=await get_gta_keyboard()
            )
        except:
            await callback.message.answer(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} va @{CHANNEL_USERNAME_2} kanallariga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                "✅ Admin qilgach, qayta 'O'yinlarni yuklash' tugmasini bosing.",
                reply_markup=await get_gta_keyboard()
            )
        await callback.answer("❌ Bot admin emas", show_alert=True)
        return
    
    # Bot admin bo'lsa, foydalanuvchi obunasini tekshiramiz
    try:
        chat_member = await bot.get_chat_member(
            chat_id=f"@{CHANNEL_USERNAME}",
            user_id=callback.from_user.id
        )
        chat_member2 = await bot.get_chat_member(
            chat_id=f"@{CHANNEL_USERNAME_2}",
            user_id=callback.from_user.id
        )
        
        print(f"User {callback.from_user.id} 1-kanal status: {chat_member.status}")
        print(f"User {callback.from_user.id} 2-kanal status: {chat_member2.status}")
        
        if chat_member.status in ["member", "administrator", "creator"] and chat_member2.status in ["member", "administrator", "creator"]:
            # Obuna bo'lgan bo'lsa, faylni yuboramiz
            try:
                # Faylni yuborish
                await bot.send_document(
                    chat_id=callback.from_user.id,
                    document="BQACAgIAAxkBAAICQmm--Z_LYXPh4R01ohZtFozIoPUrAAJElQACbqb5SROqD3hN2bi2OgQ",  # Grand Theft Auto V.zip to'g'ri file_id1111111111111111111111111111111111111111111111111111111111111111111111111111111111
                    caption="🎮 Grand Theft Auto V\n\n"
                           "📥 Fayl muvaffaqiyatli yuklandi!\n"
                           "🔧 O'yinni o'rnatish uchun arxivni oching.\n\n"
                           "🎬 O'yinni o'rnatish bo'yicha video:\n"
                           "🔗 https://youtu.be/ojvZgPs2YFo"
                )
                
                print(f"Fayl yuborildi user {callback.from_user.id} ga")
                
                # Xabarni o'zgartiramiz
                await callback.message.edit_text(
                    "✅ Siz kanalga muvaffaqiyatli obuna bo'ldingiz!\n\n"
                    "📥 GTA 5 fayli yuborildi!"
                )
            except Exception as file_error:
                print(f"Fayl yuborish xatoligi: {file_error}")
                # Agar fayl yuklab bo'lmasa, xatolik haqida xabar beramiz
                try:
                    await callback.message.edit_text(
                        "❌ Faylni yuklab bo'lmadi.\n\n"
                        "📞 Iltimos, admin bilan bog'laning:\n"
                        f"🔗 https://t.me/{CHANNEL_USERNAME}"
                    )
                except:
                    await callback.message.answer(
                        "❌ Faylni yuklab bo'lmadi.\n\n"
                        "� Iltimos, admin bilan bog'laning:\n"
                        f"🔗 https://t.me/{CHANNEL_USERNAME}"
                    )
            await callback.answer("✅ Fayl yuborildi!")
        else:
            # Obuna bo'lmagan bo'lsa, obuna bo'lishni so'raymiz
            try:
                await callback.message.edit_text(
                    "❗️ GTA 5ni yuklash uchun avval ikkala kanalga obuna bo'ling!\n\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            except:
                await callback.message.answer(
                    "❗️ GTA 5ni yuklash uchun avval ikkala kanalga obuna bo'ling!\n\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            await callback.answer("❗️ Avval ikkala kanalga obuna bo'ling!")
            
    except Exception as e:
        print(f"Download callback xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

# Mortal Kombat yuklash tugmasi bosilganda
@dp.callback_query(F.data == "download_mortal_kombat")
async def download_mortal_kombat_callback(callback: types.CallbackQuery):
    # Avval botning kanaldagi holatini tekshiramiz
    try:
        bot_info = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", bot.id)
        bot_info2 = await bot.get_chat_member(f"@{CHANNEL_USERNAME_2}", bot.id)
        bot_is_admin = bot_info.status in ["administrator", "creator"] and bot_info2.status in ["administrator", "creator"]
        print(f"Bot 1-kanalda admin: {bot_info.status in ['administrator', 'creator']}")
        print(f"Bot 2-kanalda admin: {bot_info2.status in ['administrator', 'creator']}")
    except:
        bot_is_admin = False
        print("Bot kanallarda emas yoki admin emas")
    
    if not bot_is_admin:
        # Bot admin bo'lmasa, to'g'ridan-to'g'ri yechim taklif qilamiz
        try:
            await callback.message.edit_text(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} kanaliga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                "✅ Admin qilgach, qayta 'Mortal Kombatni yuklash' tugmasini bosing.",
                reply_markup=await get_gta_keyboard()
            )
        except:
            await callback.message.answer(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} kanaliga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                "✅ Admin qilgach, qayta 'Mortal Kombatni yuklash' tugmasini bosing.",
                reply_markup=await get_gta_keyboard()
            )
        await callback.answer("❌ Bot admin emas", show_alert=True)
        return
    
    # Bot admin bo'lsa, foydalanuvchi obunasini tekshiramiz
    try:
        chat_member = await bot.get_chat_member(
            chat_id=f"@{CHANNEL_USERNAME}",
            user_id=callback.from_user.id
        )
        chat_member2 = await bot.get_chat_member(
            chat_id=f"@{CHANNEL_USERNAME_2}",
            user_id=callback.from_user.id
        )
        
        print(f"User {callback.from_user.id} 1-kanal status: {chat_member.status}")
        print(f"User {callback.from_user.id} 2-kanal status: {chat_member2.status}")
        
        if chat_member.status in ["member", "administrator", "creator"] and chat_member2.status in ["member", "administrator", "creator"]:
            # Obuna bo'lgan bo'lsa, Mortal Kombat faylini yuboramiz
            try:
                # Avval callback answer qilamiz
                await callback.answer("✅ Mortal Kombat fayli yuborilmoqda...")
                
                # Mortal Kombat faylini yuborish
                await bot.send_document(
                    chat_id=callback.from_user.id,
                    document="BQACAgIAAxkBAAICSWm--lqvEITFKzJjz3zWGKRDwxLkAAJLlQACbqb5SdXV7pWXaQeUOgQ",  # Mortal Kombat 1 file_id111111111111111111111111111111111111111111111111111111111111111111111111111111111111
                    caption="🥊 **Mortal Kombat 1**\n\n"
                           "📥 Fayl muvaffaqiyatli yuklandi!\n"
                           "🔧 O'yinni o'rnatish uchun arxivni oching.\n\n"
                           "🎬 O'yinni o'rnatish bo'yicha video:\n"
                           "https://youtu.be/woNuI0VWcpg"
                )
                print(f"Mortal Kombat fayli muvaffaqiyatli yuborildi: {callback.from_user.id}")
            except Exception as file_error:
                print(f"Mortal Kombat faylini yuborish xatoligi: {file_error}")
                await callback.message.edit_text(
                    "❌ Mortal Kombat faylini yuklab bo'lmadi.\n\n"
                    "📞 Iltimos, admin bilan bog'laning:\n"
                    f"🔗 https://t.me/{CHANNEL_USERNAME}"
                )
        else:
            # Obuna bo'lmagan bo'lsa, obuna bo'lishni so'raymiz
            try:
                await callback.message.edit_text(
                    "❗️ O'yinlarni yuklash uchun avval ikkala kanalga obuna bo'ling!\n\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            except:
                await callback.message.answer(
                    "❗️ O'yinlarni yuklash uchun avval ikkala kanalga obuna bo'ling!\n\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            await callback.answer("❗️ Avval ikkala kanalga obuna bo'ling!")
            
    except Exception as e:
        print(f"Mortal Kombat download callback xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

# Obunani tekshirish tugmasi bosilganda
@dp.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: types.CallbackQuery):
    # Avval botning kanaldagi holatini tekshiramiz
    try:
        bot_info = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", bot.id)
        bot_info2 = await bot.get_chat_member(f"@{CHANNEL_USERNAME_2}", bot.id)
        bot_is_admin = bot_info.status in ["administrator", "creator"] and bot_info2.status in ["administrator", "creator"]
        print(f"Bot 1-kanalda admin: {bot_info.status in ['administrator', 'creator']}")
        print(f"Bot 2-kanalda admin: {bot_info2.status in ['administrator', 'creator']}")
    except:
        bot_is_admin = False
        print("Bot kanallarda emas yoki admin emas")
    
    if not bot_is_admin:
        # Bot admin bo'lmasa, to'g'ridan-to'g'ri yechim taklif qilamiz
        try:
            await callback.message.edit_text(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} kanaliga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                "✅ Admin qilgach, qayta 'Obunani tekshirish' tugmasini bosing.",
                reply_markup=await get_channel_keyboard()
            )
        except:
            await callback.message.answer(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} kanaliga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                "✅ Admin qilgach, qayta 'Obunani tekshirish' tugmasini bosing.",
                reply_markup=await get_channel_keyboard()
            )
        await callback.answer("❌ Bot admin emas", show_alert=True)
        return
    
    # Bot admin bo'lsa, foydalanuvchi obunasini tekshiramiz
    try:
        chat_member = await bot.get_chat_member(
            chat_id=f"@{CHANNEL_USERNAME}",
            user_id=callback.from_user.id
        )
        chat_member2 = await bot.get_chat_member(
            chat_id=f"@{CHANNEL_USERNAME_2}",
            user_id=callback.from_user.id
        )
        
        print(f"User {callback.from_user.id} 1-kanal status: {chat_member.status}")
        print(f"User {callback.from_user.id} 2-kanal status: {chat_member2.status}")
        
        if chat_member.status in ["member", "administrator", "creator"] and chat_member2.status in ["member", "administrator", "creator"]:
            # Obuna bo'lgan bo'lsa, faylni yuboramiz
            try:
                # Faylni yuborish
                await bot.send_document(
                    chat_id=callback.from_user.id,
                    document="BAACAgUAAxkDAAICOGF6i2b3Jt8nG8kVjvY7K6r8AAKqCAAJfGxkS2kqL8X7Y9v8BA",  # Grand Theft Auto V.zip to'g'ri file_id
                    caption="🎮 Grand Theft Auto V\n\n"
                           "📥 Fayl muvaffaqiyatli yuklandi!\n"
                           "🔧 O'yinni o'rnatish uchun arxivni oching.\n\n"
                           "🎬 O'yinni o'rnatish bo'yicha video:\n"
                           "🔗 https://youtu.be/ojvZgPs2YFo"
                )
                
                print(f"Fayl yuborildi user {callback.from_user.id} ga")
                
                # Xabarni o'zgartiramiz
                await callback.message.edit_text(
                    "✅ Siz kanalga muvaffaqiyatli obuna bo'ldingiz!\n\n"
                    "📥 GTA 5 fayli yuborildi!"
                )
            except Exception as file_error:
                print(f"Fayl yuborish xatoligi: {file_error}")
                # Agar fayl yuklab bo'lmasa, xatolik haqida xabar beramiz
                try:
                    await callback.message.edit_text(
                        "❌ Faylni yuklab bo'lmadi.\n\n"
                        "📞 Iltimos, admin bilan bog'laning:\n"
                        f"🔗 https://t.me/{CHANNEL_USERNAME}"
                    )
                except:
                    await callback.message.answer(
                        "❌ Faylni yuklab bo'lmadi.\n\n"
                        "� Iltimos, admin bilan bog'laning:\n"
                        f"🔗 https://t.me/{CHANNEL_USERNAME}"
                    )
            await callback.answer("✅ Obuna tasdiqlandi!")
        else:
            # Obuna bo'lmagan bo'lsa
            try:
                await callback.message.edit_text(
                    "❌ Siz hali kanalga obuna bo'lmagansiz!\n\n"
                    "📺 Iltimos, kanalga obuna bo'ling:\n"
                    f"🔗 https://t.me/{CHANNEL_USERNAME}\n\n"
                    "Obuna bo'lgach, qayta 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            except:
                await callback.message.answer(
                    "❌ Siz hali kanalga obuna bo'lmagansiz!\n\n"
                    "📺 Iltimos, kanalga obuna bo'ling:\n"
                    f"🔗 https://t.me/{CHANNEL_USERNAME}\n\n"
                    "Obuna bo'lgach, qayta 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            await callback.answer("❌ Obuna bo'lmagan", show_alert=True)
            
    except Exception as e:
        print(f"Foydalanuvchini tekshirish xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

# Forza Horizon 5 yuklash tugmasi bosilganda
@dp.callback_query(F.data == "download_forza_horizon_5")
async def download_forza_horizon_5_callback(callback: types.CallbackQuery):
    # Avval botning kanaldagi holatini tekshiramiz
    try:
        bot_info = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", bot.id)
        bot_info2 = await bot.get_chat_member(f"@{CHANNEL_USERNAME_2}", bot.id)
        bot_is_admin = bot_info.status in ["administrator", "creator"] and bot_info2.status in ["administrator", "creator"]
        print(f"Bot 1-kanalda admin: {bot_info.status in ['administrator', 'creator']}")
        print(f"Bot 2-kanalda admin: {bot_info2.status in ['administrator', 'creator']}")
    except:
        bot_is_admin = False
        print("Bot kanallarda emas yoki admin emas")
    
    if not bot_is_admin:
        # Bot admin bo'lmasa, to'g'ridan-to'g'ri yechim taklif qilamiz
        try:
            await callback.message.edit_text(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} kanaliga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                "✅ Admin qilgach, qayta 'Forza Horizon 5ni yuklash' tugmasini bosing.",
                reply_markup=await get_gta_keyboard()
            )
        except:
            await callback.message.answer(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} kanaliga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                "✅ Admin qilgach, qayta 'Forza Horizon 5ni yuklash' tugmasini bosing.",
                reply_markup=await get_gta_keyboard()
            )
        await callback.answer("❌ Bot admin emas", show_alert=True)
        return
    
    # Bot admin bo'lsa, foydalanuvchi obunasini tekshiramiz
    try:
        chat_member = await bot.get_chat_member(
            chat_id=f"@{CHANNEL_USERNAME}",
            user_id=callback.from_user.id
        )
        chat_member2 = await bot.get_chat_member(
            chat_id=f"@{CHANNEL_USERNAME_2}",
            user_id=callback.from_user.id
        )
        
        print(f"User {callback.from_user.id} 1-kanal status: {chat_member.status}")
        print(f"User {callback.from_user.id} 2-kanal status: {chat_member2.status}")
        
        if chat_member.status in ["member", "administrator", "creator"] and chat_member2.status in ["member", "administrator", "creator"]:
            # Obuna bo'lgan bo'lsa, Forza Horizon 5 faylini yuboramiz
            try:
                # Avval callback answer qilamiz
                await callback.answer("✅ Forza Horizon 5 fayli yuborilmoqda...")
                
                # Forza Horizon 5 faylini yuborish
                await bot.send_document(
                    chat_id=callback.from_user.id,
                    document="BQACAgIAAxkBAAICUGm-_C1asZ3VgwePfeSt0LBclhNlAAJllQACbqb5SaLvElWNu8hEOgQ",  # Forza Horizon 5.zip file_id111111111111111111111
                    caption="🏎 **Forza Horizon 5**\n\n"
                           "📥 Fayl muvaffaqiyatli yuklandi!\n"
                           "🔧 O'yinni o'rnatish uchun arxivni oching.\n\n"
                           "🎬 O'yinni o'rnatish bo'yicha video:\n"
                           "🔗 https://youtu.be/ojvZgPs2YFo"
                )
                print(f"Forza Horizon 5 fayli muvaffaqiyatli yuborildi: {callback.from_user.id}")
            except Exception as file_error:
                print(f"Forza Horizon 5 faylini yuborish xatoligi: {file_error}")
                await callback.message.edit_text(
                    "❌ Forza Horizon 5 faylini yuklab bo'lmadi.\n\n"
                    "📞 Iltimos, admin bilan bog'laning:\n"
                    f"🔗 https://t.me/{CHANNEL_USERNAME}"
                )
        else:
            # Obuna bo'lmagan bo'lsa, obuna bo'lishni so'raymiz
            try:
                await callback.message.edit_text(
                    "❗️ Forza Horizon 5ni yuklash uchun avval ikkala kanalga obuna bo'ling!\n\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            except:
                await callback.message.answer(
                    "❗️ Forza Horizon 5ni yuklash uchun avval ikkala kanalga obuna bo'ling!\n\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            await callback.answer("❗️ Avval ikkala kanalga obuna bo'ling!")
            
    except Exception as e:
        print(f"Forza Horizon 5 download callback xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

async def main():
    # Loggingni sozlash
    logging.basicConfig(level=logging.INFO)
    
    # Botni ishga tushurish
    await dp.start_polling(
        bot,
        handle_signals=False  # Signal handlingni o'chirib tashlaymiz
    )

if __name__ == "__main__":
    asyncio.run(main())
