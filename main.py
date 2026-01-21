import os
import random
from datetime import datetime, timedelta
import pytz
from telegram import Bot
from telegram.constants import ParseMode
from apscheduler.schedulers.background import BackgroundScheduler
from prayer_times_calculator import PrayerTimesCalculator
from flask import Flask

# 1. إعدادات البوت والقناة
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=TOKEN)
CHANNEL_ID = "@YourChannelID" # <--- استبدل هذا بيوزر قناتك

# 2. المحتوى المتنوع (آيات، أحاديث، أدعية)
QURAN_LIST = [
    {"v": "﴿وَسَارِعُوا إِلَىٰ مَغْفِرَةٍ مِّن رَّبِّكُمْ﴾", "t": "توجيه رباني بالمبادرة بالأعمال الصالحة وعدم التأجيل."},
    {"v": "﴿إِنَّ مَعَ الْعُسْرِ يُسْرًا﴾", "t": "بشارة من الله أن كل ضيق سيعقبه فرج قريب."}
]
HADITH_LIST = [
    "قال رسول الله ﷺ: (خَيْرُكُمْ مَنْ تَعَلَّمَ الْقُرْآنَ وَعَلَّمَهُ).",
    "قال ﷺ: (مَنْ صَلَّى عَلَيَّ صَلَاةً صَلَّى الله عَلَيْهِ بِهَا عَشْرًا)."
]
DUA_LIST = [
    "اللهم إني أسألك علماً نافعاً، ورزقاً طيباً، وعملاً متقبلاً.",
    "يا حي يا قيوم برحمتك أستغيث، أصلح لي شأني كله."
]

# 3. وظيفة النشر العشوائي
def send_benefit():
    choice = random.choice(['q', 'h', 'd'])
    if choice == 'q':
        item = random.choice(QURAN_LIST)
        msg = f"📖 *من آيات الذكر الحكيم:*\n\n{item['v']}\n\n💡 *التفسير:* {item['t']}"
    elif choice == 'h':
        msg = f"✨ *حديث نبوي شريف:*\n\n{random.choice(HADITH_LIST)}"
    else:
        msg = f"🤲 *دعاء مستجاب بإذن الله:*\n\n{random.choice(DUA_LIST)}"
    try:
        bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode=ParseMode.MARKDOWN)
    except: pass

# 4. المجدول الزمني (الرياض)
def setup_schedule():
    try:
        calc = PrayerTimesCalculator(latitude=24.7136, longitude=46.6753, calculation_method='umm_al_qura', date=str(datetime.now(pytz.timezone('Asia/Riyadh')).date()))
        times = calc.fetch_prayer_times()
        
        scheduler.remove_all_jobs()
        # نشر عشوائي كل 3 ساعات ليبقى البوت مستيقظاً
        scheduler.add_job(send_benefit, 'interval', hours=3)
        scheduler.add_job(setup_schedule, 'cron', hour=0, minute=1)
    except: pass

scheduler = BackgroundScheduler(timezone="Asia/Riyadh")
setup_schedule()
scheduler.start()

# 5. نظام Flask للبقاء حياً مع Cron-job
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Online"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
