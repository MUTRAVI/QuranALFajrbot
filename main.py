import os
import logging
from flask import Flask
from threading import Thread
from telegram.ext import ApplicationBuilder
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import pytz

# إعداد خادم بسيط لإبقاء البوت مستيقظاً (Keep-Alive)
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# محتوى الأذكار (سيتم استبدالها بصورك لاحقاً)
def send_dhikr():
    # هنا سيتم وضع كود إرسال الصور فور جاهزيتها
    print(f"إرسال ذكر عند: {datetime.now()}")

if __name__ == '__main__':
    # تشغيل ميزة إبقاء البوت مستيقظاً
    keep_alive()
    
    # إعداد البوت (استقبال التوكن عبر البيئة)
    token = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BACKUP_TOKEN')
    application = ApplicationBuilder().token(token).build()
    
    # إعداد المجدل (توقيت مكة المكرمة)
    scheduler = BlockingScheduler(timezone=pytz.timezone('Asia/Riyadh'))
    
    # جدولة النشر كل 30 دقيقة
    scheduler.add_job(send_dhikr, 'interval', minutes=30)
    
    print("البوت بدأ العمل بنظام المستودع المستقر...")
    scheduler.start()
