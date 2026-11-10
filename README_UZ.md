# Turizmda sifat va xavfsizlik — Telegram test bot

## Tayyorlangan baza
- PDFdagi 304 ta savol raqami tekshirildi.
- 303 ta savolda 4 ta javob varianti mavjud.
- 149- va 153-savollarda PDFda sariq bilan belgilangan to‘g‘ri javob yo‘q. Ular botda baholanmaydi.
- 216-savolda PDFda javob variantlari umuman yo‘q. Shu sababli u test bazasiga kiritilmadi.
- Boshqa savollarda sariq bilan belgilangan javoblar to‘g‘ri javob sifatida olindi.

## Botni ishga tushirish
1. Telegramda `@BotFather` ga kiring.
2. `/newbot` yuboring va bot nomi hamda username tanlang.
3. BotFather bergan tokenni maxfiy saqlang.
4. Python 3.10+ o‘rnating.
5. Ushbu papkada terminal ochib quyidagilarni bajaring:

```bash
pip install -r requirements.txt
```

6. Tokenni environment variable sifatida kiriting:

Windows PowerShell:
```powershell
$env:BOT_TOKEN="BOTFATHER_TOKEN"
python bot.py
```

macOS / Linux:
```bash
export BOT_TOKEN="BOTFATHER_TOKEN"
python bot.py
```

Bot ishlashi uchun `bot.py` va `questions.json` bir papkada bo‘lishi kerak.
Kompyuter/hosting ishlayotgan paytda bot faol bo‘ladi.

## Rejimlar
- O‘rganish: har savoldan keyin to‘g‘ri javob ko‘rsatiladi.
- Imtihon: javoblar yakunda hisoblanadi.
- Savollar va variantlar aralashtiriladi.
