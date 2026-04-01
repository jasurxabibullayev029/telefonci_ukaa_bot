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
BOT_TOKEN = "8257079297:AAF9buIS7tBH0Nayk7I4RJ3g569hT9y5JBs"  # @BotFather dan olingan to'g'ri tokenni kiriting

# Kanal username ( @ belgisiz )
CHANNEL_USERNAME = "telefonci_ukaa"
CHANNEL_LINK = "https://t.me/telefonci_ukaa"  # Birinchi kanal linki
SECOND_CHANNEL_USERNAME = "iPhone_Lifee"  # Ikkinchi kanal nomi
SECOND_CHANNEL_LINK = "https://t.me/iPhone_Lifee"  # Ikkinchi kanal linki

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
        [InlineKeyboardButton(text="📺 Telefonci Ukaa kanaliga obuna bo'lish", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="📱 iPhone Life kanaliga obuna bo'lish", url=SECOND_CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription")]
    ])
    return keyboard

# Doimiy reply keyboard (HELP button har doim ko'rinadi)
async def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="ℹ️ HELP")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

# Help keyboard with admin contact button
async def get_help_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="‍💻 Admin bilan bog'lanish", url="https://t.me/jasurdv")]
    ])
    return keyboard

# Yangi kanal uchun ariza qabul qilish
async def handle_new_channel_request(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "username yo'q"
    first_name = message.from_user.first_name or "ism yo'q"
    
    # Adminlarga xabar yuborish
    admin_text = f"""
🆕 **Yangi kanalga ariza!**

👤 **Foydalanuvchi ma'lumotlari:**
🆔 ID: {user_id}
👤 Username: @{username}
📝 Ismi: {first_name}

📺 **Kanal:** {NEW_CHANNEL_USERNAME}
🔗 **Taklif linki:** {NEW_CHANNEL_LINK}

⏰ **Vaqt:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---
🎯 **Avtomatik ariza qabul qilish tizimi**
    """
    
    # Adminlarga xabar yuborish
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=admin_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"approve_request_{user_id}")],
                    [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_request_{user_id}")],
                    [InlineKeyboardButton(text="👤 Foydalanuvchiga yozish", url=f"https://t.me/{username}")]
                ])
            )
        except Exception as e:
            print(f"Adminga xabar yuborish xatoligi: {e}")
    
    # Foydalanuvchiga javob
    await message.answer(
        "✅ **Ariza yuborildi!**\n\n"
        "📝 Sizning arizangiz adminlarga yuborildi.\n"
        "👑 Adminlar ko'rib chiqib, tez orada javob berishadi.\n\n"
        "⏳ Iltimos, biroz kutib turing..."
    )

# Oyinlar yuklash tugmalari (database dan dinamik)
async def get_gta_keyboard():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    try:
        # Faqat fayli bor o'yinlarni olish
        cursor.execute("SELECT name FROM games WHERE file_id IS NOT NULL ORDER BY name")
        games = cursor.fetchall()
        
        if not games:
            # Agar o'yinlar bo'lmasa, bo'sh keyboard qaytaramiz
            return InlineKeyboardMarkup(inline_keyboard=[])
        
        # O'yinlar uchun tugmalar
        buttons = []
        for game in games:
            game_name = game[0]
            # Callback data ni o'yin nomidan yasaymiz
            callback_data = f"download_{game_name.lower().replace(' ', '_')}"
            buttons.append([InlineKeyboardButton(text=f"🎮 {game_name}", callback_data=callback_data)])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
        
    except Exception as e:
        print(f"Keyboard yaratish xatoligi: {e}")
        return InlineKeyboardMarkup(inline_keyboard=[])
    finally:
        conn.close()

