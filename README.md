# GTA 5 Telegram Bot

Bu bot - Telegram orqali GTA 5 o'yinini tarqatish uchun yaratilgan.

## O'rnatish

1. Python 3.8+ o'rnatilgan bo'lishi kerak
2. Kerakli kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

## Sozlash

1. `bot.py` faylini oching
2. `BOT_TOKEN` o'zgaruvchisiga o'zingizning bot tokeningizni kiriting
   - Tokenni @BotFather dan olishingiz mumkin
3. `CHANNEL_USERNAME` o'zgaruvchisiga kanal username'ini kiriting (@ belgisiz)

## Botni ishga tushurish

```bash
python bot.py
```

## Botning ishlash prinsipi

1. Foydalanuvchi `/start` komandasini yuboradi
2. Bot salomlaydi va "GTA 5ni yuklash" tugmasini ko'rsatadi
3. Foydalanuvchi tugmani bosganda, bot kanalga obuna bo'lishni tekshiradi
4. Agar obuna bo'lsa - fayl havolasini yuboradi
5. Agar obuna bo'lmasa - kanalga obuna bo'lishni so'raydi

## Muhim eslatmalar

- Bot kanalda admin bo'lishi kerak (obunani tekshirish uchun)
- Fayl havolasini o'zingizgartiring (`https://example.com/gta5-file`)
- Kanal username'ini to'g'ri kiriting
