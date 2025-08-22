#!/bin/bash
cd "$(dirname "$0")"   # go into the script's folder
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 9
