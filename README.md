🩺 MediTranscriber — MVP de Transcrição Médica com IA (Whisper + Pyannote)

O MediTranscriber é um MVP de GenAI que transcreve consultas médicas a partir de áudios, separa falas entre médico e paciente, e retorna um JSON estruturado — pronto para análise, prontuário ou automação.

Ele usa:

🚀 Faster-Whisper — Transcrição automática otimizada

🎙 Pyannote-audio — Diarização (quem falou o quê)

⚡ FastAPI — API moderna com Swagger

🧠 Classificação automática médico × paciente

Criado como projeto de portfólio para demonstrar experiência prática em IA aplicada, processamento de áudio, Python e APIs modernas.

🔥 Funcionalidades principais

Upload de áudio de consulta (.mp3, .wav, .m4a, etc.)

Transcrição automática do áudio

Diarização com identificação de falantes

Classificação automática dos papéis

Retorno estruturado em JSON

Documentação via Swagger

Front-end simples HTML/JS

Suporte a GPU (CUDA) e CPU

🧰 Stack Tecnológica

Python 3.10

FastAPI + Uvicorn

Faster-Whisper

Pyannote-audio

Torch / Torchaudio

HTML + CSS + JavaScript (Front-end simples)

🗂 Estrutura do Projeto
meditranscriber-mvp/
│
├── README.md
├── requirements.txt
│
├── meditranscriber_mvp/
│   ├── app_mvp.py
│   ├── app.py
│   ├── diarize_transcribe.py
│   ├── role_classifier.py
│   ├── report.py
│   ├── teste.py
│   ├── run.ps1
│   ├── uploads/
│   │   └── .gitkeep
│   └── web/
│       ├── index.html
│       ├── styles.css
│       └── app.js

🚀 Como rodar localmente
1. Clonar o repositório
git clone https://github.com/JotaP3h/meditranscriber-mvp.git
cd meditranscriber-mvp

2. Criar e ativar ambiente virtual (opcional)

Windows:

python -m venv .venv
.\.venv\Scripts\Activate.ps1


Linux/Mac:

python3 -m venv .venv
source .venv/bin/activate

3. Instalar dependências
pip install -r requirements.txt

4. Rodar API FastAPI
uvicorn meditranscriber_mvp.app_mvp:app --reload


Acesse:

Swagger: http://127.0.0.1:8000/docs

Redoc: http://127.0.0.1:8000/redoc

🔌 Endpoints principais
GET /
{
  "ok": true,
  "app": "MediTranscriber MVP",
  "device": "cuda",
  "diarization_available": true
}

POST /transcribe-diarize

Multipart/form-data:

file → áudio

language → "pt"

vad_filter → true/false

Retorno (exemplo):

{
  "roles_map": {
    "SPEAKER_00": "medico",
    "SPEAKER_01": "paciente"
  },
  "segments": [
    {
      "start": 0.62,
      "end": 3.62,
      "speaker": "medico",
      "text": "Olá, boa tarde, tudo bem?"
    }
  ]
}

🎧 Front-end simples (web)

Dentro de:

meditranscriber_mvp/web/


Basta abrir index.html no navegador.

⚠️ Limitações do MVP

Classificação de papéis ainda é heurística simples

Pyannote é pesado e o primeiro load leva tempo

Sem GPU pode ser lento para áudios longos

MVP não destinado ao uso clínico real

🧭 Próximos Passos

Melhorar modelo de classificação de papéis

Exportar para PDF / DOCX

Criar dashboard para histórico de transcrições

Adicionar autenticação JWT

Integração com banco de dados

Criar demo no HuggingFace Spaces

Containerizar com Docker

👨‍💻 Autor

João Pedro Freitas (JotaP3h)
Estudante de Sistemas de Informação, ex-empreendedor e entusiasta de IA aplicada a saúde, automação e produtividade.

🔗 GitHub: https://github.com/JotaP3h

🔗 LinkedIn: https://www.linkedin.com/in/joao-freitas-e-silva/
