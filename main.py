import os
import json
import requests
from google import genai
from telegram import Bot
import yt_dlp
import sys
from moviepy.editor import ImageClip, AudioFileClip
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- KONFIGURASI ---
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
    
    # --- TAHAP 1: GEMINI ---
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Give 1 short ASMR theme (e.g. Rainy Mood). Just the theme.")
        tema = response.text.strip()
    except Exception as e:
        lapor(f"❌ GAGAL DI TAHAP 1 (Gemini):\n{str(e)}\n🛑 Mesin Berhenti.")
        sys.exit(1)

    # --- TAHAP 2: DOWNLOAD AUDIO ---
    try:
        ydl_opts = {'format': 'bestaudio', 'outtmpl': 'audio.mp3', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:ASMR {tema} no talk"])
    except Exception as e:
        lapor(f"❌ GAGAL DI TAHAP 2 (Audio Download):\nTema: {tema}\nError: {str(e)}\n🛑 Mesin Berhenti.")
        sys.exit(1)

    # --- TAHAP 3: GAMBAR ---
    try:
        img_url = f"https://source.unsplash.com/1600x900/?{tema.replace(' ', ',')}"
        res = requests.get(img_url)
        if res.status_code != 200: raise Exception("Gambar tidak ditemukan")
        with open('gambar.jpg', 'wb') as f: f.write(res.content)
    except Exception as e:
        lapor(f"❌ GAGAL DI TAHAP 3 (Gambar):\nTema: {tema}\nError: {str(e)}\n🛑 Mesin Berhenti.")
        sys.exit(1)

    # --- TAHAP 4: RENDER ---
    try:
        audio = AudioFileClip("audio.mp3").subclip(0, 60) # Durasi 1 menit
        video = ImageClip("gambar.jpg").set_duration(audio.duration).set_audio(audio)
        video.write_videofile("asmr_final.mp4", fps=24, codec="libx264", audio_codec="aac", logger=None)
    except Exception as e:
        lapor(f"❌ GAGAL DI TAHAP 4 (Rendering):\nTema: {tema}\nError: {str(e)}\n🛑 Mesin Berhenti.")
        sys.exit(1)

    # --- TAHAP 5: UPLOAD GDRIVE ---
    try:
        info = json.loads(GDRIVE_JSON)
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': f"ASMR_{tema}.mp4", 'parents': [FOLDER_ID]}
        media = MediaFileUpload("asmr_final.mp4", mimetype='video/mp4')
        service.files().create(body=file_metadata, media_body=media).execute()
    except Exception as e:
        lapor(f"❌ GAGAL DI TAHAP 5 (Upload GDrive):\nTema: {tema}\nError: {str(e)}\n🛑 Mesin Berhenti.")
        sys.exit(1)

    # --- JIKA SEMUA BERHASIL ---
    lapor(f"✅ SEMUA PROSES BERHASIL!\n🎬 Tema: {tema}\n📂 Video sudah siap di Google Drive kamu, Bos!")

if __name__ == "__main__":
    main()
    
