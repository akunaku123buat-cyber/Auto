import asyncio
import edge_tts
import os

async def hasilkan_suara_dan_sub(teks, nama_file):
    VOICE = "id-ID-ArdiNeural"
    path_audio = f"assets/audio/{nama_file}.mp3"
    path_sub = f"assets/audio/{nama_file}.srt"
    
    os.makedirs("assets/audio", exist_ok=True)

    communicate = edge_tts.Communicate(teks, VOICE)
    submaker = edge_tts.SubMaker()

    with open(path_audio, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

    with open(path_sub, "w", encoding="utf-8") as f:
        f.write(submaker.generate_subs())
    
    return path_audio, path_sub
                        
