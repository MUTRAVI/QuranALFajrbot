import os
import random
import json
import asyncio
from datetime import datetime, timedelta
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes
from prayer_times_calculator import PrayerTimesCalculator
from flask import Flask
import threading

# 1. الإعدادات والروابط
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = "@AlFajr_Quran" 
OFFICIAL_CHANNEL_LINK = "https://t.me/QuranAlfajrOfficial"
DATA_FILE = "users_data.json"

# 2. الموسوعة الإسلامية
CONTENT_DB = {
    "MORNING": ["☀️ أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له."],
    "EVENING": ["🌙 أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له."],
    "QURAN": ["📖 ﴿وَقُل رَّبِّ زِدني عِلمًا﴾", "📖 ﴿إِنَّ مَعَ العُسرِ يُسرًا﴾"],
    "HADITH": ["💬 قال ﷺ: (خيركم من تعلم القرآن وعلمه)."],
    "TAFSIR": ["💡 تفسير: ﴿فَاذكُروني أَذكُركُم﴾ أي اذكروني بالطاعة أذكركم بالثواب."],
    "DUA": ["🤲 (يا مقلب القلوب ثبت قلبي على دينك)."]
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_user(chat_id):
    data = load_data()
    if str(chat_id) not in data:
        data[str(chat_id)] = {"tz": "Asia/Riyadh", "last_m": "", "last_e": ""}
        with open(DATA_FILE, "w") as f: json.dump(data, f)

# 4. وظيفة النشر التلقائي
async def daily_broadcast(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    tz_riyadh = pytz.timezone('Asia/Riyadh')
    now = datetime.now(tz_riyadh)
    today_str = str(now.date())
    
    calc = PrayerTimesCalculator(latitude=24.7136, longitude=46.6753, calculation_method='umm_al_qura', date=today_str)
    times = calc.fetch_prayer_times()
    fajr = datetime.strptime(times['Fajr'], '%H:%M').replace(year=now.year, month=now.month, day=now.day, tzinfo=tz_riyadh)
    maghrib = datetime.strptime(times['Maghrib'], '%H:%M').replace(year=now.year, month=now.month, day=now.day, tzinfo=tz_riyadh)

    # تجهيز الأزرار (مثل الصورة التي أرسلتها)
    bot_info = await context.bot.get_me()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 تفعيل البوت /start", url=f"https://t.me/{bot_info.username}?start=true")],
        [InlineKeyboardButton("📢 قناة البوت الرسمية", url=OFFICIAL_CHANNEL_LINK)]
    ])

    def get_msg(type_code):
        if type_code == "M":
            return f"✨ *رسالة الصباح:*\n\n🔹 {random.choice(CONTENT_DB['MORNING'])}\n\n🔹 {random.choice(CONTENT_DB['QURAN'])}\n\n🔹 {random.choice(CONTENT_DB['HADITH'])}"
        return f"✨ *رسالة المساء:*\n\n🔹 {random.choice(CONTENT_DB['EVENING'])}\n\n🔹 {random.choice(CONTENT_DB['TAFSIR'])}\n\n🔹 {random.choice(CONTENT_DB['DUA'])}"

    # النشر في القناة بالأزرار
    if now >= (fajr + timedelta(minutes=20)) and now < (fajr + timedelta(minutes=30)):
        try: await context.bot.send_message(chat_id=CHANNEL_ID, text=get_msg("M"), reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
        except: pass
    if now >= (maghrib - timedelta(minutes=20)) and now < (maghrib - timedelta(minutes=10)):
        try: await context.bot.send_message(chat_id=CHANNEL_ID, text=get_msg("E"), reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
        except: pass

    # النشر للخاص
    for chat_id, info in data.items():
        try:
            if now >= (fajr + timedelta(minutes=20)) and info.get('last_m') != today_str:
                await context.bot.send_message(chat_id=int(chat_id), text=get_msg("M"), parse_mode=ParseMode.MARKDOWN)
                info['last_m'] = today_str
            if now >= (maghrib - timedelta(minutes=20)) and info.get('last_e') != today_str:
                await context.bot.send_message(chat_id=int(chat_id), text=get_msg("E"), parse_mode=ParseMode.MARKDOWN)
                info['last_e'] = today_str
        except: continue
    
    with open(DATA_FILE, "w") as f: json.dump(data, f)

app = Flask(__name__)
@app.route('/')
def home(): return "Active"

def main():
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", lambda u, c: save_user(u.effective_chat.id)))
    application.job_queue.run_repeating(daily_broadcast, interval=120, first=10)
    application.run_polling()

if __name__ == '__main__':
    main()
    
