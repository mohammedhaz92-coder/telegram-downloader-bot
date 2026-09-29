import os
import telebot
import yt_dlp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# توكن البوت الخاص بك
BOT_TOKEN = "8985088016:AAG4DYONt_6mUpUVvQ-BAK4Qr1GP1zWwELY"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
    أهلاً بك يا محمد حازم! 👋
    أنا بوت التحميل الشامل (يوتيوب، تيك توك، انستقرام ستوري وريلز، فيسبوك).
    أرسل لي الرابط الآن للبدء!
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if not url.startswith("http"):
        bot.reply_to(message, "❌ الرجاء إرسال رابط صحيح يبدأ بـ http أو https.")
        return

    # أزرار اختيار الجودة
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎬 فيديو (جودة أصلية)", callback_data=f"best|{url}")
    )
    markup.row(
        InlineKeyboardButton("🎬 فيديو (جودة متوسطة)", callback_data=f"med|{url}"),
        InlineKeyboardButton("🎵 مقطع صوتي (MP3)", callback_data=f"audio|{url}")
    )
    bot.reply_to(message, "📥 اختر الجودة أو الصيغة المطلوبة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data = call.data.split("|", 1)
    action = data[0]
    url = data[1]

    bot.delete_message(call.message.chat.id, call.message.message_id)
    msg = bot.send_message(call.message.chat.id, "⏳ جاري التحميل والمعالجة... يرجى الانتظار.")

    # إعدادات التحميل (مع إضافة هيدرز لتخطي حماية تيك توك وانستقرام)
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    }

    if action == "audio":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    elif action == "best":
        # الجودة الأصلية (بحد أقصى 50 ميجا ليتوافق مع تليجرام)
        ydl_opts['format'] = 'bestvideo[filesize<=50M]+bestaudio/best[filesize<=50M]/best'
    else: 
        # جودة متوسطة لتسريع التحميل وتصغير الحجم
        ydl_opts['format'] = 'best[height<=720]/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # استخراج معلومات الفيديو وتحميله
            info = ydl.extract_info(url, download=True)
            
            # تحديد اسم الملف النهائي بناءً على ما تم تحميله
            filename = ydl.prepare_filename(info)
            if action == "audio":
                filename = filename.rsplit('.', 1)[0] + '.mp3'
            
            title = info.get('title', 'بدون عنوان')

            bot.edit_message_text(f"✅ تم سحب المقطع! جاري الإرسال إلى تليجرام...", chat_id=call.message.chat.id, message_id=msg.message_id)

            # رفع الملف إلى تليجرام مع زيادة وقت الانتظار (timeout=120) لمنع الخطأ
            with open(filename, 'rb') as f:
                if action == "audio":
                    bot.send_audio(call.message.chat.id, f, title=title, timeout=120)
                else:
                    bot.send_video(call.message.chat.id, f, caption=title, timeout=120)
            
            # حذف الملف من السيرفر بعد الإرسال
            if os.path.exists(filename):
                os.remove(filename)
                
            bot.delete_message(call.message.chat.id, msg.message_id)
            
            # رسالة طلب رابط جديد
            bot.send_message(call.message.chat.id, "🔄 لتحميل ملف آخر انسخ الرابط هنا")

    except Exception as e:
        error_msg = "❌ تعذر التحميل.\n- قد يكون الحساب خاصاً (Private).\n- قد يكون حجم الفيديو أكبر من 50MB (حدود تليجرام المسموحة للبوتات)."
        bot.edit_message_text(error_msg, chat_id=call.message.chat.id, message_id=msg.message_id)
        print(f"Error: {e}")

if __name__ == "__main__":
    print("البوت يعمل الآن...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
