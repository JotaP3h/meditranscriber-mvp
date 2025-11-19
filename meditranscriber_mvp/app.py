from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
from diarize_transcribe import process_audio
from report import build_report

app = FastAPI(title="MediTranscriber MVP")

# Serve UI
app.mount("/ui", StaticFiles(directory="web", html=True), name="ui")

AUDIO_DIR = "uploads"
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.get("/")
def root():
    return JSONResponse({"ok": True, "msg": "Use /ui para a interface"})

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower() or ".webm"
    tmp_path = os.path.join(AUDIO_DIR, f"{uuid.uuid4().hex}{ext}")
    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    result = process_audio(tmp_path)
    report = build_report(result["segments_by_role"])

    return JSONResponse({
        "ok": True,
        "audio_file": os.path.basename(tmp_path),
        "diarization": result["diarization"],
        "segments": result["segments"],
        "segments_by_role": result["segments_by_role"],
        "report": report
    })

@app.get("/download/{fname}")
def download(fname: str):
    path = os.path.join(AUDIO_DIR, fname)
    if not os.path.exists(path):
        return JSONResponse({"ok": False, "error": "Arquivo não encontrado"}, status_code=404)
    return FileResponse(path, media_type="audio/wav", filename=fname)
