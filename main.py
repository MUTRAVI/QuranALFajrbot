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

# 2. قاعدة بيانات الأذكار (الصباح والمساء)
MORNING_DB = [
    "آية الكرسي: ﴿اللَّهُ لَا إِلَهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ﴾.. (من قالها حين يصبح أجير من الجن حتى يمسي).",
    "سيد الاستغفار: (اللهم أنت ربي لا إله إلا أنت، خلقتني وأنا عبدك، وأنا على عهدك ووعدك ما استطعت..).",
    "أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
    "بسم الله الذي لا يضر مع اسمه شيء في الأرض ولا في السماء وهو السميع العليم. (3 مرات).",
    "يا حي يا قيوم برحمتك أستغيث، أصلح لي شأني كله، ولا تكلني إلى نفسي طرفة عين.",
    "رضيت بالله رباً، وبالإسلام ديناً، وبمحمد صلى الله عليه وسلم نبياً. (3 مرات).",
    "حسبي الله لا إله إلا هو، عليه توكلت وهو رب العرش العظيم. (7 مرات).",
    "اللهم إني أسألك العفو والعافية في الدنيا والآخرة، اللهم إني أسألك العفو والعافية في ديني ودنياي وأهلي ومالي."
]

EVENING_DB = [
    "آية الكرسي: ﴿اللَّهُ لَا إِلَهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ﴾.. (من قالها حين يمسي أجير من الجن حتى يصبح).",
    "أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
    "اللهم بك أمسينا، وبك أصبحنا، وبك نحيا، وبك نموت، وإليك المصير.",
    "أعوذ بكلمات الله التامات من شر ما خلق. (3 مرات).",
    "حسبي الله لا إله إلا هو، عليه توكلت وهو رب العرش العظيم. (7 مرات).",
    "يا حي يا قيوم برحمتك أستغيث، أصلح لي شأني كله، ولا تكلني إلى نفسي طرفة عين.",
    "سيد الاستغفار: (اللهم أنت ربي لا إله إلا أنت، خلقتني وأنا عبدك..).",
    "رضيت بالله رباً، وبالإسلام ديناً، وبمحمد صلى الله عليه وسلم نبياً. (3 مرات)."
]

# 3. حفظ البيانات
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_user(chat_id, timezone="Asia/Riyadh"):
    data = load_data()
    if str(chat_id) not in data:
        data[str(chat_id)] = {"tz": timezone, "last_m": "", "last_e": ""}
        with open(DATA_FILE, "w") as f: json.dump(data, f)

# 4. المهام المجدولة
async def daily_broadcast(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    today_str = str(datetime.now().date())
    updated = False

    for chat_id, info in data.items():
        try:
            tz = pytz.timezone(info.get('tz', 'Asia/Riyadh'))
            now = datetime.now(tz)
            calc = PrayerTimesCalculator(latitude=24.7136, longitude=46.6753, 
                                         calculation_method='umm_al_qura', date=str(now.date()))
            times = calc.fetch_prayer_times()
            
            fajr = datetime.strptime(times['Fajr'], '%H:%M').replace(year=now.year, month=now.month, day=now.day)
            maghrib = datetime.strptime(times['Maghrib'], '%H:%M').replace(year=now.year, month=now.month, day=now.day)

            # إرسال أذكار الصباح (3 عشوائية)
            target_m = fajr + timedelta(minutes=30)
            if now >= target_m and info.get('last_m') != today_str:
                selection = random.sample(MORNING_DB, k=min(3, len(MORNING_DB)))
                msg = "☀️ *أذكار الصباح المختارة لهذا اليوم:*\n\n" + "\n\n".join(selection)
                await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)
                info['last_m'] = today_str
                updated = True
            
            # إرسال أذكار المساء
            target_e = maghrib - timedelta(minutes=30)
            if now >= target_e and info.get('last_e') != today_str:
                selection = random.sample(EVENING_DB, k=min(3, len(EVENING_DB)))
                msg = "🌙 *أذكار المساء المختارة لهذا اليوم:*\n\n" + "\n\n".join(selection)
                await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)
                info['last_e'] = today_str
                updated = True
        except: continue

    if updated:
        with open(DATA_FILE, "w") as f: json.dump(data, f)

# 5. التشغيل
app = Flask(__name__)
@app.route('/')
def home(): return "Bot Active"

def main():
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    application = Application.builder().token(TOKEN).build()
    
    async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        save_user(update.effective_chat.id)
        await update.message.reply_text("✅ تم تفعيل البوت بنجاح! سيصلك 3 أذكار منوعة يومياً.")
    
    application.add_handler(CommandHandler("start", start_cmd))
    
    # الجدولة
    jq = application.job_queue
    jq.run_repeating(daily_broadcast, interval=300, first=10)
    
    application.run_polling()

if __name__ == '__main__':
    main()
