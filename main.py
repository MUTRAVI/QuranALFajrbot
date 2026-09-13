import subprocess
import sys

# 1. تثبيت المكتبات وتحديث البيئة أولاً
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "python-telegram-bot[job-queue]", "APScheduler", "pytz"])

# 2. استدعاء المكتبات بعد ضمان التثبيت الكامل
import os
import pytz
from datetime import time
import telegram.ext
from telegram.ext import Application

TOKEN = "7674563071:AAGgszBWDJ72Yudm8_dTsgA"
CHANNEL_ID = "@QuranAlfajrOfficial"
TIMEZONE = pytz.timezone('Asia/Riyadh')

async def send_sabah(context):
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=open('images/sabah.jpg', 'rb'))

async def send_massa(context):
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=open('images/massa.jpg', 'rb'))

async def send_sleep(context):
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=open('images/sleep_azkar.jpg', 'rb'))

async def send_friday(context):
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=open('images/friday_sunnah.jpg', 'rb'))

def main():
    # بناء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # التحقق من وجود JobQueue
    if application.job_queue is None:
        print("خطأ: لم يتم التعرف على JobQueue. جاري إعادة التشغيل...")
        sys.exit(1)

    job_queue = application.job_queue

    # جدولة المهام
    job_queue.run_daily(send_sabah, time=time(hour=5, minute=30, tzinfo=TIMEZONE))
    job_queue.run_daily(send_massa, time=time(hour=16, minute=30, tzinfo=TIMEZONE))
    job_queue.run_daily(send_sleep, time=time(hour=22, minute=30, tzinfo=TIMEZONE))
    job_queue.run_daily(send_friday, time=time(hour=9, minute=0, day_of_week=4, tzinfo=TIMEZONE))

    print("البوت فعال وشغال بنجاح...")
    application.run_polling()

if __name__ == '__main__':
    main()
