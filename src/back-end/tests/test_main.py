import importlib.util
import sys
from pathlib import Path


def load_analyzer_module():
    p = Path(__file__).resolve().parents[1] / "main.py"
    spec = importlib.util.spec_from_file_location("analyzer", str(p))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_local_filler_analysis_simple():
    analyzer = load_analyzer_module()
    text = "Bom, eu fui lá e tipo falei assim: isso é muito bom. Aí eu pensei, né, que seria ok."
    res = analyzer.local_filler_analysis(text)
    assert "summary" in res
    counts = {r["phrase"]: r["count"] for r in res["repetitions"]}
    assert counts.get("tipo", 0) >= 1


def test_feedback_fallback_compose():
    analyzer = load_analyzer_module()
    inp = analyzer.FeedbackInput(
        transcript="Olá, este é um teste. Obrigado pela atenção.", poses=[{"timestamp": 0.5, "pose": "open"}], vices=[{"phrase":"tipo","count":2,"examples":["...tipo..."]}]
    )
    res = analyzer.compose_feedback_fallback(inp)
    # compose_feedback_fallback returns dict with keys 'text' and 'highlights'
    assert isinstance(res, dict)
    assert "Vícios de linguagem detectados" in res["text"]


def test_system_prompt_exists():
    analyzer = load_analyzer_module()
    assert hasattr(analyzer, "SYSTEM_PROMPT")
    assert isinstance(analyzer.SYSTEM_PROMPT, str)
    assert len(analyzer.SYSTEM_PROMPT) > 0
