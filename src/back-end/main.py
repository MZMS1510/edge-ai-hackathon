#!/usr/bin/env python3
from typing import List
import re
import json
import os

# Try to import runtime dependencies; fall back to lightweight stubs so tests can run without installing
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import httpx
    import uvicorn
    HAS_DEPENDENCIES = True
except Exception:
    HAS_DEPENDENCIES = False
    # minimal stub for typing in tests: allow subclassing
    class BaseModel:  # minimal stub for typing in tests
        def __init__(self, **data):
            for k, v in data.items():
                setattr(self, k, v)

    class HTTPException(Exception):
        def __init__(self, status_code=None, detail=None):
            self.status_code = status_code
            self.detail = detail
            super().__init__(f"HTTPException {status_code}: {detail}")

    # Dummy app that supports decorator usage so module import doesn't fail when FastAPI is absent
    class DummyApp:
        def post(self, path, **kwargs):
            def decorator(func):
                return func

            return decorator

    def FastAPI(*args, **kwargs):
        return DummyApp()

    httpx = None
    uvicorn = None

app = FastAPI(title="Edge AI - Vícios de Linguagem Analyzer")


class AnalyzeRequest(BaseModel):
    text: str
    model: str = "llama2"  # default model name; change to your local model
    notes: List[str] = []  # optional points from other models (video analysis, ASR notes)
    transcript: str = ""  # optional full transcript from audio


class PhraseCount(BaseModel):
    phrase: str
    count: int
    examples: List[str]


class AnalyzeResponse(BaseModel):
    summary: str
    repetitions: List[PhraseCount]
    suggestions: List[str]
    feedback: str = ""  # combined textual feedback about the presentation


# Common Portuguese filler words / phrases to detect in local fallback analysis
COMMON_FILLERS = [
    "tipo",
    "né",
    "basicamente",
    "então",
    "aí",
    "assim",
    "tá",
    "ok",
    "hum",
    "quer dizer",
    "na verdade",
    "bom",
]

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")

# System prompt for the feedback model (strict: only communication skills)
SYSTEM_PROMPT = (
    "Você é um avaliador especializado exclusivamente em habilidades de comunicação de apresentadores. "
    "Gere feedback profissional e acionável sobre gesticulação, postura, contato visual (se disponível), tom de voz, "
    "intensidade/volume, velocidade de fala, pausas, vícios de linguagem, clareza articulatória, ritmo e energia. "
    "NÃO avalie conteúdo, ideias, produto, precisão factual ou qualidade técnica do roteiro. Baseie-se apenas nos dados "
    "fornecidos (transcript, vices, poses, audio_features, video_features, extra). Responda SOMENTE em JSON válido "
    "conforme o esquema esperado pelo serviço de feedback. Idioma: português (pt-BR)."
)


def local_filler_analysis(text: str) -> dict:
    lc = text.lower()
    reps = []
    # split into sentences for examples
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    for phrase in COMMON_FILLERS:
        pattern = r"\b" + re.escape(phrase) + r"\b"
        matches = re.findall(pattern, lc)
        if matches:
            examples = [s for s in sentences if phrase in s.lower()][:3]
            reps.append({"phrase": phrase, "count": len(matches), "examples": examples})
    suggestions = []
    if reps:
        suggestions.append(
            "Evite repetições e muletas de linguagem: faça pausas, use sinônimos ou reformule as frases."
        )
    else:
        suggestions.append("Nenhum vício de linguagem óbvio detectado pelo analisador local.")
    summary = (
        f"Detectados {sum(r['count'] for r in reps)} ocorrências de vícios de linguagem em {len(reps)} tipos diferentes."
        if reps
        else "Nenhuma ocorrência detectada."
    )
    return {"summary": summary, "repetitions": reps, "suggestions": suggestions}


