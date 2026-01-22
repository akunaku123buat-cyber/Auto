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

    # Menulis file SRT secara manual (Tanpa generate_subs)
    with open(path_sub, "w", encoding="utf-8") as f:
        for i, sub in enumerate(submaker.subs, 1):
            start, end = sub[0]
            teks_sub = sub[1]
            
            # Fungsi konversi waktu ke format SRT (00:00:00,000)
            def format_time(nanos):
                s = nanos / 10_000_000
                m, s = divmod(s, 60)
                h, m = divmod(m, 60)
                return f"{int(h):02}:{int(m):02}:{int(s):02},{int((s-int(s))*1000):03}"

            f.write(f"{i}\n{format_time(start)} --> {format_time(end)}\n{teks_sub}\n\n")
    
    return path_audio, path_sub
    
