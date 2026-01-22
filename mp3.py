import asyncio
import edge_tts
import os

async def hasilkan_suara(teks, nama_file):
    # Kita pakai suara 'id-ID-ArdiNeural' (Pria) atau 'id-ID-GadisNeural' (Wanita)
    VOICE = "id-ID-ArdiNeural" 
    path_simpan = f"assets/audio/{nama_file}.mp3"
    
    # Pastikan folder audio ada
    if not os.path.exists("assets/audio"):
        os.makedirs("assets/audio")

    print(f"Sedang merubah teks jadi suara...")
    communicate = edge_tts.Communicate(teks, VOICE)
    await communicate.save(path_simpan)
    print(f"✅ Suara siap: {path_simpan}")
    return path_simpan

if __name__ == "__main__":
    naskah = input("Masukkan naskah motivasi: ")
    asyncio.run(hasilkan_suara(naskah, "narasi_konten"))