def call_ollama(text: str, model: str, system_prompt: str = None) -> dict:
    # Construct a prompt asking for strict JSON output in Portuguese
    # If a system_prompt is provided, prepend it to the user text to bias the model
    user_block = (
        "Analise o texto abaixo e combine quaisquer pontos adicionais fornecidos em um único feedback corrido. "
        "Formato exigido: JSON válido conforme o esquema do serviço de feedback.\n"
        "----TEXT----\n"
        f"{text}\n"
        "----END----\n"
    )

    if system_prompt:
        prompt = system_prompt + "\n\n" + user_block
    else:
        prompt = user_block

    payload = {"model": model, "prompt": prompt, "max_tokens": 1024}
    # Security / offline guarantee: only allow local Ollama endpoints
    try:
        from urllib.parse import urlparse

        parsed = urlparse(OLLAMA_URL)
        host = parsed.hostname
        if host not in ("localhost", "127.0.0.1", None):
            raise RuntimeError(
                "Chamadas remotas não são permitidas: OLLAMA_URL deve apontar para localhost para manter operação 100% local"
            )
    except Exception:
        # If parsing fails or host is invalid, block remote calls
        raise RuntimeError("OLLAMA_URL inválido ou não-local; operações remotas proibidas")
    if not HAS_DEPENDENCIES or httpx is None:
        raise RuntimeError("httpx/fastapi dependencies não instaladas; chamada ao Ollama indisponível")

    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(OLLAMA_URL, json=payload)
            r.raise_for_status()
            text_resp = r.text.strip()
            # Try to parse direct JSON
            try:
                return json.loads(text_resp)
            except json.JSONDecodeError:
                # try to extract first JSON object inside response
                start = text_resp.find("{")
                end = text_resp.rfind("}")
                if start != -1 and end != -1 and end > start:
                    try:
                        return json.loads(text_resp[start : end + 1])
                    except Exception:
                        pass
            # fallback: return the raw text as summary
            return {"summary": text_resp, "feedback": text_resp, "repetitions": [], "suggestions": []}
    except Exception as e:
        # propagate as runtime error so caller can fallback to local analysis
        raise RuntimeError(f"Erro ao chamar Ollama local: {e}")


# ---------------- Feedback service ----------------
class FeedbackInput(BaseModel):
    transcript: str
    poses: List[dict] = []  # e.g., list of {timestamp: float, pose: 'open_hands'}
    vices: List[dict] = []  # output from vices analyzer (phrase/count/examples)
    extra: dict = {}


class FeedbackOutput(BaseModel):
    text: str
    highlights: List[str] = []


def compose_feedback_fallback(inp: FeedbackInput) -> dict:
    bullets = []
    if inp.vices:
        bullets.append(f"Vícios de linguagem detectados: {', '.join([v['phrase'] for v in inp.vices])}.")
    else:
        bullets.append("Sem vícios de linguagem significativos detectados.")

    if inp.poses:
        bullets.append(f"Foram detectadas {len(inp.poses)} observações de pose durante a apresentação.")

    if inp.transcript and len(inp.transcript) > 0:
        # brief content suggestion
        first_sentence = inp.transcript.strip().split('.')[0][:200]
        bullets.append(f"Conteúdo: comece com: '{first_sentence.strip()}'...")

    summary = " ".join(bullets)
    highlights = bullets
    return {"text": summary, "highlights": highlights}


@app.post("/feedback", response_model=FeedbackOutput)
def feedback_service(inp: FeedbackInput, model: str = "llama2"):
    # Build a prompt for Ollama to compose a cohesive feedback text
    prompt_parts = ["Junte os pontos abaixo e gere um feedback corrido e profissional em português:"]
    prompt_parts.append("TRANSCRIPT:\n" + (inp.transcript or ""))
    if inp.vices:
        prompt_parts.append("VICIOS:\n" + json.dumps(inp.vices, ensure_ascii=False))
    if inp.poses:
        prompt_parts.append("POSES:\n" + json.dumps(inp.poses, ensure_ascii=False))
    if inp.extra:
        prompt_parts.append("EXTRA:\n" + json.dumps(inp.extra, ensure_ascii=False))

    prompt = "\n\n".join(prompt_parts)

    try:
        res = call_ollama(prompt, model)
        # accept either raw text or structured JSON
        if isinstance(res, dict) and "text" in res:
            text = res.get("text")
            highlights = res.get("highlights", [])
        elif isinstance(res, str):
            text = res
            highlights = []
        else:
            # if model returned JSON structure
            text = res.get("summary", str(res)) if isinstance(res, dict) else str(res)
            highlights = res.get("highlights", []) if isinstance(res, dict) else []
        return FeedbackOutput(text=text, highlights=highlights)
    except Exception:
        fb = compose_feedback_fallback(inp)
        return FeedbackOutput(text=fb["text"], highlights=fb["highlights"])


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="campo 'text' vazio")

    # First, try to call local Ollama daemon
    try:
        result = call_ollama(req.text, req.model)
        if not isinstance(result, dict) or "repetitions" not in result:
            # invalid response, fallback
            raise RuntimeError("Resposta do Ollama não no formato esperado")
    except Exception:
        result = local_filler_analysis(req.text)

    # Normalize repetitions into PhraseCount dataclass list
    reps = [PhraseCount(**r) for r in result.get("repetitions", [])]
    return AnalyzeResponse(
        summary=result.get("summary", ""), repetitions=reps, suggestions=result.get("suggestions", [])
    )


if __name__ == "__main__":
    # Minimal runner for local development
    if not HAS_DEPENDENCIES:
        raise RuntimeError("Dependências de runtime não instaladas. Rode 'pip install -r requirements.txt'.")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