# Ariza qabul qilish callback
@dp.callback_query(F.data.startswith("approve_request_"))
async def approve_request_callback(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("🚫 Siz admin emassiz!", show_alert=True)
        return
    
    # User ID ni olish
    user_id = int(callback.data.split("_")[-1])
    
    try:
        # Foydalanuvchiga xabar yuborish
        await bot.send_message(
            chat_id=user_id,
            text=f"""
✅ **Arizangiz qabul qilindi!** 

🎉 Tabriklaymiz! Siz {NEW_CHANNEL_USERNAME} kanaliga qo'shildingiz.

📺 **Kanal:** {NEW_CHANNEL_USERNAME}
🔗 **Kanalga o'tish:** {NEW_CHANNEL_LINK}

🎯 **Endi siz:**
• Kanaldagi barcha kinolarni tomosha qilishingiz mumkin
• Yangi kinolardan xabardor bo'lasiz
• Boshqa a'zolar bilan suhbat qurishingiz mumkin

🙏 **Kanalga tashrifingiz uchun rahmat!**
            """
        )
        
        # Adminga xabar
        await callback.message.edit_text(
            f"✅ **Ariza qabul qilindi!**\n\n"
            f"👤 Foydalanuvchi ID: {user_id}\n"
            f"📺 Kanal: {NEW_CHANNEL_USERNAME}\n"
            f"⏰ Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await callback.answer("✅ Ariza qabul qilindi!", show_alert=True)
        
    except Exception as e:
        print(f"Ariza qabul qilish xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)

# HELP callback handler
@dp.callback_query(F.data == "help")
async def help_callback(callback: types.CallbackQuery):
    help_text = f"""
ℹ️ **YORDAM**

🤖 **Bot haqida ma'lumot:**
Bu bot sizga turli xil o'yinlarni yuklab berish uchun xizmat qiladi.

📱 **Admin bilan bog'lanish:**
👤 Admin username: @jasurdv

🆘 **Agar bot ishlamasa:**
• Bot javob bermayotgan bo'lsa
• Fayl yuklab bo'lmayotgan bo'lsa
• Boshqa texnik muammolar bo'lsa

📞 **Darhol admin bilan bog'laning:**
@jasurdv ga yozing va muammoni tavsiflang!

🙏 **Tashrifingiz uchun rahmat!**
    """
    
    try:
        await callback.message.edit_text(
            help_text,
            reply_markup=await get_channel_keyboard()
        )
    except:
        await callback.message.answer(
            help_text,
            reply_markup=await get_channel_keyboard()
        )
    
    await callback.answer("ℹ️ Yordam ko'rsatildi!", show_alert=True)

# HELP button message handler
@dp.message(F.text == "ℹ️ HELP")
async def help_message_handler(message: Message):
    help_text = f"""
ℹ️ **YORDAM**

🤖 **Bot haqida ma'lumot:**
Bu bot sizga turli xil o'yinlarni yuklab berish uchun xizmat qiladi.

🆘 **Agar bot ishlamasa:**
• Bot javob bermayotgan bo'lsa
• Fayl yuklab bo'lmayotgan bo'lsa
• Boshqa texnik muammolar bo'lsa

📞 **Yechim:**
Pastdagi "Admin bilan bog'lanish" tugmasini bosing!

🙏 **Tashrifingiz uchun rahmat!**
    """
    
    await message.answer(
        help_text,
        reply_markup=await get_help_keyboard()
    )

# Fayl yuborish callback (admin uchun)
@dp.callback_query(F.data.startswith("send_file_"))
async def send_file_callback(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("🚫 Siz admin emassiz!", show_alert=True)
        return
    
    # User ID ni olish
    user_id = int(callback.data.split("_")[-1])
    
    try:
        # Foydalanuvchiga fayl yuborish
        await bot.send_document(
            chat_id=user_id,
            document="BAACAgUAAxkDAAICOGF6i2b3Jt8nG8kVjvY7K6r8AAKqCAAJfGxkS2kqL8X7Y9v8BA",
            caption="🎮 Grand Theft Auto V\n\n"
                   "📥 Fayl muvaffaqiyatli yuklandi!\n"
                   "🔧 O'yinni o'rnatish uchun arxivni oching.\n\n"
                   "🎬 O'yinni o'rnatish bo'yicha video:\n"
                   "🔗 https://youtu.be/ojvZgPs2YFo\n\n"
                   "✅ **Arizangiz tasdiqlandi!**\n"
                   f"📺 {NEW_CHANNEL_USERNAME} kanaliga obuna bo'lganingiz uchun rahmat!"
        )
        
        # Adminga xabar
        await callback.message.edit_text(
            f"✅ **Fayl yuborildi!**\n\n"
            f"👤 Foydalanuvchi ID: {user_id}\n"
            f"🎮 O'yin: GTA 5\n"
            f"📺 Kanal: {NEW_CHANNEL_USERNAME}\n"
            f"⏰ Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await callback.answer("✅ Fayl yuborildi!", show_alert=True)
        
    except Exception as e:
        print(f"Fayl yuborish xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)

# Fayl rad etish callback (admin uchun)
@dp.callback_query(F.data.startswith("reject_file_"))
async def reject_file_callback(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("🚫 Siz admin emassiz!", show_alert=True)
        return
    
    # User ID ni olish
    user_id = int(callback.data.split("_")[-1])
    
    try:
        # Foydalanuvchiga xabar yuborish
        await bot.send_message(
            chat_id=user_id,
            text=f"""
❌ **Arizangiz rad etildi!**

😔 Kechirasiz, sizning arizangiz {NEW_CHANNEL_USERNAME} kanaliga fayl olish uchun rad etildi.

📝 **Sabab:** Adminlar tomonidan ko'rib chiqilgandan so'ng rad etildi.

🔄 **Qayta urinish:**
• Kanalga to'liq obuna bo'ling
• Yoki admin bilan bog'laning

📞 **Admin bilan bog'lanish:**
• @admin_username yozing
• Yoki boshqa usul bilan aloqa qiling

🙏 **Tushunishingiz uchun rahmat!**
            """
        )
        
        # Adminga xabar
        await callback.message.edit_text(
            f"❌ **Ariza rad etildi!**\n\n"
            f"👤 Foydalanuvchi ID: {user_id}\n"
            f"🎮 O'yin: GTA 5\n"
            f"📺 Kanal: {NEW_CHANNEL_USERNAME}\n"
            f"⏰ Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await callback.answer("❌ Ariza rad etildi!", show_alert=True)
        
    except Exception as e:
        print(f"Ariza rad etish xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)

# Ariza rad etish callback
@dp.callback_query(F.data.startswith("reject_request_"))
async def reject_request_callback(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("🚫 Siz admin emassiz!", show_alert=True)
        return
    
    # User ID ni olish
    user_id = int(callback.data.split("_")[-1])
    
    try:
        # Foydalanuvchiga xabar yuborish
        await bot.send_message(
            chat_id=user_id,
            text=f"""
❌ **Arizangiz rad etildi!**

😔 Kechirasiz, sizning arizangiz {NEW_CHANNEL_USERNAME} kanaliga qo'shilish uchun rad etildi.

📝 **Sabab:** Adminlar tomonidan ko'rib chiqilgandan so'ng rad etildi.

🔄 **Qayta urinish:**
• Agar xatolik bo'lsa, admin bilan bog'laning
• Yoki keyinroq qayta ariza yuboring

📞 **Admin bilan bog'lanish:**
• @admin_username yozing
• Yoki boshqa usul bilan aloqa qiling

🙏 **Tushunishingiz uchun rahmat!**
            """
        )
        
        # Adminga xabar
        await callback.message.edit_text(
            f"❌ **Ariza rad etildi!**\n\n"
            f"👤 Foydalanuvchi ID: {user_id}\n"
            f"📺 Kanal: {NEW_CHANNEL_USERNAME}\n"
            f"⏰ Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await callback.answer("❌ Ariza rad etildi!", show_alert=True)
        
    except Exception as e:
        print(f"Ariza rad etish xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)

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
                # Show reply keyboard with HELP button
                await message.answer(
                    "ℹ️ Yordam kerak bo'lsa, pastdagi HELP tugmasini bosing!",
                    reply_markup=await get_main_keyboard()
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
    # Show reply keyboard with HELP button
    await message.answer(
        "ℹ️ Yordam kerak bo'lsa, pastdagi HELP tugmasini bosing!",
        reply_markup=await get_main_keyboard()
    )

# Yangi kanal uchun ariza komandasi
@dp.message(F.text.startswith("/ariza_"))
async def channel_request_command(message: Message):
    # Kanal nomini olish
    command_parts = message.text.split("_", 1)
    channel_name = command_parts[1] if len(command_parts) > 1 else ""
    
    # SWEET HOME🛍️ ni tekshirish (case-insensitive)
    if "sweet" in channel_name.lower() and "home" in channel_name.lower():
        await handle_new_channel_request(message)
    else:
        await message.answer(
            "❌ **Noto'g'ri kanal nomi!**\n\n"
            f"📺 To'g'ri kanal: {NEW_CHANNEL_USERNAME}\n"
            f"🔗 Taklif linki: {NEW_CHANNEL_LINK}\n\n"
            f"📝 To'g'ri ariza uchun: /ariza_sweet_home"
        )

# Fayl ID ni kodga avtomatik yozish
async def write_file_id_to_code(game_name, file_id):
    try:
        # Bot kodini o'qish
        with open('bot.py', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # O'yin nomiga mos callback_data ni topish
        callback_data = f"download_{game_name.lower().replace(' ', '_')}"
        
        # Callback handler ni topish va file_id ni yangilish
        lines = content.split('\n')
        updated_lines = []
        in_callback = False
        callback_found = False
        
        for line in lines:
            # Callback handler boshlanishini aniqlash
            if f"@dp.callback_query(F.data == \"{callback_data}\")" in line:
                in_callback = True
                callback_found = True
                updated_lines.append(line)
                continue
            
            # Callback handler ichida file_id ni yangilash
            if in_callback and 'document=' in line and 'file_id' in line.lower():
                # Eski file_id ni yangisiga almashtirish
                import re
                # document="..." ichidagi file_id ni yangilash
                pattern = r'document="([^"]*)"'
                matches = re.findall(pattern, line)
                if matches:
                    old_file_id = matches[0]
                    line = line.replace(f'document="{old_file_id}"', f'document="{file_id}"')
            
            updated_lines.append(line)
            
            # Callback handler tugashini aniqlash
            if in_callback and line.strip().startswith('async def') and callback_data not in line:
                in_callback = False
        
        # Yangilangan kodni yozish
        if callback_found:
            with open('bot.py', 'w', encoding='utf-8') as file:
                file.write('\n'.join(updated_lines))
            
            print(f"✅ {game_name} uchun file_id kodga yozildi: {file_id}")
            print(f"🎮 {game_name} uchun callback handler muvaffaqiyat yangilandi!")
        else:
            print(f"⚠️ {game_name} uchun callback handler topilmadi!")
            print(f"🔥 Yangi callback handler yaratilmoqda...")
            
            # Yangi callback handler yaratish
            new_handler = f'''
# {game_name} yuklash tugmasi bosilganda
@dp.callback_query(F.data == "{callback_data}")
async def download_{game_name.lower().replace(' ', '_')}_callback(callback: types.CallbackQuery):
    # O'yin nomini olish
    game_name = "{game_name}"
    
    # Avval botning kanaldagi holatini tekshiramiz
    try:
        bot_info = await bot.get_chat_member(f"@{{CHANNEL_USERNAME}}", bot.id)
        bot_info2 = await bot.get_chat_member(f"@{{SECOND_CHANNEL_USERNAME}}", bot.id)
        bot_is_admin = bot_info.status in ["administrator", "creator"] and bot_info2.status in ["administrator", "creator"]
        print(f"Bot 1-kanalda admin: {{bot_info.status in ['administrator', 'creator']}}")
        print(f"Bot 2-kanalda admin: {{bot_info2.status in ['administrator', 'creator']}}")
    except:
        bot_is_admin = False
        print("Bot kanallarda emas yoki admin emas")
    
    if not bot_is_admin:
        # Bot admin bo'lmasa, to'g'ridan-to'g'ri yechim taklif qilamiz
        try:
            await callback.message.edit_text(
                "❌ Bot kanalga obunani tekshira olmaydi!\\n\\n"
                "🔧 Yechim:\\n"
                f"1. @{{CHANNEL_USERNAME}} va @{{SECOND_CHANNEL_USERNAME}} kanallariga o'ting\\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\\n"
                "3. 'Invite users via link' ruxsatini bering\\n\\n"
                f"✅ Admin qilgach, qayta '{game_name}ni yuklash' tugmasini bosing.",
                reply_markup=await get_gta_keyboard()
            )
        except:
            await callback.message.answer(
                "❌ Bot kanalga obunani tekshira olmaydi!\\n\\n"
                "🔧 Yechim:\\n"
                f"1. @{{CHANNEL_USERNAME}} va @{{SECOND_CHANNEL_USERNAME}} kanallariga o'ting\\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\\n"
                "3. 'Invite users via link' ruxsatini bering\\n\\n"
                f"✅ Admin qilgach, qayta '{game_name}ni yuklash' tugmasini bosing.",
                reply_markup=await get_gta_keyboard()
            )
        await callback.answer("❌ Bot admin emas", show_alert=True)
        return
    
    # Bot admin bo'lsa, foydalanuvchi obunasini tekshiramiz
    try:
        chat_member = await bot.get_chat_member(
            chat_id=f"@{{CHANNEL_USERNAME}}",
            user_id=callback.from_user.id
        )
        chat_member2 = await bot.get_chat_member(
            chat_id=f"@{{SECOND_CHANNEL_USERNAME}}",
            user_id=callback.from_user.id
        )
        
        print(f"User {{callback.from_user.id}} 1-kanal status: {{chat_member.status}}")
        print(f"User {{callback.from_user.id}} 2-kanal status: {{chat_member2.status}}")
        
        if chat_member.status in ["member", "administrator", "creator"] and chat_member2.status in ["member", "administrator", "creator"]:
            # Obuna bo'lgan bo'lsa, faylni yuboramiz
            try:
                # Avval callback answer qilamiz
                await callback.answer(f"✅ {game_name} fayli yuborilmoqda...")
                
                # Faylni yuborish
                await bot.send_document(
                    chat_id=callback.from_user.id,
                    document="{file_id}",
                    caption=f"🎮 {{game_name}}\\n\\n"
                           "📥 Fayl muvaffaqiyatli yuklandi!\\n"
                           "🔧 O'yinni o'rnatish uchun arxivni oching.\\n\\n"
                           "🎬 O'yinni o'rnatish bo'yicha video:\\n"
                           "🔗 https://youtu.be/ojvZgPs2YFo"
                )
                
                print(f"{game_name} fayli muvaffaqiyatli yuborildi: {{callback.from_user.id}}")
                
                # Xabarni o'zgartiramiz
                await callback.message.edit_text(
                    f"✅ Siz kanalga muvaffaqiyatli obuna bo'ldingiz!\\n\\n"
                    f"📥 {game_name} fayli yuborildi!"
                )
            except Exception as file_error:
                print(f"{game_name} faylini yuborish xatoligi: {{file_error}}")
                await callback.message.edit_text(
                    f"❌ {game_name} faylini yuklab bo'lmadi.\\n\\n"
                    "📞 Iltimos, admin bilan bog'laning:\\n"
                    f"🔗 https://t.me/{{CHANNEL_USERNAME}}"
                )
        else:
            # Obuna bo'lmagan bo'lsa, obuna bo'lishni so'raymiz
            try:
                await callback.message.edit_text(
                    f"❗️ {game_name}ni yuklash uchun avval ikkala kanalga obuna bo'ling!\\n\\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            except:
                await callback.message.answer(
                    f"❗️ {game_name}ni yuklash uchun avval ikkala kanalga obuna bo'ling!\\n\\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            await callback.answer("❗️ Avval ikkala kanalga obuna bo'ling!")
            
    except Exception as e:
        print(f"{game_name} download callback xatoligi: {{e}}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
'''
            
            # Yangi handler ni kodga qo'shish
            with open('bot.py', 'a', encoding='utf-8') as file:
                file.write(new_handler)
            
            print(f"✅ {game_name} uchun yangi callback handler yaratildi!")
            
    except Exception as e:
        print(f"❌ Kodni yangilashda xatolik: {e}")

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
        file_name = file_info.file_name
        file_id = file_info.file_id
        
        # Database ga ulash
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        try:
            # Oxirgi qo'shilgan o'yinni olish
            cursor.execute("SELECT name FROM games WHERE file_id IS NULL ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                game_name = result[0]
                
                # O'yinni topish va file_id ni yangilash
                cursor.execute(
                    "UPDATE games SET file_id = ? WHERE name = ?",
                    (file_id, game_name)
                )
                
                if cursor.rowcount > 0:
                    # Fayl ID ni kodga avtomatik yozish
                    await write_file_id_to_code(game_name, file_id)
                    
                    await message.answer(
                        f"✅ **Fayl avtomatik bog'landi!**\n\n"
                        f"🎮 O'yin: {game_name}\n"
                        f"📁 Fayl: {file_name}\n"
                        f"🆔 File ID: `{file_id}`\n\n"
                        f"🔧 Endi bu o'yin fayli yuklanadi!"
                    )
                    print(f"Fayl bog'landi: {game_name} -> {file_id}")
                    print(f"✅ O'yin '{game_name}' muvaffaqiyat qo'shildi va fayl bog'landi!")
                    print(f"📊 Database da {cursor.rowcount} ta o'yin yangilandi!")
                else:
                    await message.answer(
                        f"⚠️ **O'yin topilmadi!**\n\n"
                        f"🎮 O'yin: {game_name}\n"
                        f"📁 Fayl: {file_name}\n"
                        f"🆔 File ID: `{file_id}`\n\n"
                        f"🔧 Iltimos, avval admin paneldan o'yin qo'shing!"
                    )
                    print(f"O'yin topilmadi: {game_name}")
                    print(f"📊 Database da qo'shilgan o'yin yo'q! Avval o'yin qo'shing kerak.")
            else:
                await message.answer(
                    f"⚠️ **O'yin topilmadi!**\n\n"
                    f"📁 Fayl: {file_name}\n"
                    f"🆔 File ID: `{file_id}`\n\n"
                    f"🔧 Iltimos, avval admin paneldan o'yin qo'shing!"
                )
                print(f"❌ O'yin topilmadi: {game_name}")
                print(f"📊 Database da qo'shilgan o'yin yo'q! Avval o'yin qo'shing kerak.")
            
            conn.commit()
            
        except Exception as e:
            print(f"Database xatoligi: {e}")
            await message.answer(
                f"❌ **Xatolik yuz berdi!**\n\n"
                f"📁 Fayl: {file_name}\n"
                f"🆔 File ID: `{file_id}`\n\n"
                f"🔧 Qo'lda kodga qo'ying!"
            )
        finally:
            conn.close()
            
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
                [InlineKeyboardButton(text="📝 File ID ni kodga yozish", callback_data="write_file_id")],
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
        game_name = message.text.strip()
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
        video_link = message.text.strip()
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
    
    # O'yin nomini qabul qilish (qo'shish jarayonida)
    if message.from_user.id in admin_sessions and message.from_user.id in admin_states and admin_states[message.from_user.id]["step"] == "waiting_game_name":
        game_name = message.text.strip()
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
        return  # Bu muhim - shu handlerni to'xtatsh
    
    # Video linkini qabul qilish
    if message.from_user.id in admin_sessions and message.from_user.id in admin_states and admin_states[message.from_user.id]["step"] == "waiting_video_link":
        video_link = message.text.strip()
        game_name = admin_states[message.from_user.id]["game_name"]
        
        # Database ga qo'shish
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
        return  # Bu muhim - shu handlerni to'xtatsh
    
    # O'yin nomini qabul qilish (File ID ni kodga yozish uchun)
    if message.from_user.id in admin_sessions and message.from_user.id in admin_states and admin_states[message.from_user.id]["step"] == "waiting_game_name":
        game_name = message.text.strip()
        
        # Database ga qo'shish
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        try:
            # O'yin mavjudligini tekshirish
            cursor.execute("SELECT file_id FROM games WHERE name = ?", (game_name,))
            result = cursor.fetchone()
            
            if result:
                # O'yin allaqachon mavjud
                await message.answer(
                    f"❌ **Bu o'yin allaqachon mavjud!**\n\n"
                    f"🎮 O'yin: {game_name}\n"
                    f"🆔 Hozirgi File ID: `{result[0]}`\n\n"
                    f"📝 Agar File ID ni o'zgartirmoqchi bo'lsa, 'File ID ni kodga yozish' tugmasini bosing!"
                )
                print(f"❌ O'yin allaqachon mavjud: {game_name}")
            else:
                # O'yin yo'q, qo'shish
                cursor.execute(
                    "INSERT INTO games (name, video, file_id) VALUES (?, ?, ?)",
                    (game_name, "", None)
                )
                conn.commit()
                
                # Admin state ni tozalash
                del admin_states[message.from_user.id]
                
                await message.answer(
                    f"✅ **O'yin qo'shildi!**\n\n"
                    f"🎮 O'yin nomi: {game_name}\n"
                    f"📝 Endi fayl yuboring yoki 'File ID ni kodga yozish' tugmasini bosing!"
                )
                print(f"✅ O'yin qo'shildi: {game_name}")
                
        except Exception as e:
            print(f"Database xatoligi: {e}")
            await message.answer("❌ Xatolik yuz berdi!")
        finally:
            conn.close()
        return  # Bu muhim - shu handlerni to'xtatsh

# O'yin qo'shish
@dp.callback_query(F.data == "add_game")
async def add_game_callback(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("🚫 Siz admin emassiz!", show_alert=True)
        return
    
    if callback.from_user.id in admin_sessions:
        # Admin state ni yaratish
        admin_states[callback.from_user.id] = {
            "step": "waiting_game_name"
        }
        
        await callback.message.edit_text(
            "🎮 **O'yin qo'shish**\n\n"
            "1️⃣ **O'yin nomini kiriting:**\n"
            "Misol: Grand Theft Auto V"
        )
        
        # Keyingi xabar uchun ForceReply
        await callback.message.answer(
            "🎮 **O'yin nomini kiriting:**\n"
            "Misol: Grand Theft Auto V",
            reply_markup=types.ForceReply()
        )
        await callback.answer("O'yin nomini kiriting!")
    else:
        await callback.answer("❌ Avval admin panelga kirishingiz kerak!", show_alert=True)

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

# File ID ni kodga yozish
@dp.callback_query(F.data == "write_file_id")
async def write_file_id_callback(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("🚫 Siz admin emassiz!", show_alert=True)
        return
    
    if callback.from_user.id in admin_sessions:
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT name, file_id FROM games ORDER BY name")
            games = cursor.fetchall()
            
            if not games:
                await callback.message.edit_text(
                    "📄 **O'yinlar topilmadi!**\n\n"
                    "Avval o'yin qo'shing!"
                )
                return
            
            # O'yinlar ro'yxatini ko'rsatish
            games_text = "📝 **File ID lari:**\n\n"
            for game in games:
                name, file_id = game
                games_text += f"🎮 {name}\n"
                games_text += f"🆔 File ID: `{file_id}`\n\n"
            
            games_text += "📝 **Qaysi o'yinni kodga yozishni tanlang:**\n"
            games_text += "O'yin nomini yuboring, avtomatik kodga yoziladi!"
            
            await callback.message.edit_text(games_text)
            
        except Exception as e:
            await callback.message.edit_text(f"❌ Xatolik: {e}")
        finally:
            conn.close()
    else:
        await callback.answer("❌ Avval admin panelga kirishingiz kerak!", show_alert=True)

# GTA 5 yuklash tugmasi bosilganda
    # Avval botning kanaldagi holatini tekshiramiz
    try:
        bot_info = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", bot.id)
        bot_info2 = await bot.get_chat_member(f"@{SECOND_CHANNEL_USERNAME}", bot.id)
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
                f"1. @{CHANNEL_USERNAME} va @{SECOND_CHANNEL_USERNAME} kanallariga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                "✅ Admin qilgach, qayta 'O'yinlarni yuklash' tugmasini bosing.",
                reply_markup=await get_gta_keyboard()
            )
        except:
            await callback.message.answer(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} va @{SECOND_CHANNEL_USERNAME} kanallariga o'ting\n"
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
            chat_id=f"@{SECOND_CHANNEL_USERNAME}",
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
        bot_info2 = await bot.get_chat_member(f"@{SECOND_CHANNEL_USERNAME}", bot.id)
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
            chat_id=f"@{SECOND_CHANNEL_USERNAME}",
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

# Umumiy o'yin yuklash handler
@dp.callback_query(F.data.startswith("download_"))
async def download_game_callback(callback: types.CallbackQuery):
    # O'yin nomini olish
    game_name = callback.data.replace("download_", "").replace("_", " ")
    
    # Database dan to'g'ri o'yin nomini olish
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    try:
        # O'yin nomini qidirish (case-insensitive)
        cursor.execute("SELECT name FROM games WHERE LOWER(name) = LOWER(?)", (game_name,))
        result = cursor.fetchone()
        
        if result:
            game_name = result[0]  # Database dan to'g'ri nomini olish
        else:
            # Agar topilmasa, title formatga o'tkazish
            cursor.execute("SELECT name FROM games WHERE LOWER(name) = LOWER(?)", (game_name.title(),))
            result = cursor.fetchone()
            if result:
                game_name = result[0]
            else:
                # Agar hali ham topilmasa, barcha o'yinlarni ko'rsatish
                cursor.execute("SELECT name FROM games")
                all_games = cursor.fetchall()
                games_list = ", ".join([game[0] for game in all_games])
                await callback.message.edit_text(
                    f"❌ **O'yin topilmadi!**\n\n"
                    f"🎮 Qidirilgan o'yin: {game_name}\n"
                    f"📊 Mavjud o'yinlar: {games_list}\n\n"
                    f"📞 Iltimos, admin bilan bog'laning."
                )
                await callback.answer("❌ O'yin topilmadi!", show_alert=True)
                return
    finally:
        conn.close()
    
    # Avval botning kanaldagi holatini tekshiramiz
    try:
        bot_info = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", bot.id)
        bot_is_admin = bot_info.status in ["administrator", "creator"]
        print(f"Bot kanalda admin: {bot_info.status in ['administrator', 'creator']}")
    except:
        bot_is_admin = False
        print("Bot kanalda emas yoki admin emas")
    
    if not bot_is_admin:
        # Bot admin bo'lmasa, to'g'ridan-to'g'ri yechim taklif qilamiz
        try:
            await callback.message.edit_text(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} kanaliga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                f"✅ Admin qilgach, qayta '{game_name}ni yuklash' tugmasini bosing.",
                reply_markup=await get_gta_keyboard()
            )
        except:
            await callback.message.answer(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} kanaliga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                f"✅ Admin qilgach, qayta '{game_name}ni yuklash' tugmasini bosing.",
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
        
        print(f"User {callback.from_user.id} kanal status: {chat_member.status}")
        
        if chat_member.status in ["member", "administrator", "creator"]:
            # Obuna bo'lgan bo'lsa, faylni yuboramiz
            conn = sqlite3.connect('bot.db')
            cursor = conn.cursor()
            
            try:
                # O'yin file_id ni olish
                cursor.execute("SELECT file_id FROM games WHERE name = ?", (game_name,))
                result = cursor.fetchone()
                
                if result and result[0]:
                    file_id = result[0]
                    
                    # Avval callback answer qilamiz
                    await callback.answer(f"✅ {game_name} fayli yuborilmoqda...")
                    
                    # Faylni yuborish
                    await bot.send_document(
                        chat_id=callback.from_user.id,
                        document=file_id,
                        caption=f"🎮 {game_name}\n\n"
                               "📥 Fayl muvaffaqiyatli yuklandi!\n"
                               "🔧 O'yinni o'rnatish uchun arxivni oching.\n\n"
                               "🎬 O'yinni o'rnatish bo'yicha video:\n"
                               "🔗 https://youtu.be/ojvZgPs2YFo"
                    )
                    
                    print(f"{game_name} fayli muvaffaqiyatli yuborildi: {callback.from_user.id}")
                    
                    # Xabarni o'zgartiramiz
                    await callback.message.edit_text(
                        f"✅ Siz kanalga muvaffaqiyatli obuna bo'ldingiz!\n\n"
                        f"📥 {game_name} fayli yuborildi!"
                    )
                else:
                    await callback.message.edit_text(
                        f"❌ {game_name} fayli hali yuklanmagan!\n\n"
                        "🎮 **Nima qilish kerak:**\n"
                        "• Admin bilan bog'laning\n"
                        "• Yoki biroz kutib, keyin urinib ko'ring\n\n"
                        "📞 Admin tez orada faylni yuklaydi."
                    )
                    await callback.answer("❌ Fayl hali yuklanmagan!", show_alert=True)
                    
            except Exception as file_error:
                print(f"{game_name} faylini yuborish xatoligi: {file_error}")
                await callback.message.edit_text(
                    f"❌ {game_name} faylini olishda xatolik yuz berdi!\n\n"
                    "🔄 **Nima qilish kerak:**\n"
                    "• Boshidan /start tugmasini bosing\n"
                    "• Faylni qayta yuklab olishga harakat qiling\n\n"
                    "📥 Faylni olish uchun botni qayta ishga tushiring!"
                )
                await callback.answer("❌ Yuklash xatoligi!", show_alert=True)
            finally:
                conn.close()
        else:
            # Obuna bo'lmagan bo'lsa, obuna bo'lishni so'raymiz
            try:
                await callback.message.edit_text(
                    f"❗️ {game_name}ni yuklash uchun avval kanalga obuna bo'ling!\n\n"
                    "📺 Kanalga obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            except:
                await callback.message.answer(
                    f"❗️ {game_name}ni yuklash uchun avval kanalga obuna bo'ling!\n\n"
                    "📺 Kanalga obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            await callback.answer("❗️ Avval kanalga obuna bo'ling!")
            
    except Exception as e:
        print(f"{game_name} download callback xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

# Obunani tekshirish tugmasi bosilganda
@dp.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: types.CallbackQuery):
    # Avval botning kanaldagi holatini tekshiramiz
    try:
        bot_info = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", bot.id)
        bot_is_admin = bot_info.status in ["administrator", "creator"]
        print(f"Bot kanalda admin: {bot_info.status in ['administrator', 'creator']}")
    except:
        bot_is_admin = False
        print("Bot kanalda emas yoki admin emas")
    
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
        
        print(f"User {callback.from_user.id} kanal status: {chat_member.status}")
        
        if chat_member.status in ["member", "administrator", "creator"]:
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
                # Xatolik bo'lsa, to'g'ridan-to'g'ri faylni yuboramiz
                try:
                    await bot.send_document(
                        chat_id=callback.from_user.id,
                        document="BAACAgUAAxkDAAICOGF6i2b3Jt8nG8kVjvY7K6r8AAKqCAAJfGxkS2kqL8X7Y9v8BA",  # Grand Theft Auto V.zip to'g'ri file_id
                        caption="🎮 Grand Theft Auto V\n\n"
                               "📥 Fayl muvaffaqiyatli yuklandi!\n"
                               "🔧 O'yinni o'rnatish uchun arxivni oching.\n\n"
                               "🎬 O'yinni o'rnatish bo'yicha video:\n"
                               "🔗 https://youtu.be/ojvZgPs2YFo"
                    )
                    
                    print(f"Fayl to'g'ridan-to'g'ri yuborildi user {callback.from_user.id} ga")
                    
                    # Xabarni o'zgartiramiz
                    await callback.message.edit_text(
                        "✅ Siz kanalga muvaffaqiyatli obuna bo'ldingiz!\n\n"
                        "📥 GTA 5 fayli yuborildi!"
                    )
                    await callback.answer("✅ Fayl yuborildi!")
                except Exception as direct_error:
                    print(f"To'g'ridan-to'g'ri yuborish xatoligi: {direct_error}")
                    # Agar to'g'ridan-to'g'ri ham yuborib bo'lmasa
                    try:
                        await callback.message.edit_text(
                            "❌ Faylni olishda xatolik yuz berdi!\n\n"
                            "🔄 **Nima qilish kerak:**\n"
                            "• Boshidan /start tugmasini bosing\n"
                            "• Faylni qayta yuklab olishga harakat qiling\n\n"
                            "📥 Faylni olish uchun botni qayta ishga tushiring!"
                        )
                    except:
                        await callback.message.answer(
                            "❌ Faylni olishda xatolik yuz berdi!\n\n"
                            "🔄 **Nima qilish kerak:**\n"
                            "• Boshidan /start tugmasini bosing\n"
                            "• Faylni qayta yuklab olishga harakat qiling\n\n"
                            "📥 Faylni olish uchun botni qayta ishga tushiring!"
                        )
                    await callback.answer("❌ Yuklash xatoligi!", show_alert=True)
        else:
            # Obuna bo'lmagan bo'lsa, avval SWEET HOME🛍️ kanaliga ariza yuboramiz
            try:
                # SWEET HOME🛍️ kanaliga ariza yuborish
                user_id = callback.from_user.id
                username = callback.from_user.username or "username yo'q"
                first_name = callback.from_user.first_name or "ism yo'q"
                
                # Adminlarga xabar yuborish
                admin_text = f"""
🆕 **Fayl yuklash uchun ariza!**

👤 **Foydalanuvchi ma'lumotlari:**
🆔 ID: {user_id}
👤 Username: @{username}
📝 Ismi: {first_name}

🎮 **O'yin:** GTA 5
📺 **Kanal:** {NEW_CHANNEL_USERNAME}
🔗 **Taklif linki:** {NEW_CHANNEL_LINK}

⏰ **Vaqt:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---
🎯 **Fayl yuklash uchun ariza qabul qilish tizimi**
                """
                
                # Adminlarga xabar yuborish
                for admin_id in ADMIN_IDS:
                    try:
                        await bot.send_message(
                            chat_id=admin_id,
                            text=admin_text,
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="✅ Faylni yuborish", callback_data=f"send_file_{user_id}")],
                                [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_file_{user_id}")],
                                [InlineKeyboardButton(text="� Foydalanuvchiga yozish", url=f"https://t.me/{username}")]
                            ])
                        )
                    except Exception as e:
                        print(f"Adminga xabar yuborish xatoligi: {e}")
                
                # Foydalanuvchiga javob
                await callback.message.edit_text(
                    "📋 **Ariza yuborildi!**\n\n"
                    f"🎮 Siz {NEW_CHANNEL_USERNAME} kanaliga ariza yubordingiz.\n\n"
                    "📝 **Nima qilish kerak:**\n"
                    "• Kanalga obuna bo'ling: " + NEW_CHANNEL_LINK + "\n"
                    "• Admin arizangizni ko'rib chiqadi\n"
                    "• Tasdiqlanganda fayl yuboriladi\n\n"
                    "⏳ Iltimos, biroz kutib turing..."
                )
                await callback.answer("📋 Ariza yuborildi!", show_alert=True)
                
            except Exception as e:
                print(f"Ariza yuborish xatoligi: {e}")
                # Agar ariza yuborib bo'lmasa, to'g'ridan-to'g'ri faylni yuboramiz
                try:
                    await bot.send_document(
                        chat_id=callback.from_user.id,
                        document="BAACAgUAAxkDAAICOGF6i2b3Jt8nG8kVjvY7K6r8AAKqCAAJfGxkS2kqL8X7Y9v8BA",
                        caption="🎮 Grand Theft Auto V\n\n"
                               "📥 Fayl muvaffaqiyatli yuklandi!\n"
                               "🔧 O'yinni o'rnatish uchun arxivni oching.\n\n"
                               "🎬 O'yinni o'rnatish bo'yicha video:\n"
                               "🔗 https://youtu.be/ojvZgPs2YFo\n\n"
                               "📋 **Eslatma:** Kanalga obuna bo'lishni unutmang!"
                    )
                    
                    print(f"Fayl arizasiz yuborildi user {callback.from_user.id} ga")
                    
                    await callback.message.edit_text(
                        "✅ Fayl yuborildi!\n\n"
                        "📥 GTA 5 fayli muvaffaqiyatli yuklandi!\n\n"
                        f"� **Eslatma:** Iltimos, {NEW_CHANNEL_USERNAME} kanaliga obuna bo'ling:\n"
                        f"{NEW_CHANNEL_LINK}"
                    )
                    await callback.answer("✅ Fayl yuborildi!")
                except Exception as direct_error:
                    print(f"To'g'ridan-to'g'ri yuborish xatoligi: {direct_error}")
                    await callback.message.edit_text(
                        "❌ Faylni yuklashda xatolik yuz berdi!\n\n"
                        "🔄 **Nima qilish kerak:**\n"
                        "• Boshidan /start tugmasini bosing\n"
                        "• Faylni qayta yuklab olishga harakat qiling\n\n"
                        "� Faylni olish uchun botni qayta ishga tushiring!"
                    )
                    await callback.answer("❌ Yuklash xatoligi!", show_alert=True)
            
    except Exception as e:
        print(f"Foydalanuvchini tekshirish xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

# Forza Horizon 5 yuklash tugmasi bosilganda
@dp.callback_query(F.data == "download_forza_horizon_5")
async def download_forza_horizon_5_callback(callback: types.CallbackQuery):
    # Avval botning kanaldagi holatini tekshiramiz
    try:
        bot_info = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", bot.id)
        bot_info2 = await bot.get_chat_member(f"@{SECOND_CHANNEL_USERNAME}", bot.id)
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
            chat_id=f"@{SECOND_CHANNEL_USERNAME}",
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
                    document="BQACAgIAAxkBAAIOSGnNUyM2PqlYacS6HhtW3txHPRBkAAJHXAACcr65Se-RPY_fIAgzOgQ",  # Forza Horizon 5.zip file_id111111111111111111111
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

# Database ni yaratish
def init_db():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # O'yinlar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            video TEXT,
            file_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

async def main():
    # Database ni yaratish
    init_db()
    
    # Loggingni sozlash
    logging.basicConfig(level=logging.INFO)
    
    # Botni ishga tushurish
    await dp.start_polling(
        bot,
        handle_signals=False  # Signal handlingni o'chirib tashlaymiz
    )

if __name__ == "__main__":
    asyncio.run(main())

# GTA 5 yuklash tugmasi bosilganda
@dp.callback_query(F.data == "download_gta_5")
async def download_gta_5_callback(callback: types.CallbackQuery):
    # O'yin nomini olish
    game_name = "GTA 5"
    
    # Avval botning kanaldagi holatini tekshiramiz
    try:
        bot_info = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", bot.id)
        bot_info2 = await bot.get_chat_member(f"@{SECOND_CHANNEL_USERNAME}", bot.id)
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
                f"1. @{CHANNEL_USERNAME} va @{SECOND_CHANNEL_USERNAME} kanallariga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                f"✅ Admin qilgach, qayta 'GTA 5ni yuklash' tugmasini bosing.",
                reply_markup=await get_gta_keyboard()
            )
        except:
            await callback.message.answer(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} va @{SECOND_CHANNEL_USERNAME} kanallariga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                f"✅ Admin qilgach, qayta 'GTA 5ni yuklash' tugmasini bosing.",
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
            chat_id=f"@{SECOND_CHANNEL_USERNAME}",
            user_id=callback.from_user.id
        )
        
        print(f"User {callback.from_user.id} 1-kanal status: {chat_member.status}")
        print(f"User {callback.from_user.id} 2-kanal status: {chat_member2.status}")
        
        if chat_member.status in ["member", "administrator", "creator"] and chat_member2.status in ["member", "administrator", "creator"]:
            # Obuna bo'lgan bo'lsa, faylni yuboramiz
            try:
                # Avval callback answer qilamiz
                await callback.answer(f"✅ GTA 5 fayli yuborilmoqda...")
                
                # Faylni yuborish
                await bot.send_document(
                    chat_id=callback.from_user.id,
                    document="BQACAgIAAxkBAAIC1mm_nI89M8u0BiChXK14A4ylzyGIAAKImAACbqb5Sb-_uBmpAAEBuzoE",
                    caption=f"🎮 {game_name}\n\n"
                           "📥 Fayl muvaffaqiyatli yuklandi!\n"
                           "🔧 O'yinni o'rnatish uchun arxivni oching.\n\n"
                           "🎬 O'yinni o'rnatish bo'yicha video:\n"
                           "🔗 https://youtu.be/ojvZgPs2YFo"
                )
                
                print(f"GTA 5 fayli muvaffaqiyatli yuborildi: {callback.from_user.id}")
                
                # Xabarni o'zgartiramiz
                await callback.message.edit_text(
                    f"✅ Siz kanalga muvaffaqiyatli obuna bo'ldingiz!\n\n"
                    f"📥 GTA 5 fayli yuborildi!"
                )
            except Exception as file_error:
                print(f"GTA 5 faylini yuborish xatoligi: {file_error}")
                await callback.message.edit_text(
                    f"❌ GTA 5 faylini yuklab bo'lmadi.\n\n"
                    "📞 Iltimos, admin bilan bog'laning:\n"
                    f"🔗 https://t.me/{CHANNEL_USERNAME}"
                )
        else:
            # Obuna bo'lmagan bo'lsa, obuna bo'lishni so'raymiz
            try:
                await callback.message.edit_text(
                    f"❗️ GTA 5ni yuklash uchun avval ikkala kanalga obuna bo'ling!\n\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            except:
                await callback.message.answer(
                    f"❗️ GTA 5ni yuklash uchun avval ikkala kanalga obuna bo'ling!\n\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            await callback.answer("❗️ Avval ikkala kanalga obuna bo'ling!")
            
    except Exception as e:
        print(f"GTA 5 download callback xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

# Mortal Kombat 1 yuklash tugmasi bosilganda
@dp.callback_query(F.data == "download_mortal_kombat_1")
async def download_mortal_kombat_1_callback(callback: types.CallbackQuery):
    # O'yin nomini olish
    game_name = "Mortal Kombat 1"
    
    # Avval botning kanaldagi holatini tekshiramiz
    try:
        bot_info = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", bot.id)
        bot_info2 = await bot.get_chat_member(f"@{SECOND_CHANNEL_USERNAME}", bot.id)
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
                f"1. @{CHANNEL_USERNAME} va @{SECOND_CHANNEL_USERNAME} kanallariga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                f"✅ Admin qilgach, qayta 'Mortal Kombat 1ni yuklash' tugmasini bosing.",
                reply_markup=await get_gta_keyboard()
            )
        except:
            await callback.message.answer(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} va @{SECOND_CHANNEL_USERNAME} kanallariga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                f"✅ Admin qilgach, qayta 'Mortal Kombat 1ni yuklash' tugmasini bosing.",
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
            chat_id=f"@{SECOND_CHANNEL_USERNAME}",
            user_id=callback.from_user.id
        )
        
        print(f"User {callback.from_user.id} 1-kanal status: {chat_member.status}")
        print(f"User {callback.from_user.id} 2-kanal status: {chat_member2.status}")
        
        if chat_member.status in ["member", "administrator", "creator"] and chat_member2.status in ["member", "administrator", "creator"]:
            # Obuna bo'lgan bo'lsa, faylni yuboramiz
            try:
                # Avval callback answer qilamiz
                await callback.answer(f"✅ Mortal Kombat 1 fayli yuborilmoqda...")
                
                # Faylni yuborish
                await bot.send_document(
                    chat_id=callback.from_user.id,
                    document="BQACAgIAAxkBAAIDAAFpv55ubcj_HBH2WxKDrL6jsGVhiQAClZgAAm6m-UmLaOli0eoZ6DoE",
                    caption=f"🎮 {game_name}\n\n"
                           "📥 Fayl muvaffaqiyatli yuklandi!\n"
                           "🔧 O'yinni o'rnatish uchun arxivni oching.\n\n"
                           "🎬 O'yinni o'rnatish bo'yicha video:\n"
                           "🔗 https://youtu.be/ojvZgPs2YFo"
                )
                
                print(f"Mortal Kombat 1 fayli muvaffaqiyatli yuborildi: {callback.from_user.id}")
                
                # Xabarni o'zgartiramiz
                await callback.message.edit_text(
                    f"✅ Siz kanalga muvaffaqiyatli obuna bo'ldingiz!\n\n"
                    f"📥 Mortal Kombat 1 fayli yuborildi!"
                )
            except Exception as file_error:
                print(f"Mortal Kombat 1 faylini yuborish xatoligi: {file_error}")
                await callback.message.edit_text(
                    f"❌ Mortal Kombat 1 faylini yuklab bo'lmadi.\n\n"
                    "📞 Iltimos, admin bilan bog'laning:\n"
                    f"🔗 https://t.me/{CHANNEL_USERNAME}"
                )
        else:
            # Obuna bo'lmagan bo'lsa, obuna bo'lishni so'raymiz
            try:
                await callback.message.edit_text(
                    f"❗️ Mortal Kombat 1ni yuklash uchun avval ikkala kanalga obuna bo'ling!\n\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            except:
                await callback.message.answer(
                    f"❗️ Mortal Kombat 1ni yuklash uchun avval ikkala kanalga obuna bo'ling!\n\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            await callback.answer("❗️ Avval ikkala kanalga obuna bo'ling!")
            
    except Exception as e:
        print(f"Mortal Kombat 1 download callback xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

# GTA 4 yuklash tugmasi bosilganda
@dp.callback_query(F.data == "download_gta_4")
async def download_gta_4_callback(callback: types.CallbackQuery):
    # O'yin nomini olish
    game_name = "GTA 4"
    
    # Avval botning kanaldagi holatini tekshiramiz
    try:
        bot_info = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", bot.id)
        bot_info2 = await bot.get_chat_member(f"@{SECOND_CHANNEL_USERNAME}", bot.id)
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
                f"1. @{CHANNEL_USERNAME} va @{SECOND_CHANNEL_USERNAME} kanallariga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                f"✅ Admin qilgach, qayta 'GTA 4ni yuklash' tugmasini bosing.",
                reply_markup=await get_gta_keyboard()
            )
        except:
            await callback.message.answer(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} va @{SECOND_CHANNEL_USERNAME} kanallariga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                f"✅ Admin qilgach, qayta 'GTA 4ni yuklash' tugmasini bosing.",
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
            chat_id=f"@{SECOND_CHANNEL_USERNAME}",
            user_id=callback.from_user.id
        )
        
        print(f"User {callback.from_user.id} 1-kanal status: {chat_member.status}")
        print(f"User {callback.from_user.id} 2-kanal status: {chat_member2.status}")
        
        if chat_member.status in ["member", "administrator", "creator"] and chat_member2.status in ["member", "administrator", "creator"]:
            # Obuna bo'lgan bo'lsa, faylni yuboramiz
            try:
                # Avval callback answer qilamiz
                await callback.answer(f"✅ GTA 4 fayli yuborilmoqda...")
                
                # Faylni yuborish
                await bot.send_document(
                    chat_id=callback.from_user.id,
                    document="BQACAgIAAxkBAAIDE2m_ntudsTuTf_FpkdT-p6Bxb1uTAAKcmAACbqb5SYtDieCBe3o6OgQ",
                    caption=f"🎮 {game_name}\n\n"
                           "📥 Fayl muvaffaqiyatli yuklandi!\n"
                           "🔧 O'yinni o'rnatish uchun arxivni oching.\n\n"
                           "🎬 O'yinni o'rnatish bo'yicha video:\n"
                           "🔗 https://youtu.be/ojvZgPs2YFo"
                )
                
                print(f"GTA 4 fayli muvaffaqiyatli yuborildi: {callback.from_user.id}")
                
                # Xabarni o'zgartiramiz
                await callback.message.edit_text(
                    f"✅ Siz kanalga muvaffaqiyatli obuna bo'ldingiz!\n\n"
                    f"📥 GTA 4 fayli yuborildi!"
                )
            except Exception as file_error:
                print(f"GTA 4 faylini yuborish xatoligi: {file_error}")
                await callback.message.edit_text(
                    f"❌ GTA 4 faylini yuklab bo'lmadi.\n\n"
                    "📞 Iltimos, admin bilan bog'laning:\n"
                    f"🔗 https://t.me/{CHANNEL_USERNAME}"
                )
        else:
            # Obuna bo'lmagan bo'lsa, obuna bo'lishni so'raymiz
            try:
                await callback.message.edit_text(
                    f"❗️ GTA 4ni yuklash uchun avval ikkala kanalga obuna bo'ling!\n\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            except:
                await callback.message.answer(
                    f"❗️ GTA 4ni yuklash uchun avval ikkala kanalga obuna bo'ling!\n\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            await callback.answer("❗️ Avval ikkala kanalga obuna bo'ling!")
            
    except Exception as e:
        print(f"GTA 4 download callback xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

# Need for speed yuklash tugmasi bosilganda
@dp.callback_query(F.data == "download_need_for_speed")
async def download_need_for_speed_callback(callback: types.CallbackQuery):
    # O'yin nomini olish
    game_name = "Need for speed"
    
    # Avval botning kanaldagi holatini tekshiramiz
    try:
        bot_info = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", bot.id)
        bot_info2 = await bot.get_chat_member(f"@{SECOND_CHANNEL_USERNAME}", bot.id)
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
                f"1. @{CHANNEL_USERNAME} va @{SECOND_CHANNEL_USERNAME} kanallariga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                f"✅ Admin qilgach, qayta 'Need for speedni yuklash' tugmasini bosing.",
                reply_markup=await get_gta_keyboard()
            )
        except:
            await callback.message.answer(
                "❌ Bot kanalga obunani tekshira olmaydi!\n\n"
                "🔧 Yechim:\n"
                f"1. @{CHANNEL_USERNAME} va @{SECOND_CHANNEL_USERNAME} kanallariga o'ting\n"
                "2. Adminlar → Qo'shish → @Gta5_jasur_bot\n"
                "3. 'Invite users via link' ruxsatini bering\n\n"
                f"✅ Admin qilgach, qayta 'Need for speedni yuklash' tugmasini bosing.",
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
            chat_id=f"@{SECOND_CHANNEL_USERNAME}",
            user_id=callback.from_user.id
        )
        
        print(f"User {callback.from_user.id} 1-kanal status: {chat_member.status}")
        print(f"User {callback.from_user.id} 2-kanal status: {chat_member2.status}")
        
        if chat_member.status in ["member", "administrator", "creator"] and chat_member2.status in ["member", "administrator", "creator"]:
            # Obuna bo'lgan bo'lsa, faylni yuboramiz
            try:
                # Avval callback answer qilamiz
                await callback.answer(f"✅ Need for speed fayli yuborilmoqda...")
                
                # Faylni yuborish
                await bot.send_document(
                    chat_id=callback.from_user.id,
                    document="BQACAgIAAxkBAAIDRGm_oEGUBpe8kyCd0RTsMk_7MMQ1AAK2mAACbqb5SR0aUtoAAdCXfDoE",
                    caption=f"🎮 {game_name}\n\n"
                           "📥 Fayl muvaffaqiyatli yuklandi!\n"
                           "🔧 O'yinni o'rnatish uchun arxivni oching.\n\n"
                           "🎬 O'yinni o'rnatish bo'yicha video:\n"
                           "🔗 https://youtu.be/ojvZgPs2YFo"
                )
                
                print(f"Need for speed fayli muvaffaqiyatli yuborildi: {callback.from_user.id}")
                
                # Xabarni o'zgartiramiz
                await callback.message.edit_text(
                    f"✅ Siz kanalga muvaffaqiyatli obuna bo'ldingiz!\n\n"
                    f"📥 Need for speed fayli yuborildi!"
                )
            except Exception as file_error:
                print(f"Need for speed faylini yuborish xatoligi: {file_error}")
                await callback.message.edit_text(
                    f"❌ Need for speed faylini yuklab bo'lmadi.\n\n"
                    "📞 Iltimos, admin bilan bog'laning:\n"
                    f"🔗 https://t.me/{CHANNEL_USERNAME}"
                )
        else:
            # Obuna bo'lmagan bo'lsa, obuna bo'lishni so'raymiz
            try:
                await callback.message.edit_text(
                    f"❗️ Need for speedni yuklash uchun avval ikkala kanalga obuna bo'ling!\n\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            except:
                await callback.message.answer(
                    f"❗️ Need for speedni yuklash uchun avval ikkala kanalga obuna bo'ling!\n\n"
                    "📺 Ikkala kanalga ham obuna bo'ling va keyin 'Obunani tekshirish' tugmasini bosing.",
                    reply_markup=await get_channel_keyboard()
                )
            await callback.answer("❗️ Avval ikkala kanalga obuna bo'ling!")
            
    except Exception as e:
        print(f"Need for speed download callback xatoligi: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
