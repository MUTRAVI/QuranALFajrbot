import os
import random
import json
import asyncio
from datetime import datetime, timedelta
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from prayer_times_calculator import PrayerTimesCalculator
from flask import Flask
import threading

# تم وضع التوكن الخاص بك هنا مباشرة
TOKEN = "7674563071:AAGgszBWDJ72Yudm8_dTSgAukKIgi3-YUXg"

OFFICIAL_CHANNEL_LINK = "https://t.me/QuranAlfajrOfficial" 
DATA_FILE = "users_data.json"

CITIES = {
    "riyadh": {"name": "الرياض", "lat": 24.7136, "lon": 46.6753, "tz": "Asia/Riyadh"},
    "makkah": {"name": "مكة المكرمة", "lat": 21.4225, "lon": 39.8262, "tz": "Asia/Riyadh"},
    "madinah": {"name": "المدينة المنورة", "lat": 24.4673, "lon": 39.6068, "tz": "Asia/Riyadh"},
    "jeddah": {"name": "جدة", "lat": 21.5433, "lon": 39.1728, "tz": "Asia/Riyadh"}
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    cities_list = list(CITIES.items())
    for i in range(0, len(cities_list), 2):
        row = [InlineKeyboardButton(cities_list[i][1]["name"], callback_data=f"set_{cities_list[i][0]}")]
        if i + 1 < len(cities_list):
            row.append(InlineKeyboardButton(cities_list[i+1][1]["name"], callback_data=f"set_{cities_list[i+1][0]}"))
        keyboard.append(row)
    await update.message.reply_text("✨ مرحباً بك يا محمد في بوت قرآن الفجر\nيرجى اختيار مدينتك لتصلك الأذكار في وقتها:", reply_markup=InlineKeyboardMarkup(keyboard))

async def city_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city_code = query.data.split("_")[1]
    chat_id = str(query.message.chat_id)
    data = load_data()
    data[chat_id] = {"lat": CITIES[city_code]['lat'], "lon": CITIES[city_code]['lon'], "tz": CITIES[city_code]['tz']}
    save_data(data)
    await query.edit_message_text(f"✅ تم ضبط التوقيت لمدينة {CITIES[city_code]['name']}\nقناتنا الرسمية: {OFFICIAL_CHANNEL_LINK}")

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Running"

def main():
    # تشغيل سيرفر صغير لإبقاء البوت حياً على Render
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    
    # تشغيل البوت
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(city_callback, pattern="^set_"))
    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
    
