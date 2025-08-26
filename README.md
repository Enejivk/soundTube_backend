# SoundTube Backend

A FastAPI-based backend service for downloading audio from YouTube videos. This service provides a simple API endpoint that extracts audio from YouTube URLs and serves it as MP3 files.

## Features

- Extract audio from YouTube videos
- Rate limiting to prevent abuse (5 requests per minute per IP)
- Automatic file cleanup after download
- Cross-Origin Resource Sharing (CORS) enabled for frontend integration

## Requirements

- Python 3.9+
- FFmpeg (for audio extraction)
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Enejivk/soundTube_backend.git
cd soundTube_backend
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Make sure FFmpeg is installed on your system:
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## Usage

### Starting the server

You can start the server using the provided shell script:

```bash
chmod +x start.sh  # Make the script executable (first time only)
./start.sh
```

Or run it directly with Python:

```bash
uvicorn main:app --reload
```

The server will start on `http://localhost:8000` by default. The production setup in `start.sh` uses multiple workers and binds to all interfaces (`0.0.0.0`).

### API Endpoints

#### Download Audio

```
POST /download_audio/
```

**Parameters:**

- `url`: The YouTube video URL (form data)

**Response:**

- MP3 file download

**Rate Limiting:**

- 5 requests per minute per IP address

## Development

The application is built with FastAPI and uses yt-dlp for YouTube video processing.

Main components:

- `main.py`: Contains the FastAPI application and endpoints
- `start.sh`: Shell script to start the server with multiple workers

## License

[MIT](LICENSE)
