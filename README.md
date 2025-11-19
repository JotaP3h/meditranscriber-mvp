
---

# **📄 README.md (COMPLETO — COPIE EXATAMENTE COMO ESTÁ)**

```markdown
# 🩺🧠 MediTranscriber MVP – Transcrição Médica com IA (Whisper + Pyannote)

MediTranscriber é um **MVP de GenAI** que transcreve consultas médicas a partir de áudios, usando:

- **Faster-Whisper** para transcrição automática (ASR)  
- **Pyannote-audio** para diarização (separação de falantes)  
- **FastAPI** como backend para expor tudo via API  

O objetivo do projeto é demonstrar, na prática, o uso de **IA aplicada**, processamento de áudio e construção de APIs modernas — focado em cenários de saúde (HealthTech).

---

## ✨ Principais funcionalidades

- 🎤 Upload de áudio de consulta (`.mp3`, `.wav`, etc.)
- 🧠 **Transcrição automática** do áudio em texto
- 👥 **Diarização**: separa diferentes falantes
- 🩺 Mapeamento de papéis (**médico** / **paciente**) via heurísticas
- 📦 Retorno estruturado em **JSON**, pronto para prontuário ou análise
- 📄 Documentação auto-gerada via **Swagger** (`/docs`)
- 🌐 Front-end simples (HTML/JS) para testes locais

---

## 🧰 Stack Tecnológica

- **Linguagem:** Python 3.10  
- **Framework Web:** FastAPI + Uvicorn  
- **Transcrição (ASR):** Faster-Whisper  
- **Diarização:** pyannote.audio  
- **Execução com GPU:** CUDA (quando disponível)  
- **Front-end:** HTML + CSS + JavaScript simples  

---

## 📁 Estrutura do projeto

```

Projeto_Medico_IA/
│
└── meditranscriber_mvp/
├── app_mvp.py              # App FastAPI principal
├── app.py                  # Versão alternativa / testes
├── diarize_transcribe.py   # Lógica de diarização + transcrição
├── role_classifier.py      # Heurísticas para identificar médico/paciente
├── report.py               # Saída estruturada / exportações
├── uploads/                # Áudios enviados
├── web/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── requirements.txt
└── .gitignore

````

---

## 🚀 Como rodar localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/JotaP3h/meditranscriber-mvp.git
cd meditranscriber-mvp
````

---

### 2. Criar e ativar o ambiente virtual

**Windows (PowerShell):**

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/Mac:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

⚠️ *Whisper + Pyannote são pesados. Em PCs sem GPU funciona, mas mais devagar.*

---

### 4. Rodar o servidor FastAPI

```bash
uvicorn meditranscriber_mvp.app_mvp:app --reload
```

Saída esperada:

```
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

---

### 5. Acessar documentação da API

* Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Redoc → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔌 Endpoints principais

### **GET /**

```json
{
  "ok": true,
  "app": "MediTranscriber MVP",
  "device": "cuda",
  "diarization_available": true
}
```

---

### **POST /transcribe-diarize**

Multipart/form-data:

* `file` → áudio
* `language` (opcional)
* `vad_filter` (opcional)

Exemplo de resposta:

```json
{
  "device": "cuda",
  "language": "pt",
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
```

---

## 🌐 Front-end simples

Pasta:

```
meditranscriber_mvp/web/
```

Abra:

```
index.html
```

---

## ⚠️ Limitações do MVP

* Classificação médico/paciente ainda é por heurística
* Pyannote pode errar falantes dependendo do áudio
* Sem GPU, processamento mais lento
* MVP não é validado para uso clínico real

---

## 🧭 Próximos passos

* Melhorar heurísticas
* Exportação em **PDF / DOCX**
* Criar painel web com histórico
* Autenticação (JWT)
* Banco de dados (PostgreSQL)
* Docker + deploy

---

## 👨‍💻 Autor

**João Pedro Freitas (JotaP3h)**

* GitHub: [https://github.com/JotaP3h](https://github.com/JotaP3h)
* LinkedIn: *(adicione quando quiser)*
