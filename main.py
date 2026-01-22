import asyncio
import os
import requests
import google.generativeai as genai
from jpg import download_gambar
from mp3 import hasilkan_suara_dan_sub

async def jalankan_otomatis():
    # Ambil Kunci dari Secrets GitHub
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 1. Buat Naskah
    print("✍️ Membuat naskah...")
    res = model.generate_content("Buatkan 1 kalimat motivasi singkat (max 15 kata) untuk TikTok.")
    naskah = res.text.strip()
    
    # 2. Buat Gambar & Audio (Memanggil file jpg.py dan mp3.py)
    print("🎨 Mengunduh gambar...")
    img_path = download_gambar(naskah, "bg_utama")
    
    print("🎙️ Membuat suara...")
    audio_path, sub_path = await hasilkan_suara_dan_sub(naskah, "narasi")
    
    # 3. Rakit Video pakai FFmpeg (Cara paling ringan untuk server GitHub)
    print("🎬 Merakit video...")
    video_output = "output/final.mp4"
    os.makedirs("output", exist_ok=True)
    
    cmd = (
        f'ffmpeg -loop 1 -i "{img_path}" -i "{audio_path}" '
        f'-vf "subtitles={sub_path}:force_style=\'Alignment=2,FontSize=20\'" '
        f'-c:v libx264 -preset ultrafast -tune stillimage -c:a aac -shortest "{video_output}" -y'
    )
    os.system(cmd)
    
    # 4. Kirim ke Telegram
    print("🚀 Mengirim ke Telegram...")
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendVideo"
    
    with open(video_output, "rb") as f:
        requests.post(url, data={"chat_id": chat_id, "caption": naskah}, files={"video": f})
    print("✅ Berhasil!")

if __name__ == "__main__":
    asyncio.run(jalankan_otomatis())
