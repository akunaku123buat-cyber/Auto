import requests
import os

def download_gambar(prompt, nama_file):
    # Membersihkan prompt agar bisa masuk ke URL (spasi jadi _)
    prompt_bersih = prompt.replace(" ", "_")
    
    # Ukuran 1080x1920 untuk YouTube Shorts
    url = f"https://image.pollinations.ai/prompt/{prompt_bersih}?width=1080&height=1920&nologo=true"
    
    print(f"Sedang mencarikan gambar untuk: {prompt}...")
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            # Pastikan folder assets ada
            if not os.path.exists("assets/images"):
                os.makedirs("assets/images")
                
            path_simpan = f"assets/images/{nama_file}.jpg"
            with open(path_simpan, "wb") as f:
                f.write(response.content)
            print(f"✅ Sukses! Gambar disimpan di: {path_simpan}")
            return path_simpan
        else:
            print("❌ Gagal mengambil gambar dari server.")
    except Exception as e:
        print(f"❌ Terjadi error: {e}")

if __name__ == "__main__":
    tema = input("Mau gambar tentang apa? ")
    download_gambar(tema, "background_utama")
