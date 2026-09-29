FROM python:3.9-slim

# تحديث النظام وتثبيت ffmpeg الضروري للتحويل
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# تحديد مسار العمل
WORKDIR /app

# نسخ ملف requirements.txt وتثبيت المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي الملفات
COPY . .

# تشغيل البوت
CMD ["python", "bot.py"]
