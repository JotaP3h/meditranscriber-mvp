# 🩺 MediTranscriber MVP – Transcrição Médica com IA (Whisper + Pyannote)

MediTranscriber é um **MVP de GenAI** que transcreve consultas médicas a partir de áudios, usando:

- **Faster-Whisper** para transcrição automática (ASR)
- **Pyannote-audio** para diarização (separação de falantes)
- **FastAPI** como backend para expor tudo via API

O objetivo do projeto é demonstrar, na prática, o uso de **IA aplicada**, processamento de áudio e construção de APIs modernas – focado em cenários de saúde (HealthTech).

---

## ✨ Principais funcionalidades

- 🎙️ Upload de áudio de consulta (`.mp3`, `.wav`, etc.)
- 🧠 **Transcrição automática** do áudio em texto
- 👥 **Diarização**: separa diferentes falantes
- 🩻 Mapeamento de papéis (`médico` / `paciente`) via heurísticas
- 🔁 Retorno estruturado em **JSON**, pronto para prontuário ou análise
- 📚 Documentação auto-gerada via **Swagger** (`/docs`)
- 🌐 Front-end simples (HTML/JS) para testes locais

---

## 🧱 Stack Tecnológica

- **Linguagem:** Python 3.10  
- **Framework Web:** FastAPI + Uvicorn  
- **Transcrição (ASR):** [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)  
- **Diarização:** [pyannote.audio](https://github.com/pyannote/pyannote-audio)  
- **Execução em GPU:** CUDA (quando disponível)  
- **Front-end de teste:** HTML + CSS + JavaScript simples  

---

## 🗂 Estrutura do projeto

```bash
Projeto_Medico_IA/
├── meditranscriber_mvp/
│   ├── app_mvp.py            # App FastAPI principal
│   ├── app.py                # Versão alternativa / testes
│   ├── diarize_transcribe.py # Lógica de diarização + transcrição
│   ├── role_classifier.py    # Heurísticas p/ mapear médico/paciente
│   ├── report.py             # Geração/formatação de relatórios (MVP)
│   ├── uploads/
│   │   └── .gitkeep          # Pasta para arquivos enviados
│   └── web/
│       ├── index.html        # Front simples
│       ├── styles.css
│       └── app.js
│
├── requirements.txt          # Dependências do projeto
└── README.md                 # Este arquivo

