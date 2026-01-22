import asyncio
import os
import requests
import google.generativeai as genai
import time
from jpg import download_gambar
from mp3 import hasilkan_suara_dan_sub

async def jalankan_otomatis():
    # Inisialisasi API
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 1. BUAT NASKAH
    print("✍️ Membuat naskah...")
    try:
        res = model.generate_content("Buatkan 1 kalimat motivasi singkat (max 15 kata) untuk TikTok.")
        naskah = res.text.strip()
        if not naskah:
            raise ValueError("Naskah kosong")
        print(f"✅ Naskah: {naskah}")
    except Exception as e:
        print(f"❌ STOP: Gagal membuat naskah karena {e}")
        return # BERHENTI DI SINI jika gagal

    # 2. BUAT GAMBAR
    print("🎨 Mengunduh gambar...")
    try:
        img_path = download_gambar(naskah, "bg_utama")
        if not os.path.exists(img_path):
            raise FileNotFoundError("File gambar tidak ada")
        print("✅ Gambar berhasil diunduh")
    except Exception as e:
        print(f"❌ STOP: Gagal ambil gambar karena {e}")
        return # BERHENTI DI SINI jika gagal
    
    # 3. BUAT SUARA & SUBTITLE
    print("🎙️ Membuat suara...")
    try:
        audio_path, sub_path = await hasilkan_suara_dan_sub(naskah, "narasi")
        print("✅ Suara & Subtitle selesai")
    except Exception as e:
        print(f"❌ STOP: Gagal membuat audio karena {e}")
        return # BERHENTI DI SINI jika gagal
    
    # 4. RAKIT VIDEO
    print("🎬 Merakit video...")
    video_output = "output/final.mp4"
    os.makedirs("output", exist_ok=True)
    
    cmd = (
        f'ffmpeg -loop 1 -i "{img_path}" -i "{audio_path}" '
        f'-vf "subtitles={sub_path}:force_style=\'Alignment=2,FontSize=20\'" '
        f'-c:v libx264 -preset ultrafast -tune stillimage -c:a aac -shortest "{video_output}" -y'
    )
    
    hasil_ffmpeg = os.system(cmd)
    if hasil_ffmpeg != 0:
        print("❌ STOP: FFmpeg gagal merakit video")
        return # BERHENTI DI SINI jika gagal

    # 5. KIRIM KE TELEGRAM
    print("🚀 Mengirim ke Telegram...")
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendVideo"
    
    if os.path.exists(video_output):
        with open(video_output, "rb") as f:
            requests.post(url, data={"chat_id": chat_id, "caption": naskah}, files={"video": f})
        print("✅ SEMUA BERES!")
    else:
        print("❌ STOP: Video tidak ditemukan")

if __name__ == "__main__":
    asyncio.run(jalankan_otomatis())
    
