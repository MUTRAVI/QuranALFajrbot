import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot[job-queue]", "APScheduler", "pytz"])

import os
import pytz
from datetime import time
from telegram.ext import Application

import os
import pytz
from datetime import time
from telegram.ext import Application

TOKEN = "7674563071:AAGgszBWDJ72Yudm8_dTSgA"
CHANNEL_ID = "@QuranAlfajrOfficial"
TIMEZONE = pytz.timezone('Asia/Riyadh')

async def send_sabah(context):
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=open('images/sabah.jpg', 'rb'), caption="☀️ أذكار الصباح")

async def send_massa(context):
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=open('images/massa.jpg', 'rb'), caption="🌆 أذكار المساء")

async def send_sleep(context):
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=open('images/sleep_azkar.jpg', 'rb'), caption="🌙 أذكار النوم")

async def send_friday(context):
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=open('images/friday_sunnah.jpg', 'rb'), caption="🌿 من سنن يوم الجمعة")

def main():
    app = Application.builder().token(TOKEN).build()
    job_queue = app.job_queue

    job_queue.run_daily(send_sabah, time=time(hour=5, minute=30, tzinfo=TIMEZONE))
    job_queue.run_daily(send_massa, time=time(hour=16, minute=30, tzinfo=TIMEZONE))
    job_queue.run_daily(send_sleep, time=time(hour=22, minute=30, tzinfo=TIMEZONE))
    job_queue.run_daily(send_friday, time=time(hour=9, minute=0, tzinfo=TIMEZONE), days=(4,))

    print("البوت يعمل بنجاح...")
    app.run_polling()

if __name__ == '__main__':
    main()
