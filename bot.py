import os
import json
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi. Avval BOT_TOKEN environment variable ni sozlang.")

with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

# Har bir foydalanuvchining joriy testi shu yerda saqlanadi.
SESSIONS = {}

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 O‘rganish rejimi", callback_data="mode:study")],
        [InlineKeyboardButton("📝 Imtihon rejimi", callback_data="mode:exam")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Assalomu alaykum! 🌿\n\n"
        "«Turizmda sifat va xavfsizlik» fanidan test botiga xush kelibsiz.\n"
        f"Test bazasida {len(QUESTIONS)} ta savol mavjud.\n\n"
        "Rejimni tanlang:"
    )
    await update.message.reply_text(text, reply_markup=main_menu())

async def show_question(query, user_id):
    session = SESSIONS.get(user_id)
    if not session:
        await query.edit_message_text("Test sessiyasi topilmadi. /start buyrug‘ini bosing.")
        return

    # Test yakunlandi
    if session["index"] >= len(session["questions"]):
        total = session["scored"]
        correct = session["correct"]
        wrong = session["wrong"]
        skipped = session["unkeyed"]
        percent = round(correct / total * 100) if total else 0
        result = (
            "🏁 TEST YAKUNLANDI!\n\n"
            f"📊 Jami baholangan savollar: {total}\n"
            f"✅ To‘g‘ri: {correct}\n"
            f"❌ Noto‘g‘ri: {wrong}\n"
            f"⚪ Javob kaliti belgilanmagan: {skipped}\n"
            f"🎯 Natija: {percent}%\n\n"
            "Yana test ishlash uchun rejimni tanlang:"
        )
        await query.edit_message_text(result, reply_markup=main_menu())
        SESSIONS.pop(user_id, None)
        return

    q = session["questions"][session["index"]]
    session["current"] = q
    options = q["options"]
    correct_count = sum(1 for o in options if o["correct"])

    header = f"📘 Savol {session['index'] + 1}/{len(session['questions'])}\n\n{q['question']}"
    if correct_count == 0:
        header += "\n\n⚠️ PDF faylida bu savolning sariq bilan belgilangan javobi topilmadi. Bu savol natijaga qo‘shilmaydi."
    keyboard = [
        [InlineKeyboardButton(f"{chr(65+i)}. {o['text'][:75]}{'…' if len(o['text'])>75 else ''}",
                              callback_data=f"answer:{i}")]
        for i, o in enumerate(options)
    ]
    await query.edit_message_text(header, reply_markup=InlineKeyboardMarkup(keyboard))

async def choose_mode(query, user_id, mode):
    qs = [dict(q) for q in QUESTIONS]
    random.shuffle(qs)
    for q in qs:
        q["options"] = [dict(o) for o in q["options"]]
        random.shuffle(q["options"])
    SESSIONS[user_id] = {
        "mode": mode,
        "questions": qs,
        "index": 0,
        "correct": 0,
        "wrong": 0,
        "unkeyed": 0,
        "scored": 0,
        "answered": False,
    }
    label = "O‘rganish" if mode == "study" else "Imtihon"
    await query.edit_message_text(f"✅ {label} rejimi boshlandi. Omad!")
    # Send first question as a new message
    await query.message.reply_text("Birinchi savol:", reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Boshlash ▶️", callback_data="next")]]
    ))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data or ""

    if data.startswith("mode:"):
        await choose_mode(query, user_id, data.split(":",1)[1])
        return

    if data == "next":
        await show_question(query, user_id)
        return

    if data.startswith("answer:"):
        session = SESSIONS.get(user_id)
        if not session or session.get("answered"):
            return
        q = session["current"]
        choice = int(data.split(":")[1])
        selected = q["options"][choice]
        correct_options = [o for o in q["options"] if o["correct"]]
        session["answered"] = True

        if not correct_options:
            session["unkeyed"] += 1
            feedback = "⚪ Bu savol uchun PDFda to‘g‘ri javob sariq bilan belgilanmagan. Natijaga qo‘shilmadi."
        else:
            session["scored"] += 1
            if selected["correct"]:
                session["correct"] += 1
                feedback = "✅ To‘g‘ri javob!"
            else:
                session["wrong"] += 1
                right = correct_options[0]["text"]
                feedback = f"❌ Noto‘g‘ri.\n\n✅ To‘g‘ri javob: {right}"

        if session["mode"] == "study":
            await query.edit_message_text(
                f"{q['question']}\n\nSizning javobingiz: {selected['text']}\n\n{feedback}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Keyingi savol ➡️", callback_data="continue")]])
            )
        else:
            # Imtihon rejimida javoblar yakunda ko‘rsatiladi.
            await query.edit_message_text(
                f"Javob qabul qilindi. ({session['index'] + 1}/{len(session['questions'])})",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Davom etish ➡️", callback_data="continue")]])
            )
        return

    if data == "continue":
        session = SESSIONS.get(user_id)
        if not session:
            await query.edit_message_text("Test sessiyasi tugagan. /start ni bosing.")
            return
        session["index"] += 1
        session["answered"] = False
        await show_question(query, user_id)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Botdan foydalanish:\n/start — testni boshlash\n"
        "O‘rganish rejimida har savoldan keyin javob ko‘rsatiladi.\n"
        "Imtihon rejimida natija test oxirida hisoblanadi."
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
