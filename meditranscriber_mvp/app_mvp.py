# ===== Shim Numpy (alguns pacotes antigos usam np.NaN) =====
import numpy as _np
if not hasattr(_np, "NaN"):
    _np.NaN = _np.nan

# ===== Imports =====
import io
import os
import tempfile
from typing import List, Optional, Dict
from collections import defaultdict

import numpy as np
import soundfile as sf
from pydub import AudioSegment

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse

from dotenv import load_dotenv

# Melhoramento de áudio
import noisereduce as nr
from scipy.signal import butter, lfilter

# Para evitar erro de OpenMP duplicado no Windows (mensagem do libiomp5md)
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

# ===== Ambiente (.env) =====
load_dotenv()

# ===== App =====
app = FastAPI(title="MediTranscriber MVP", version="0.1.0")

# ===== Dispositivo =====
DEVICE = "cuda" if os.environ.get("USE_CUDA", "1") == "1" else "cpu"

# ===== Whisper (não usar token do HF) =====
# Evita que huggingface_hub injete Authorization em modelos públicos
for bad in ("HUGGINGFACE_TOKEN", "HUGGINGFACE_HUB_TOKEN", "HF_TOKEN"):
    if bad in os.environ:
        os.environ.pop(bad, None)

from faster_whisper import WhisperModel
_compute_type = "int8_float16" if DEVICE == "cuda" else "int8"
_whisper_model = WhisperModel("medium", device=DEVICE, compute_type=_compute_type)

# ===== Pyannote (diarização) =====
from pyannote.audio import Pipeline
# Aceita tanto HF_PYANNOTE_TOKEN quanto HUGGINGFACE_TOKEN
HF_PYANNOTE_TOKEN = os.environ.get("HF_PYANNOTE_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN") or ""
DIAR_MODEL = os.environ.get("PYANNOTE_DIARIZATION_MODEL", "pyannote/speaker-diarization-3.1")

_diar_pipeline = None
try:
    if HF_PYANNOTE_TOKEN:
        _d = Pipeline.from_pretrained(DIAR_MODEL, use_auth_token=HF_PYANNOTE_TOKEN)
    else:
        # modelos "gated" exigem token; sem token tentamos assim mesmo
        _d = Pipeline.from_pretrained(DIAR_MODEL)
    _diar_pipeline = _d
    print("[OK] Pyannote diarization pipeline carregado.")
except Exception as e:
    print(f"[AVISO] Pyannote indisponível ({DIAR_MODEL}): {e}")

# ===== Utils =====

def convert_to_wav_16k_mono(file_bytes: bytes) -> np.ndarray:
    """
    Converte MP3/M4A/WAV/etc para array float32 mono 16 kHz.
    Requer ffmpeg no PATH para o pydub.
    """
    audio = AudioSegment.from_file(io.BytesIO(file_bytes))
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    buf = io.BytesIO()
    audio.export(buf, format="wav")
    buf.seek(0)

    y, sr = sf.read(buf, dtype="float32", always_2d=False)
    if y.ndim == 2:
        y = y.mean(axis=1)
    return y

def butter_highpass(cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="high", analog=False)
    return b, a

def highpass_filter(y: np.ndarray, sr: int, cutoff: float = 80.0) -> np.ndarray:
    b, a = butter_highpass(cutoff, sr, order=4)
    return lfilter(b, a, y)

def enhance_audio(y: np.ndarray, sr: int = 16000) -> np.ndarray:
    """
    1) High-pass leve
    2) Noise reduction espectral
    3) Normalização de pico
    """
    y_hp = highpass_filter(y, sr, cutoff=80.0)
    y_nr = nr.reduce_noise(y_hp, sr=sr, prop_decrease=0.8, stationary=False)
    peak = float(np.max(np.abs(y_nr)) + 1e-9)
    y_nr = (y_nr / peak) * 0.95
    return y_nr.astype("float32")

def to_temp_wav(y: np.ndarray, sr: int = 16000) -> str:
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    sf.write(path, y, sr)
    return path

def who_speaks_for_interval(t_start: float, t_end: float, segs: List[Dict]) -> str:
    """Escolhe o speaker do centro do intervalo; fallback para o mais próximo."""
    mid = 0.5 * (t_start + t_end)
    candidates = [s for s in segs if s["start"] <= mid <= s["end"]]
    if candidates:
        return candidates[0]["speaker"]
    if segs:
        return min(segs, key=lambda s: abs((s["start"] + s["end"]) / 2 - mid))["speaker"]
    return "SPEAKER_00"

# ===== Heurística de papéis (médico x paciente) =====

