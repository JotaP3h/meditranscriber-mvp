# Ativa o venv e roda o servidor
$env:PYTHONUTF8=1
.\.venv\Scripts\activate
uvicorn app:app --reload
