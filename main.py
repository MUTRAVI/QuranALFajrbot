import os
import random
import json
import asyncio
from datetime import datetime, timedelta
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from prayer_times_calculator import PrayerTimesCalculator
from flask import Flask
import threading

# 1. الإعدادات والروابط
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OFFICIAL_CHANNEL_LINK = "https://t.me/QuranAlfajrOfficial" 
DATA_FILE = "users_data.json"

CITIES = {
    "riyadh": {"name": "الرياض", "lat": 24.7136, "lon": 46.6753, "tz": "Asia/Riyadh"},
    "makkah": {"name": "مكة المكرمة", "lat": 21.4225, "lon": 39.8262, "tz": "Asia/Riyadh"},
    "kuwait": {"name": "الكويت", "lat": 29.3759, "lon": 47.9774, "tz": "Asia/Kuwait"},
    "cairo": {"name": "القاهرة", "lat": 30.0444, "lon": 31.2357, "tz": "Africa/Cairo"}
}

CONTENT_DB = {
    "MORNING": ["☀️ أصبحنا وأصبح الملك لله، والحمد لله."],
    "EVENING": ["🌙 أمسينا وأمسى الملك لله، والحمد لله."],
    "QURAN": ["📖 ﴿وَقُل رَّبِّ زِدني عِلمًا﴾"],
    "DUA": ["🤲 (يا مقلب القلوب ثبت قلبي على دينك)."]
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

# 3. واجهة اختيار المدينة
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    cities_list = list(CITIES.items())
    for i in range(0, len(cities_list), 2):
        row = [InlineKeyboardButton(cities_list[i][1]["name"], callback_data=f"set_{cities_list[i][0]}")]
        if i + 1 < len(cities_list):
            row.append(InlineKeyboardButton(cities_list[i+1][1]["name"], callback_data=f"set_{cities_list[i+1][0]}"))
        keyboard.append(row)
    
    await update.message.reply_text(
        "**مرحباً بك في بوت قرآن الفجر** 🌿\n\nيرجى اختيار مدينتك لضبط المواقيت بدقة:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def city_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city_code = query.data.split("_")[1]
    chat_id = str(query.message.chat_id)
    
    data = load_data()
    data[chat_id] = {
        "lat": CITIES[city_code]['lat'],
        "lon": CITIES[city_code]['lon'],
        "tz": CITIES[city_code]['tz'],
        "last_m": "", "last_e": ""
    }
    save_data(data)
    
    bot_info = await query.bot.get_me()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 تفعيل البوت /start", url=f"https://t.me/{bot_info.username}?start=true")],
        [InlineKeyboardButton("📢 قناة قرآن الفجر", url=OFFICIAL_CHANNEL_LINK)]
    ])
    
    await query.edit_message_text(
        f"✅ تم ضبط التوقيت حسب مدينة (**{CITIES[city_code]['name']}**)\n\nستصلك الرسائل في وقتها الصحيح بإذن الله.",
        reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
    )

# 4. النشر التلقائي
async def daily_broadcast(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    updated = False
    for chat_id, info in data.items():
        try:
            user_tz = pytz.timezone(info.get('tz', 'Asia/Riyadh'))
            now = datetime.now(user_tz)
            calc = PrayerTimesCalculator(latitude=info['lat'], longitude=info['lon'], calculation_method='umm_al_qura', date=str(now.date()))
            times = calc.fetch_prayer_times()
            fajr = datetime.strptime(times['Fajr'], '%H:%M').replace(year=now.year, month=now.month, day=now.day, tzinfo=user_tz)
            maghrib = datetime.strptime(times['Maghrib'], '%H:%M').replace(year=now.year, month=now.month, day=now.day, tzinfo=user_tz)

            if now >= (fajr + timedelta(minutes=20)) and info.get('last_m') != str(now.date()):
                await context.bot.send_message(chat_id=int(chat_id), text=f"✨ *رسالة الصباح:*\n\n🔹 {random.choice(CONTENT_DB['MORNING'])}\n\n🔹 {random.choice(CONTENT_DB['QURAN'])}", parse_mode=ParseMode.MARKDOWN)
                info['last_m'] = str(now.date()); updated = True
            
            if now >= (maghrib - timedelta(minutes=20)) and info.get('last_e') != str(now.date()):
                await context.bot.send_message(chat_id=int(chat_id), text=f"✨ *رسالة المساء:*\n\n🔹 {random.choice(CONTENT_DB['EVENING'])}\n\n🔹 {random.choice(CONTENT_DB['DUA'])}", parse_mode=ParseMode.MARKDOWN)
                info['last_e'] = str(now.date()); updated = True
        except: continue
    if updated: save_data(data)

app = Flask(__name__)
@app.route('/')
def home(): return "Active"

def main():
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(city_callback, pattern="^set_"))
    application.job_queue.run_repeating(daily_broadcast, interval=300, first=10)
    application.run_polling()

if __name__ == '__main__':
    main()
