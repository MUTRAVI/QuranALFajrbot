import os
import random
import json
import asyncio
from datetime import datetime, timedelta
import pytz
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes
from prayer_times_calculator import PrayerTimesCalculator
from flask import Flask
import threading

# 1. الإعدادات
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DATA_FILE = "users_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return {}

def save_user(chat_id, timezone="Asia/Riyadh"):
    data = load_data()
    data[str(chat_id)] = {"tz": timezone}
    with open(DATA_FILE, "w") as f: json.dump(data, f)

# 2. المحتوى
MORNING_ATHKAR = "☀️ *أذكار الصباح*\n(أصبحنا وأصبح الملك لله...)"
EVENING_ATHKAR = "🌙 *أذكار المساء*\n(أمسينا وأمسى الملك لله...)"

QURAN_LIST = [
    {"v": "﴿وَسَارِعُوا إِلَىٰ مَغْفِرَةٍ مِّن رَّبِّكُمْ﴾", "t": "توجيه رباني بالمبادرة بالأعمال الصالحة."},
    {"v": "﴿إِنَّ مَعَ الْعُسْرِ يُسْرًا﴾", "t": "بشارة بأن كل ضيق سيعقبه فرج قريب."}
]

# 3. وظيفة حساب مواقيت الصلاة
def get_times(tz_name):
    # نستخدم إحداثيات تقريبية بناءً على التوقيت (للبساطة)
    # الرياض كمثال افتراضي
    calc = PrayerTimesCalculator(latitude=24.7136, longitude=46.6753, 
                                 calculation_method='umm_al_qura', 
                                 date=str(datetime.now(pytz.timezone(tz_name)).date()))
    return calc.fetch_prayer_times()

# 4. المهام المجدولة
async def daily_broadcast(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    for chat_id, info in data.items():
        tz = pytz.timezone(info['tz'])
        now = datetime.now(tz)
        times = get_times(info['tz'])
        
        # تحويل أوقات الصلاة لنصوص زمنية
        fajr_time = datetime.strptime(times['Fajr'], '%H:%M').replace(year=now.year, month=now.month, day=now.day)
        maghrib_time = datetime.strptime(times['Maghrib'], '%H:%M').replace(year=now.year, month=now.month, day=now.day)

        # إذا كان الوقت الآن = وقت الفجر + 30 دقيقة
        if now.hour == (fajr_time + timedelta(minutes=30)).hour and now.minute == (fajr_time + timedelta(minutes=30)).minute:
            await context.bot.send_message(chat_id=chat_id, text=MORNING_ATHKAR, parse_mode=ParseMode.MARKDOWN)
        
        # إذا كان الوقت الآن = وقت المغرب - 30 دقيقة
        if now.hour == (maghrib_time - timedelta(minutes=30)).hour and now.minute == (maghrib_time - timedelta(minutes=30)).minute:
            await context.bot.send_message(chat_id=chat_id, text=EVENING_ATHKAR, parse_mode=ParseMode.MARKDOWN)

async def random_post(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    item = random.choice(QURAN_LIST)
    msg = f"📖 *من آيات الذكر الحكيم:*\n\n{item['v']}\n\n💡 *التفسير:* {item['t']}"
    for chat_id in data.keys():
        try: await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)
        except: continue
    
    # جدولة المرة القادمة وقت عشوائي
    next_time = random.randint(1800, 10800)
    context.job_queue.run_once(random_post, when=next_time)

# 5. الأوامر
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_chat.id)
    await update.message.reply_text("تم تفعيل البوت! سيصلك أذكار الصباح والمساء حسب توقيتك، ومنشورات عشوائية يومياً.")

# 6. التشغيل
app = Flask(__name__)
@app.route('/')
def home(): return "Active"

def run_flask(): app.run(host='0.0.0.0', port=8080)

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    job_queue = application.job_queue
    # فحص الأذكار كل دقيقة
    job_queue.run_repeating(daily_broadcast, interval=60, first=10)
    # المنشور العشوائي الأول
    job_queue.run_once(random_post, when=120)
    
    application.run_polling()

if __name__ == '__main__':
    main()
