import os
import json
import requests
from google import genai
from telegram import Bot
import yt_dlp
import sys
from moviepy.editor import ImageClip, AudioFileClip

# --- KONFIGURASI DARI GITHUB SECRETS ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GDRIVE_JSON = os.getenv("GDRIVE_CREDENTIALS")
FOLDER_ID = "14VaQQKHy6-e3bkCdlfX_XsPYEMmuRRpi"

def lapor(pesan):
    try:
        Bot(token=TG_TOKEN).send_message(chat_id=CHAT_ID, text=pesan)
    except:
        print(f"TG Error: {pesan}")

def main():
    tema = "Unknown"
    
    # --- TAHAP 1: GEMINI (SDK BARU) ---
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents="Give 1 short ASMR theme (e.g. Rainy Mood). Just the theme."
        )
        tema = response.text.strip()
    except Exception as e:
        lapor(f"❌ GAGAL TAHAP 1 (Gemini):\n{str(e)}")
        sys.exit(1)

    # --- TAHAP 2: AUDIO ---
    try:
        ydl_opts = {'format': 'bestaudio', 'outtmpl': 'audio.mp3', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:ASMR {tema} no talk"])
    except Exception as e:
        lapor(f"❌ GAGAL TAHAP 2 (Audio):\n{str(e)}")
        sys.exit(1)

    # --- TAHAP 3: GAMBAR ---
    try:
        img_url = f"https://source.unsplash.com/1600x900/?{tema.replace(' ', ',')}"
        res = requests.get(img_url)
        with open('gambar.jpg', 'wb') as f: f.write(res.content)
    except Exception as e:
        lapor(f"❌ GAGAL TAHAP 3 (Gambar):\n{str(e)}")
        sys.exit(1)

    # --- TAHAP 4: RENDER ---
    try:
        audio = AudioFileClip("audio.mp3").subclip(0, 30) # 30 detik dulu buat tes
        video = ImageClip("gambar.jpg").set_duration(audio.duration).set_audio(audio)
        video.write_videofile("hasil.mp4", fps=24, codec="libx264", audio_codec="aac", logger=None)
    except Exception as e:
        lapor(f"❌ GAGAL TAHAP 4 (Render):\n{str(e)}")
        sys.exit(1)

    # --- TAHAP 5: UPLOAD GDRIVE ---
    try:
        info = json.loads(GDRIVE_JSON)
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=creds)
        meta = {'name': f"ASMR_{tema}.mp4", 'parents': [FOLDER_ID]}
        media = MediaFileUpload("hasil.mp4", mimetype='video/mp4')
        service.files().create(body=meta, media_body=media).execute()
        
        lapor(f"✅ BERHASIL!\n🎬 Tema: {tema}\n📂 Cek Drive Bos!")
    except Exception as e:
        lapor(f"❌ GAGAL TAHAP 5 (Drive):\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    
