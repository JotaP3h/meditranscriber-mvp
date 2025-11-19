# MediTranscriber MVP

MVP local para gravar áudio no navegador, diarizar (separar falantes), transcrever (Whisper) e montar relatório SOAP.

## Pré-requisitos
- Python 3.10+
- FFmpeg no PATH
- Token Hugging Face com READ (HF_TOKEN)

## Instalação (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Se usar GPU CUDA 12.1, instale torch pela index dedicada (ajuste conforme sua GPU)
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Defina o token do HF (substitua pelo seu)
setx HF_TOKEN "hf_xxx_seu_token_aqui"
```

## Rodar
```powershell
.\.venv\Scripts\activate
uvicorn app:app --reload
```
Abra http://localhost:8000/ui
