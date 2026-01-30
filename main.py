import os
from telegram import Bot

TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def test():
    try:
        bot = Bot(token=TG_TOKEN)
        bot.send_message(chat_id=CHAT_ID, text="🚨 TES KONEKSI: Kalau kamu baca ini, berarti Telegram Aman!")
        print("Sukses kirim ke TG")
    except Exception as e:
        print(f"Error TG: {e}")

if __name__ == "__main__":
    test()
    
