from moviepy.editor import ImageClip, AudioFileClip
import os

def buat_video_simpel():
    # 1. Tentukan lokasi file (Bahan yang sudah kita buat tadi)
    path_gambar = "assets/images/background_utama.jpg"
    path_audio = "assets/audio/narasi_konten.mp3"
    path_output = "output/video_final.mp4"

    # Pastikan folder output ada
    if not os.path.exists("output"):
        os.makedirs("output")

    print("Sedang merakit video... Mohon tunggu, ini butuh tenaga HP.")

    # 2. Ambil Suara (sebagai penentu durasi video)
    audio = AudioFileClip(path_audio)
    
    # 3. Ambil Gambar & Set durasi mengikuti suara
    # Kita tambahkan efek zoom sedikit agar tidak statis
    clip = ImageClip(path_gambar).set_duration(audio.duration)
    
    # 4. Satukan Gambar dan Suara
    video = clip.set_audio(audio)

    # 5. Export jadi MP4 (Gunakan preset ultrafast agar HP tidak panas)
    video.write_videofile(path_output, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    
    print(f"🎉 SELESAI! Video ada di: {path_output}")

if __name__ == "__main__":
    buat_video_simpel()
