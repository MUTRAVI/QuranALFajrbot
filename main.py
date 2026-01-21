import os
import random
import json
from datetime import datetime, timedelta
import pytz
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask
import threading
import asyncio

# 1. إعدادات البوت
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# ملف بسيط لحفظ أرقام القنوات والقروبات لكي لا تضيع
DATA_FILE = "chats_ids.json"

def load_chats():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return ["@quranalfajr"] # قناتك الأساسية

def save_chat(chat_id):
    chats = load_chats()
    if str(chat_id) not in [str(c) for c in chats]:
        chats.append(chat_id)
        with open(DATA_FILE, "w") as f: json.dump(chats, f)

# 2. المحتوى
QURAN_LIST = [
    {"v": "﴿وَسَارِعُوا إِلَىٰ مَغْفِرَةٍ مِّن رَّبِّكُمْ﴾", "t": "توجيه رباني بالمبادرة بالأعمال الصالحة."},
    {"v": "﴿إِنَّ مَعَ الْعُسْرِ يُسْرًا﴾", "t": "بشارة بأن كل ضيق سيعقبه فرج قريب."},
    {"v": "﴿لَئِن شَكَرْتُمْ لَأَزِيدَنَّكُمْ﴾", "t": "وعد من الله بزيادة النعم لمن يشكره."}
]
HADITH_LIST = [
    "قال ﷺ: (خَيْرُكُمْ مَنْ تَعَلَّمَ الْقُرْآنَ وَعَلَّمَهُ).",
    "قال ﷺ: (مَنْ صَلَّى عَلَيَّ صَلَاةً صَلَّى الله عَلَيْهِ بِهَا عَشْرًا)."
]

# 3. وظيفة النشر الجماعي العشوائي
async def broadcast_benefit():
    bot = Bot(token=TOKEN)
    chats = load_chats()
    
    choice = random.choice(['q', 'h'])
    if choice == 'q':
        item = random.choice(QURAN_LIST)
        msg = f"📖 *من آيات الذكر الحكيم:*\n\n{item['v']}\n\n💡 *التفسير:* {item['t']}"
    else:
        msg = f"✨ *حديث نبوي شريف:*\n\n{random.choice(HADITH_LIST)}"
    
    for chat_id in chats:
        try:
            await bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)
        except: continue

# 4. أوامر البوت للتفعيل التلقائي
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    save_chat(chat_id)
    await update.message.reply_text("تم تفعيل البوت بنجاح! سيتم النشر تلقائياً في هذا المكان (كل 30 دقيقة إلى 3 ساعات).")

# 5. تشغيل البوت والسيرفر
def run_flask():
    app = Flask(__name__)
    @app.route('/')
    def home(): return "Bot is Online"
    app.run(host='0.0.0.0', port=8080)

async def main():
    # تشغيل Flask في خيط منفصل
    threading.Thread(target=run_flask, daemon=True).start()
    
    # تشغيل البوت
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    # جدولة النشر التلقائي كل وقت عشوائي
    job_queue = application.job_queue
    def callback_wrapper(context):
        asyncio.create_task(broadcast_benefit())
        # إعادة جدولة الوقت العشوائي القادم
        next_time = random.randint(1800, 10800) # بين 30 و 180 دقيقة بالثواني
        job_queue.run_once(callback_wrapper, when=next_time)

    job_queue.run_once(callback_wrapper, when=120) # أول منشور بعد دقيقتين
    
    await application.initialize()
    await application.start_polling()
    await application.idle()

if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except: pass
