import asyncio
import os
import requests
import google.generativeai as genai
import time
from jpg import download_gambar
from mp3 import hasilkan_suara_dan_sub

# Fungsi bantuan untuk kirim pesan teks ke Telegram
def kirim_notif(pesan):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": pesan})
    except:
        pass

async def jalankan_otomatis():
    # Inisialisasi
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    kirim_notif("🤖 Bot dimulai: Sedang membuat naskah...")

    # 1. BUAT NASKAH
    try:
        res = model.generate_content("Buatkan 1 kalimat motivasi singkat (max 15 kata) untuk TikTok.")
        naskah = res.text.strip()
        if not naskah: raise ValueError("Naskah kosong")
        print(f"✅ Naskah: {naskah}")
    except Exception as e:
        kirim_notif(f"❌ STOP: Gagal membuat naskah. Error: {e}")
        return

    # 2. BUAT GAMBAR
    kirim_notif("🎨 Sedang mengunduh gambar background...")
    try:
        img_path = download_gambar(naskah, "bg_utama")
        if not os.path.exists(img_path): raise FileNotFoundError("Gambar tidak ditemukan")
    except Exception as e:
        kirim_notif(f"❌ STOP: Gagal ambil gambar. Error: {e}")
        return
    
    # 3. BUAT SUARA & SUBTITLE
    kirim_notif("🎙️ Sedang memproses suara AI dan subtitle...")
    try:
        audio_path, sub_path = await hasilkan_suara_dan_sub(naskah, "narasi")
    except Exception as e:
        kirim_notif(f"❌ STOP: Gagal buat audio/sub. Error: {e}")
        return
    
    # 4. RAKIT VIDEO
    kirim_notif("🎬 Sedang merakit video dengan FFmpeg (ini butuh waktu)...")
    video_output = "output/final.mp4"
    os.makedirs("output", exist_ok=True)
    
    # Perintah FFmpeg yang lebih stabil
    cmd = (
        f'ffmpeg -y -loop 1 -t 10 -i "{img_path}" -i "{audio_path}" '
        f'-vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,subtitles={sub_path}" '
        f'-c:v libx264 -preset ultrafast -tune stillimage -c:a aac -b:a 192k -shortest "{video_output}"'
    )
    
    if os.system(cmd) != 0:
        kirim_notif("❌ STOP: FFmpeg gagal merakit video.")
        return

    # 5. KIRIM VIDEO KE TELEGRAM
    kirim_notif("🚀 Video selesai dirakit! Sedang mengirim ke kamu...")
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url_video = f"https://api.telegram.org/bot{token}/sendVideo"
    
    try:
        if os.path.exists(video_output):
            with open(video_output, "rb") as f:
                r = requests.post(url_video, data={"chat_id": chat_id, "caption": naskah}, files={"video": f}, timeout=60)
            if r.status_code == 200:
                kirim_notif("✅ BERHASIL! Video sudah dikirim.")
            else:
                kirim_notif(f"❌ Gagal kirim video ke Telegram: {r.text}")
        else:
            kirim_notif("❌ STOP: File video final tidak ditemukan.")
    except Exception as e:
        kirim_notif(f"❌ STOP: Terjadi kesalahan saat pengiriman. Error: {e}")

if __name__ == "__main__":
    asyncio.run(jalankan_otomatis())
    
