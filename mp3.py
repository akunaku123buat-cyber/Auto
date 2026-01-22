import asyncio
import edge_tts
import os

async def hasilkan_suara_dan_sub(teks, nama_file):
    VOICE = "id-ID-ArdiNeural"
    path_audio = f"assets/audio/{nama_file}.mp3"
    path_sub = f"assets/audio/{nama_file}.srt"
    
    os.makedirs("assets/audio", exist_ok=True)

    communicate = edge_tts.Communicate(teks, VOICE)
    subs_data = []

    with open(path_audio, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # Simpan data langsung dari stream untuk menghindari AttributeError
                subs_data.append({
                    "start": chunk["offset"],
                    "duration": chunk["duration"],
                    "text": chunk["text"]
                })

    # Menulis file SRT secara manual
    with open(path_sub, "w", encoding="utf-8") as f:
        for i, data in enumerate(subs_data, 1):
            start_time = data["start"]
            end_time = data["start"] + data["duration"]
            
            def format_time(nanos):
                s = nanos / 10_000_000
                m, s = divmod(s, 60)
                h, m = divmod(m, 60)
                return f"{int(h):02}:{int(m):02}:{int(s):02},{int((s-int(s))*1000):03}"

            f.write(f"{i}\n{format_time(start_time)} --> {format_time(end_time)}\n{data['text']}\n\n")
    
    return path_audio, path_sub
    
