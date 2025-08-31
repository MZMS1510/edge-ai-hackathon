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


def test_pose_model_fallback():
    # create a simple symmetric joint dict
    import importlib.util, os
    p = Path(__file__).resolve().parents[1] / "pose_model.py"
    spec = importlib.util.spec_from_file_location("pose_model", str(p))
    pm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pm)
    joints = {
        'nose_x': 0.5, 'nose_y': 0.5,
        'left_shoulder_x': 0.4, 'left_shoulder_y': 0.6,
        'right_shoulder_x': 0.6, 'right_shoulder_y': 0.6,
    }
    res = pm.predict_from_joints(None, joints)
    assert 'label' in res and 'score' in res


def test_media_pipe_converter():
    import importlib.util
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "media_pipe_utils.py"
    spec = importlib.util.spec_from_file_location("media_pipe_utils", str(p))
    mpu = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mpu)
    # fake landmarks as dicts
    landmarks = []
    for i in range(33):
        landmarks.append({'x': i * 0.01, 'y': i * 0.02, 'z': 0.0})
    flat = mpu.convert_landmarks_to_flat(landmarks)
    assert 'nose_x' in flat and 'left_shoulder_x' in flat
