#!/bin/bash

echo "🚀 Memulai proses pembuatan konten otomatis..."

# 1. Ambil Gambar
echo "🎨 Step 1: Mengambil Gambar AI..."
python jpg.py

# 2. Buat Suara
echo "🎙️ Step 2: Membuat Narasi Suara..."
python mp3.py

# 3. Rakit Video
echo "🎬 Step 3: Merakit Video MP4..."
python mp4.py

echo "✅ SELESAI! Video kamu siap di folder output."
