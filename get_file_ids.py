import asyncio
from aiogram import Bot, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile

# Bot tokeningizni shu yerga kiriting
BOT_TOKEN = "8746729342:AAEvlijgD7w1bM9EogAv-WrM_SAOy6qggOg"

# Botni sozlash
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

async def upload_files():
    # Fayl yo'llari
    files_to_upload = [
        "Grand Theft Auto V.zip",
        "Mortal Kombat 1.zip"
    ]
    
    for file_path in files_to_upload:
        try:
            # Faylni yuborish
            document = FSInputFile(file_path)
            message = await bot.send_document(
                chat_id=1209491758,  # Admin ID
                document=document,
                caption=f"📁 {file_path} fayli yuklandi"
            )
            
            # File ID ni olish
            file_id = message.document.file_id
            print(f"✅ {file_path} file_id: {file_id}")
            
        except Exception as e:
            print(f"❌ {file_path} yuklashda xatolik: {e}")

if __name__ == "__main__":
    asyncio.run(upload_files())
