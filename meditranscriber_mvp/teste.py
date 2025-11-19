import soundfile as sf
import numpy as np
from faster_whisper import WhisperModel

# leia seu áudio (de preferência WAV 16k mono)
audio, sr = sf.read("entrada.wav", dtype="float32", always_2d=False)
if audio.ndim == 2:  # stereo -> mono
    audio = audio.mean(axis=1)

# carregue o modelo (troque "medium" por "large-v3" quando quiser)
model = WhisperModel("medium", compute_type="float32")

segments, info = model.transcribe(audio, language="pt", vad_filter=True)

print("Idioma:", info.language, "conf:", round(info.language_probability, 3))
for s in segments:
    print(f"[{s.start:.2f} -> {s.end:.2f}] {s.text}")
