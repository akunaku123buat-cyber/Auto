#!/bin/bash

# Buat folder yang dibutuhkan jika belum ada
mkdir -p assets
mkdir -p output

# Jalankan script satu per satu
python3 jpg.py
python3 mp3.py
python3 mp4.py

echo "Proses selesai, video siap di output/"

