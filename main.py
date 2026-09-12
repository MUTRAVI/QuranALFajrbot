import subprocess
import sys

# تثبيت المكتبات المطلوبة فوراً عند الإقلاع
subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot[job-queue]", "APScheduler", "pytz"])

import os
import pytz
from datetime import time
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
    # بناء التطبيق بعد ضمان تثبيت المكتبة
    application = Application.builder().token(TOKEN).build()
    job_queue = application.job_queue

    # جدولة المواعيد
    job_queue.run_daily(send_sabah, time=time(hour=5, minute=30, tzinfo=TIMEZONE))
    job_queue.run_daily(send_massa, time=time(hour=16, minute=30, tzinfo=TIMEZONE))
    job_queue.run_daily(send_sleep, time=time(hour=22, minute=30, tzinfo=TIMEZONE))
    job_queue.run_daily(send_friday, time=time(hour=9, minute=0, day_of_week=4, tzinfo=TIMEZONE))

    print("البوت فعال...")
    application.run_polling()

if __name__ == '__main__':
    main()
