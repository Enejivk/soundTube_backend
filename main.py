from fastapi import FastAPI, Form, BackgroundTasks, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os
import uuid
import re
import time
from threading import Lock

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def remove_file(path: str):
    try:
        os.remove(path)
    except Exception:
        pass

RATE_LIMIT = 5  
RATE_PERIOD = 60 

rate_limit_data = {}
rate_limit_lock = Lock()


def is_rate_limited(client_ip):
    now = time.time()
    with rate_limit_lock:
        data = rate_limit_data.get(client_ip, [])
        data = [t for t in data if now - t < RATE_PERIOD]
        if len(data) >= RATE_LIMIT:
            rate_limit_data[client_ip] = data
            return True
        data.append(now)
        rate_limit_data[client_ip] = data
        return False



@app.post("/download_audio/")
async def download_audio(
    background_tasks: BackgroundTasks,
    url: str = Form(...),
    request: Request = None
):
    
    client_ip = request.client.host if request else "unknown"
    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too Many Requests")
    
    with yt_dlp.YoutubeDL({}) as ydl:
        info = ydl.extract_info(url, download=False)
        
        title = info.get('title')
        print(title)
        safe_title = sanitize_filename(title)
        output_filename = f"{safe_title}.mp3"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': safe_title,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    background_tasks.add_task(remove_file, output_filename)
    return FileResponse(output_filename, media_type="audio/mpeg", filename=output_filename)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", reload=True)