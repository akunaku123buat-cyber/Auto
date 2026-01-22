import requests
import os
from google import genai

def buat_prompt_gambar(naskah):
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    prompt_ai = f"Based on this script: '{naskah}', create a high-quality cinematic image prompt. focus on atmosphere, no text, 4k, portrait orientation."
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_ai
    )
    return response.text

def download_gambar(naskah, nama_file):
    prompt_keren = buat_prompt_gambar(naskah)
    # Bersihkan prompt agar bisa jadi URL yang valid
    prompt_url = prompt_keren.replace(" ", "_").replace("\n", "").replace('"', '').replace("'", "")[:500]
    
    url = f"https://image.pollinations.ai/prompt/{prompt_url}?width=1080&height=1920&nologo=true"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            os.makedirs("assets/images", exist_ok=True)
            path_simpan = f"assets/images/{nama_file}.jpg"
            with open(path_simpan, "wb") as f:
                f.write(response.content)
            return path_simpan
    except Exception as e:
        print(f"Gagal buat gambar: {e}")
    return None
                
