from fastapi import FastAPI, Form, BackgroundTasks, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os
import re
import time
from threading import Lock

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


# sanitize filename
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)


# cleanup task
def remove_file(path: str):
    try:
        os.remove(path)
    except Exception:
        pass


# Rate limiting setup
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

    # yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }

    # Download + get metadata
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url) 
        title = info.get("title", "audio")
        safe_title = sanitize_filename(title)
        output_filename = f"{safe_title}.mp3"
        print(f"Expected file: {output_filename}")
        
        # Find the actual file that was downloaded
        # The file might include the YouTube ID in square brackets
        actual_file = None
        for file in os.listdir('.'):
            if file.endswith('.mp3') and safe_title in file:
                actual_file = file
                print(f"Found matching file: {actual_file}")
                break
        
        # If we found a matching file, use it instead
        if actual_file:
            output_filename = actual_file

    # Verify file exists before trying to serve it
    if not os.path.exists(output_filename):
        raise HTTPException(status_code=404, detail=f"Audio file not found: {output_filename}")

    # cleanup task
    background_tasks.add_task(remove_file, output_filename)

    # return file with correct title
    return FileResponse(
        path=output_filename,
        media_type="audio/mpeg",
        filename=f"{safe_title}.mp3" 
    )


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", reload=True)
