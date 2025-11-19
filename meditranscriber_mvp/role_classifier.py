from typing import Dict, List

MEDICO_CUES = {
    "prescrever", "prescrição", "dosagem", "posologia", "exame", "solicitar exame",
    "encaminhamento", "hipótese", "diagnóstico", "diagnosticar", "tratamento",
    "conduta", "retorno", "anamnese", "antibiótico", "anti-inflamatório",
    "resultado", "laudo", "radiografia", "ressonância", "tomografia",
    "pressão", "saturação", "frequência cardíaca", "medicação", "atestado"
}

PACIENTE_CUES = {
    "dor", "doendo", "sinto", "tô", "estou", "febre", "enjoo", "náusea", "cansaço",
    "minha", "meu", "minhas", "meus", "acho", "penso", "medo", "preocupado",
    "melhorou", "piorou", "não consigo", "não aguento"
}

def score_text(text: str, cues: set) -> int:
    t = text.lower()
    return sum(1 for c in cues if c in t)

def label_speaker_roles(segments: List[dict]) -> Dict[str, str]:
    per_spk = {}
    for s in segments:
        spk = s.get("speaker", "UNKNOWN")
        txt = s.get("text", "")
        m = score_text(txt, MEDICO_CUES)
        p = score_text(txt, PACIENTE_CUES)
        q = 1 if txt.endswith("?") else 0
        per_spk.setdefault(spk, {"m": 0, "p": 0, "q": 0})
        per_spk[spk]["m"] += m
        per_spk[spk]["p"] += p
        per_spk[spk]["q"] += q

    mapping = {}
    sorted_spk = sorted(per_spk.items(), key=lambda kv: ((kv[1]["m"] - kv[1]["p"]), kv[1]["q"]), reverse=True)
    if sorted_spk:
        mapping[sorted_spk[0][0]] = "Médico"
    for spk, _ in per_spk.items():
        mapping.setdefault(spk, "Paciente")
    return mapping
