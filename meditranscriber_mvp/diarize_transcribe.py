from dotenv import load_dotenv
load_dotenv()

import os
import subprocess
import tempfile
from typing import List, Dict, Any

from faster_whisper import WhisperModel
from pyannote.audio import Pipeline
from role_classifier import label_speaker_roles

HF_TOKEN = os.getenv("HF_TOKEN")

# Modelos
WHISPER_MODEL_NAME = "medium"          # small | medium | large-v3
WHISPER_COMPUTE_TYPE = "float16"       # 'int8' p/ CPU, 'float16' p/ GPU

DIARIZATION_MODEL = "pyannote/speaker-diarization-3.1"

_whisper = None
_diar = None

def get_whisper():
    global _whisper
    if _whisper is None:
        _whisper = WhisperModel(WHISPER_MODEL_NAME, compute_type=WHISPER_COMPUTE_TYPE)
    return _whisper

def get_diar():
    global _diar
    if _diar is None:
        if not HF_TOKEN:
            raise RuntimeError("Defina a variável de ambiente HF_TOKEN para usar pyannote.")
        _diar = Pipeline.from_pretrained(DIARIZATION_MODEL, use_auth_token=HF_TOKEN)
    return _diar

def ensure_wav16k(input_path: str) -> str:
    out_path = tempfile.mktemp(suffix=".wav")
    cmd = ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", out_path]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path

def diarize(audio_path: str) -> List[Dict[str, Any]]:
    diar = get_diar()
    diarization = diar(audio_path)
    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "speaker": speaker,
            "start": float(turn.start),
            "end": float(turn.end)
        })
    segments.sort(key=lambda x: x["start"])
    return segments

def transcribe(audio_path: str) -> List[Dict[str, Any]]:
    model = get_whisper()
    segments, _ = model.transcribe(audio_path, language="pt", vad_filter=True, vad_parameters=dict(min_silence_duration_ms=200))
    out = []
    for s in segments:
        out.append({
            "start": float(s.start),
            "end": float(s.end),
            "text": s.text.strip()
        })
    return out

def align_speech(diar_segs, asr_segs) -> List[Dict[str, Any]]:
    aligned = []
    for a in asr_segs:
        best_label = None
        best_overlap = 0.0
        for d in diar_segs:
            start = max(a["start"], d["start"])
            end = min(a["end"], d["end"])
            overlap = max(0.0, end - start)
            if overlap > best_overlap:
                best_overlap = overlap
                best_label = d["speaker"]
        aligned.append({**a, "speaker": best_label or "UNKNOWN"})
    return aligned

def process_audio(input_path: str) -> Dict[str, Any]:
    wav = ensure_wav16k(input_path)
    diar_segs = diarize(wav)
    asr_segs  = transcribe(wav)
    aligned   = align_speech(diar_segs, asr_segs)

    speaker_roles = label_speaker_roles(aligned)
    segments_by_role = {"Médico": [], "Paciente": []}
    for seg in aligned:
        role = speaker_roles.get(seg["speaker"], "Paciente")
        segments_by_role[role].append(seg)

    return {
        "diarization": diar_segs,
        "segments": aligned,
        "segments_by_role": segments_by_role
    }
