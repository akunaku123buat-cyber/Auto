import os
import json
import requests
from google import genai
from telegram import Bot
import sys
from moviepy.editor import ImageClip, AudioFileClip

# --- KONFIGURASI ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GDRIVE_JSON = os.getenv("GDRIVE_CREDENTIALS")
FOLDER_ID = "14VaQQKHy6-e3bkCdlfX_XsPYEMmuRRpi"

def lapor(pesan):
    try: Bot(token=TG_TOKEN).send_message(chat_id=CHAT_ID, text=pesan)
    except: print(pesan)

def main():
    tema = "Rain"
    
    # 1. GEMINI (Cari Kata Kunci)
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        response = client.models.generate_content(model="gemini-2.0-flash", contents="Give me 1 simple English word for ASMR nature sound (e.g. Rain, Forest, Ocean). Just 1 word.")
        tema = response.text.strip()
    except Exception as e:
        lapor(f"❌ GEMINI GAGAL: {str(e)}")
        sys.exit(1)

    # 2. CARI AUDIO DI PIXABAY (Lebih aman dari YouTube)
    try:
        # Kita cari suara alam di Pixabay
        search_url = f"https://pixabay.com/api/videos/?key=43224742-53b05f6319808a3d54838e1a1&q={tema}&category=nature"
        # Karena Pixabay API audio butuh key sendiri, kita pakai cara 'tembak langsung' ke file publik atau ganti taktik ke download file statis dulu buat tes.
        # UNTUK TES: Kita pakai link audio hujan yang pasti jalan
        audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" 
        res = requests.get(audio_url)
        with open('audio.mp3', 'wb') as f: f.write(res.content)
    except Exception as e:
        lapor(f"❌ AUDIO GAGAL: {str(e)}")
        sys.exit(1)

    # 3. GAMBAR
    try:
        img_url = f"https://picsum.photos/seed/{tema}/1600/900"
        with open('gambar.jpg', 'wb') as f: f.write(requests.get(img_url).content)
    except Exception as e:
        lapor(f"❌ GAMBAR GAGAL: {str(e)}")
        sys.exit(1)

    # 4. RENDER
    try:
        audio = AudioFileClip("audio.mp3").subclip(0, 10) # 10 detik aja buat tes
        video = ImageClip("gambar.jpg").set_duration(audio.duration).set_audio(audio)
        video.write_videofile("hasil.mp4", fps=24, codec="libx264", audio_codec="aac", logger=None)
    except Exception as e:
        lapor(f"❌ RENDER GAGAL: {str(e)}")
        sys.exit(1)

    # 5. UPLOAD GDRIVE
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
        lapor(f"✅ BERHASIL TOTAL!\nTema: {tema}")
    except Exception as e:
        lapor(f"❌ DRIVE GAGAL: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
        
