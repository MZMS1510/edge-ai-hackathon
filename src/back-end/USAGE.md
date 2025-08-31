# Uso completo das ferramentas do Analista de Apresentações (local)

Este documento descreve uso das ferramentas adicionais (extração MediaPipe, treino e inferência em lote) e o endpoint `pose-classify`.

## Extração de keypoints (MediaPipe)

Script: `src/back-end/tools/extract_keypoints_mediapipe.py`

Extrai landmarks do MediaPipe por frame e produz um CSV com colunas `frame`, `time`, `joint_x`, `joint_y`, `joint_z`.

Uso:

```bash
python src/back-end/tools/extract_keypoints_mediapipe.py --video input.mp4 --out keypoints.csv
```

Opções:
- `--frame-step N` — processa a cada N-ésimo frame (padrão 1)
- `--max-frames M` — limita o número de frames processados

Requer: `opencv-python` e `mediapipe` instalados.

## Inferência em lote

Script: `src/back-end/tools/pose_inference_batch.py`

Lê um CSV gerado pela extração e classifica cada linha usando `pose_model.predict_from_joints`. Gera um `report.json` com rótulos e scores por frame.

Uso:

```bash
python src/back-end/tools/pose_inference_batch.py --csv keypoints.csv --out report.json
```

Se tiver um modelo `joblib` treinado, passe `--model model.joblib`.

## Treinamento do modelo de pose

Script: `src/back-end/train_pose_model.py`

Formato do CSV: colunas numéricas correspondentes aos joints (ex.: `nose_x`, `nose_y`, ...) e uma coluna `label` com 0 (ruim) ou 1 (bom).

Uso:

```bash
python src/back-end/train_pose_model.py --csv labeled.csv --out model.joblib
```

Requer: `pandas`, `scikit-learn`, `joblib`.

## Pipeline de exemplo (conveniência)

Script: `src/back-end/tools/run_pipeline_example.py` — chama extração e inferência em sequência:

```bash
python src/back-end/tools/run_pipeline_example.py --video input.mp4 --outdir ./out
```

## Endpoint `POST /pose-classify`

Recebe um JSON com `joints` (flat dict) e retorna `label` e `score`.

Exemplo de request:

```json
{ "joints": { "nose_x": 0.5, "nose_y": 0.5, "left_shoulder_x": 0.4, ... } }
```

Resposta:

```json
{ "label": "good", "score": 0.82 }
```

## Testes

Rode o suite de testes unitários:

```bash
cd src/back-end
. .venv/bin/activate
pip install pytest
pytest -q
```

## Observações

- Todas as ferramentas funcionam localmente. Instale as dependências opcionais apenas nas máquinas onde fará extração ou treino.
- Posso criar um notebook interativo para rotulagem visual (frame-by-frame) caso queira acelerar a criação de um dataset rotulado.
