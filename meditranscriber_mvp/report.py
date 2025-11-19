from typing import Dict, List

def join_text(segments: List[dict]) -> str:
    return " ".join(s["text"] for s in segments).strip()

def extract_items(text: str, keywords: list) -> List[str]:
    t = text.lower()
    return list({k for k in keywords if k in t})

def build_report(segments_by_role: Dict[str, List[dict]]) -> Dict:
    paciente_txt = join_text(segments_by_role.get("Paciente", []))
    medico_txt   = join_text(segments_by_role.get("Médico", []))
    full_txt     = (paciente_txt + " " + medico_txt).strip()

    queixa = paciente_txt or "(sem texto suficiente do paciente)"
    observacoes = medico_txt or "(sem observações do médico)"

    sinais = extract_items(full_txt, ["febre", "tosse", "dor", "dispneia", "náusea", "vômito", "diarreia", "cefaleia"])
    exames = extract_items(full_txt, ["hemograma", "raio-x", "radiografia", "ressonância", "tomografia", "urocultura"])
    meds   = extract_items(full_txt, ["dipirona", "amoxicilina", "ibuprofeno", "paracetamol", "azitromicina", "metformina"])
    conduta_keywords = extract_items(full_txt, ["repouso", "hidratação", "analgésico", "antibiótico", "anti-inflamatório", "fisioterapia"])

    report = {
        "S": {
            "Queixa principal": queixa,
            "História/Contexto (resumo)": paciente_txt[:600] + ("..." if len(paciente_txt) > 600 else "")
        },
        "O": {
            "Observações do médico (resumo)": observacoes[:600] + ("..." if len(observacoes) > 600 else ""),
            "Sinais/Sintomas citados": sinais or []
        },
        "A": {
            "Hipóteses (indícios a partir do texto)": "—"
        },
        "P": {
            "Conduta citada": conduta_keywords or [],
            "Exames citados": exames or [],
            "Medicações citadas": meds or [],
            "Follow-up sugerido": "Retorno se piora ou em 7–14 dias (ajuste conforme protocolo)."
        }
    }
    return report
