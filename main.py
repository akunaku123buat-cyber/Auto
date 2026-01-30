import os
import json
import requests
import asyncio
from google import genai
from telegram import Bot
import sys
from moviepy.editor import ImageClip, AudioFileClip

# --- KONFIGURASI ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GDRIVE_JSON = os.getenv("GDRIVE_CREDENTIALS")
FOLDER_ID = "1A_Qy7lMNnkClfNas8v41J4aipIlHcCyh"

async def lapor(pesan):
    try:
        bot = Bot(token=TG_TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=pesan)
    except Exception as e:
        print(f"Gagal lapor: {e}")

async def main():
    tema = "Rain"
    
    # 1. GEMINI
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents="Give me 1 simple English word for ASMR nature (e.g. Forest, Ocean, Rain). Just 1 word."
        )
        tema = response.text.strip()
    except Exception as e:
        await lapor(f"❌ GEMINI GAGAL: {e}")
        return

    # 2. AUDIO (Link Statis yang Pasti Jalan)
    try:
        # Pake link audio sample biar gak kena blok YouTube dulu
        audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        with open('audio.mp3', 'wb') as f:
            f.write(requests.get(audio_url).content)
    except Exception as e:
        await lapor(f"❌ AUDIO GAGAL: {e}")
        return

    # 3. GAMBAR
    try:
        img_url = f"https://picsum.photos/seed/{tema}/1280/720"
        with open('gambar.jpg', 'wb') as f:
            f.write(requests.get(img_url).content)
    except Exception as e:
        await lapor(f"❌ GAMBAR GAGAL: {e}")
        return

    # 4. RENDER (15 Detik biar Cepet)
    try:
        audio = AudioFileClip("audio.mp3").subclip(0, 15)
        video = ImageClip("gambar.jpg").set_duration(audio.duration).set_audio(audio)
        video.write_videofile("hasil.mp4", fps=24, codec="libx264", audio_codec="aac", logger=None)
    except Exception as e:
        await lapor(f"❌ RENDER GAGAL: {e}")
        return

            # --- TAHAP 5: UPLOAD GDRIVE (MODE SEMBUNYI EMAIL) ---
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        
        # Ambil email dari Secrets GitHub
        MY_EMAIL = os.getenv("MY_GDRIVE_EMAIL")
        
        info = json.loads(GDRIVE_JSON.strip())
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('drive', 'v3', credentials=creds)
        
        # 1. Upload File
        meta = {'name': f"ASMR_{tema}.mp4", 'parents': [FOLDER_ID]}
        media = MediaFileUpload("hasil.mp4", mimetype='video/mp4', resumable=True)
        
        file = service.files().create(
            body=meta, 
            media_body=media, 
            fields='id',
            supportsAllDrives=True
        ).execute()
        
        file_id = file.get('id')

        # 2. Pindahkan Kepemilikan (Pakai email dari Secret)
        user_permission = {
            'type': 'user',
            'role': 'owner',
            'emailAddress': MY_EMAIL 
        }
        
        service.permissions().create(
            fileId=file_id,
            body=user_permission,
            transferOwnership=True,
            supportsAllDrives=True
        ).execute()
        
        await lapor(f"✅ BERHASIL TOTAL, KETUA!\n🎬 Video: {tema}\n📂 Sudah masuk ke Drive kamu.")
    except Exception as e:
        await lapor(f"❌ GDRIVE GAGAL: {e}")



if __name__ == "__main__":
    asyncio.run(main())
        
