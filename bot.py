import os
import telebot
import yt_dlp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# التوكن الخاص بك
BOT_TOKEN = "8985088016:AAG4DYONt_6mUpUVvQ-BAK4Qr1GP1zWwELY"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
    أهلاً بك يا محمد حازم! 👋
    أنا بوت المحمل الشامل، أستطيع تحميل الفيديوهات أو تحويلها إلى MP3.
    فقط أرسل لي الرابط وسأتولى الباقي!
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if not url.startswith("http"):
        bot.reply_to(message, "❌ الرجاء إرسال رابط صحيح يبدأ بـ http أو https.")
        return

    # إرسال أزرار اختيار الصيغة (فيديو أو صوت)
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎬 تحميل فيديو", callback_data=f"video|{url}"),
        InlineKeyboardButton("🎵 تحميل MP3", callback_data=f"audio|{url}")
    )
    bot.reply_to(message, "📥 ماذا تريد أن تفعل بهذا الرابط؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    # فصل البيانات لمعرفة هل الطلب فيديو أم صوت
    data = call.data.split("|", 1)
    action = data[0]
    url = data[1]

    bot.delete_message(call.message.chat.id, call.message.message_id)
    msg = bot.send_message(call.message.chat.id, "⏳ جاري التحميل والمعالجة... يرجى الانتظار.")

    # إعدادات yt-dlp للتحميل بجودة عالية
    ydl_opts = {
        'outtmpl': f'%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    # تخصيص الإعدادات إذا كان الطلب صوت فقط
    if action == "audio":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        file_extension = 'mp3'
    else:
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        file_extension = 'mp4'

    try:
        # بدء عملية التحميل
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = f"{info['id']}.{file_extension}"
            title = info.get('title', 'فيديو بدون عنوان')

            bot.edit_message_text(f"✅ تم الانتهاء من التحميل! جاري الإرسال إلى التليجرام...", chat_id=call.message.chat.id, message_id=msg.message_id)

            # رفع الملف إلى التليجرام
            with open(file_name, 'rb') as f:
                if action == "audio":
                    bot.send_audio(call.message.chat.id, f, title=title)
                else:
                    bot.send_video(call.message.chat.id, f, caption=title)
            
            # تنظيف وحذف الملف من السيرفر لتجنب امتلاء المساحة
            os.remove(file_name)
            bot.delete_message(call.message.chat.id, msg.message_id)

    except Exception as e:
        error_msg = f"❌ تعذر التحميل. قد يكون الفيديو خاصاً (Private) أو محمياً.\n\nنص الخطأ التقني: {str(e)[:150]}"
        bot.edit_message_text(error_msg, chat_id=call.message.chat.id, message_id=msg.message_id)
        print(f"Error: {e}")

if __name__ == "__main__":
    print("البوت يعمل الآن...")
    bot.infinity_polling()
