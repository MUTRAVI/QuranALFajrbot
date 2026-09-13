import subprocess
import sys

# تثبيت المكتبات المضمونة
subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot", "apscheduler", "pytz"])

import asyncio
import pytz
from datetime import time
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "7674563071:AAGgszBWDJ72Yudm8_dTsgA"
CHANNEL_ID = "@QuranAlfajrOfficial"
TIMEZONE = pytz.timezone('Asia/Riyadh')

bot = Bot(token=TOKEN)

async def send_sabah():
    await bot.send_photo(chat_id=CHANNEL_ID, photo=open('images/sabah.jpg', 'rb'))

async def send_massa():
    await bot.send_photo(chat_id=CHANNEL_ID, photo=open('images/massa.jpg', 'rb'))

async def send_sleep():
    await bot.send_photo(chat_id=CHANNEL_ID, photo=open('images/sleep_azkar.jpg', 'rb'))

async def send_friday():
    await bot.send_photo(chat_id=CHANNEL_ID, photo=open('images/friday_sunnah.jpg', 'rb'))

async def main():
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)

    # جدولة المواعيد بتوقيت الرياض
    scheduler.add_job(send_sabah, 'cron', hour=5, minute=30)
    scheduler.add_job(send_massa, 'cron', hour=16, minute=30)
    scheduler.add_job(send_sleep, 'cron', hour=22, minute=30)
    scheduler.add_job(send_friday, 'cron', day_of_week='fri', hour=9, minute=0)

    scheduler.start()
    print("تم تشغيل البوت والجدولة بنجاح تام!")

    # إبقاء البوت شغال بدون توقف
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