def _score_medico(text: str) -> float:
    """Heurística simples: quanto maior, mais provável ser MÉDICO."""
    t = text.lower()

    keys_med = {
        "vamos": 1.0, "vou": 0.8, "precisa": 1.2, "deve": 1.0, "oriento": 1.5,
        "exame": 1.6, "solicitar": 1.6, "prescrever": 1.8, "receitar": 1.8,
        "medicação": 1.4, "remédio": 1.2, "dosagem": 1.5, "posologia": 1.6,
        "diagnóstico": 1.6, "hipótese": 1.6, "anamnese": 2.0,
        "pressão": 1.3, "frequência cardíaca": 1.4, "saturação": 1.4,
        "retorno": 0.9, "encaminhar": 1.3, "especialista": 1.2,
        "há quanto tempo": 1.8, "desde quando": 1.8, "melhora ou piora": 1.8,
        "alergia": 1.2, "histórico": 1.2, "antecedente": 1.2,
    }
    keys_pac = {
        "eu": -0.4, "estou": -0.6, "tô": -0.6, "tenho": -0.6, "sinto": -0.8,
        "minha": -0.5, "meu": -0.5, "dor": -0.6, "desde ontem": -0.8,
        "melhorou": -0.5, "piorou": -0.5, "falta de ar": -0.6, "enjoo": -0.6,
    }
    score = 0.0
    for k, w in keys_med.items():
        if k in t:
            score += w
    for k, w in keys_pac.items():
        if k in t:
            score += w
    score += t.count("?") * 0.6  # médico costuma perguntar mais
    imperativos = ["respire", "mostre", "tome", "faça", "evite", "retorne", "traga"]
    score += sum(1 for k in imperativos if k in t) * 0.8
    return score

def _auto_assign_roles(transcribed_segments: List[Dict]) -> Dict[str, str]:
    """
    Recebe segments com 'speaker' e 'text' e retorna um mapa:
      ex.: {'SPEAKER_01': 'medico', 'SPEAKER_00': 'paciente'}
    """
    agg = defaultdict(list)
    for s in transcribed_segments:
        agg[s["speaker"]].append(s["text"])
    per_speaker_text = {spk: " ".join(txts) for spk, txts in agg.items()}

    if not per_speaker_text:
        return {}

    scores = {spk: _score_medico(txt) for spk, txt in per_speaker_text.items()}
    medico_spk = max(scores.items(), key=lambda kv: kv[1])[0]
    others = [s for s in scores.keys() if s != medico_spk]

    role_map = {medico_spk: "medico"}
    if others:
        role_map[others[0]] = "paciente"
    return role_map

# ===== Rotas =====

@app.get("/")
def root():
    return {
        "ok": True,
        "app": "MediTranscriber MVP",
        "device": DEVICE,
        "diarization_available": _diar_pipeline is not None
    }

@app.get("/health")
def health():
    return {"status": "healthy", "device": DEVICE}

@app.post("/enhance")
async def api_enhance(file: UploadFile = File(...)):
    data = await file.read()
    y = convert_to_wav_16k_mono(data)
    y_enh = enhance_audio(y, 16000)
    out_path = to_temp_wav(y_enh, 16000)
    return FileResponse(out_path, media_type="audio/wav", filename="enhanced.wav")

@app.post("/transcribe-diarize")
async def api_transcribe_diarize(
    file: UploadFile = File(...),
    language: Optional[str] = Form(default="pt"),
    vad_filter: bool = Form(default=True),
):
    """
    1) Converte e melhora o áudio
    2) Diariza com pyannote (se disponível)
    3) Transcreve com faster-whisper
    4) Faz matching simples e classifica automaticamente médico/paciente
    """
    data = await file.read()

    # 1) Converte -> 16k mono
    y = convert_to_wav_16k_mono(data)
    # 2) Melhoramento
    y = enhance_audio(y, 16000)
    # WAV temporário para pyannote
    wav_path = to_temp_wav(y, 16000)

    # 3) Diarização
    diar_segments: List[Dict] = []
    try:
        if _diar_pipeline is not None:
            diar = _diar_pipeline(wav_path)  # Annotation
            for turn, _, speaker in diar.itertracks(yield_label=True):
                diar_segments.append({
                    "start": round(float(turn.start), 2),
                    "end": round(float(turn.end), 2),
                    "speaker": str(speaker),
                })
        else:
            diar_segments = [{"start": 0.0, "end": round(len(y)/16000.0, 2), "speaker": "SPEAKER_00"}]
    finally:
        try:
            os.remove(wav_path)
        except Exception:
            pass

    # 4) Transcrição
    segments, info = _whisper_model.transcribe(y, language=language, vad_filter=vad_filter)

    # 5) Matching (centro do trecho)
    results = []
    for s in segments:
        spk = who_speaks_for_interval(float(s.start), float(s.end), diar_segments)
        results.append({
            "start": round(float(s.start), 2),
            "end": round(float(s.end), 2),
            "speaker": spk,
            "text": s.text.strip()
        })

    # 6) Classificação automática médico/paciente
    auto_map = _auto_assign_roles(results)
    for r in results:
        if r["speaker"] in auto_map:
            r["speaker"] = auto_map[r["speaker"]]

    return JSONResponse({
        "device": DEVICE,
        "language": info.language,
        "language_conf": float(info.language_probability),
        "diarization_available": _diar_pipeline is not None,
        "roles_map": auto_map,
        "segments": results
    })

@app.post("/tts")
async def api_tts(text: str = Form(...), voice: Optional[str] = Form(default=None)):
    """
    TTS simples offline com pyttsx3 (usa SAPI5 no Windows).
    """
    try:
        import pyttsx3
    except Exception as e:
        return JSONResponse({"error": f"pyttsx3 não instalado/indisponível: {e}"}, status_code=500)

    engine = pyttsx3.init()
    if voice:
        for v in engine.getProperty("voices"):
            if voice.lower() in (v.name.lower(), v.id.lower()):
                engine.setProperty("voice", v.id)
                break
    fd, out_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    engine.save_to_file(text, out_path)
    engine.runAndWait()
    return FileResponse(out_path, media_type="audio/wav", filename="tts.wav")
