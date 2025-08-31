# Edge Coach - Analista de Apresentações com IA (100% Local)

Sistema completo de análise de apresentações executando inteiramente em dispositivos edge. Utiliza MediaPipe para análise visual, processamento de áudio para transcrição, e IA local (Ollama) para feedback inteligente.

## 📑 Índice

- [🎯 Características](#-características)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto) 
- [🚀 Instalação](#-instalação)
- [🔧 Execução](#-execução)
- [📡 API Reference](#-api-reference)
- [🔌 WebSocket Protocol](#-websocket-protocol)
- [🧠 Componentes de IA](#-componentes-de-ia)
- [🧪 Testes](#-testes)
- [📊 Métricas](#-métricas)
- [🛠️ Ferramentas Avançadas](#️-ferramentas-avançadas)
- [🚨 Solução de Problemas](#-solução-de-problemas)
- [📝 Desenvolvimento](#-desenvolvimento)
- [📋 Changelog](#-changelog)

## 🎯 Características

- **100% Local**: Nenhum dado sai do dispositivo
- **Análise em Tempo Real**: WebSocket para processamento contínuo
- **IA Integrada**: Feedback inteligente via Ollama (DeepSeek-R1)
- **Visão Computacional**: MediaPipe para detecção de poses, gestos e expressões
- **Análise de Áudio**: Detecção de vícios de linguagem e métricas vocais
- **APIs REST**: Interface completa para integração
- **Dashboard Interativo**: Interface Streamlit para visualização

## 📁 Estrutura do Projeto

### Arquivos Principais
```
├── main.py                    # Servidor FastAPI principal (REST API)
├── websocket_server.py        # Servidor WebSocket para tempo real
├── core_processing.py         # Processamento MediaPipe e extração de features
├── ollama_client.py          # Cliente para IA local (Ollama)
├── pose_model.py             # Classificação de poses corporais
├── version.py                # Informações de versão
└── requirements_minimal.txt   # Dependências essenciais
```

### Utilitários
```
├── ui_streamlit.py           # Dashboard Streamlit
├── capture_audio.py          # Captura de áudio standalone
├── capture_video.py          # Captura de vídeo standalone
├── train_pose_model.py       # Treinamento de modelos de pose
└── test_websocket.py         # Testes WebSocket
```

### Ferramentas Avançadas
```
tools/
├── extract_keypoints_mediapipe.py  # Extração de landmarks
├── pose_inference_batch.py         # Inferência em lote
└── run_pipeline_example.py         # Pipeline completo
```

## 🚀 Instalação

### 1. Ambiente Python
```bash
cd src/back-end
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. Dependências
```bash
# Instalação mínima (recomendada)
pip install -r requirements_minimal.txt

# Ou instalação completa
pip install -r requirements.txt
```

### 3. Configuração Ollama (Opcional)
```bash
# Instalar Ollama: https://ollama.com/download
ollama serve
ollama pull deepseek-r1:8b

# Configurar URL (padrão já é localhost)
export OLLAMA_URL="http://localhost:11434/api/generate"
```

## 🔧 Execução

### Opção 1: Servidor REST API
```bash
# Método 1: Direto
python main.py

# Método 2: Via uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```
🌐 **Acesso**: http://localhost:8000  
📖 **Documentação**: http://localhost:8000/docs

### Opção 2: Servidor WebSocket (Tempo Real)
```bash
python websocket_server.py
```
🔌 **WebSocket**: ws://localhost:8765  
🧪 **Teste**: Acesse via browser para cliente HTML integrado

### Opção 3: Dashboard Streamlit
```bash
streamlit run ui_streamlit.py
```
📊 **Dashboard**: http://localhost:8501

### Opção 4: Execução Completa (Recomendada)
Execute simultaneamente para funcionalidade completa:
```bash
# Terminal 1: API REST
python main.py

# Terminal 2: WebSocket
python websocket_server.py

# Terminal 3: Dashboard (opcional)
streamlit run ui_streamlit.py
```

## 📡 API Reference

### REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Server info |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | API documentation |
| `POST` | `/metrics` | Send video metrics |
| `POST` | `/transcript` | Send audio transcript |
| `POST` | `/analyze` | Analyze text for filler words |
| `POST` | `/pose-classify` | Classify body pose |
| `GET` | `/stats` | Current session stats |
| `GET` | `/metrics?count=N` | Get metrics history |
| `GET` | `/transcript` | Get full transcript |
| `GET` | `/analysis` | Get available analyses |
| `POST` | `/analysis/generate` | Force new analysis |
| `POST` | `/reset` | Reset session |

### Exemplos de Uso

#### Análise de Texto
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Então, tipo, hoje vou falar sobre IA, né?"}'

# Resposta
{
  "summary": "Detectados 3 vícios de linguagem",
  "repetitions": [
    {"phrase": "tipo", "count": 1, "examples": ["..."]}
  ],
  "suggestions": ["Evite repetições..."]
}
```

#### Métricas de Vídeo
```bash
curl -X POST http://localhost:8000/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": 1693486200.0,
    "nervousness_score": 0.3,
    "blink_detected": true,
    "blink_stats": {"blink_rate": 15.2},
    "hand_movement": 0.45,
    "head_movement": 0.23,
    "hands_detected": 2,
    "face_detected": 1,
    "raw_metrics": {"avg_hand_movement": 0.45}
  }'
```

#### Classificação de Poses
```bash
curl -X POST http://localhost:8000/pose-classify \
  -H "Content-Type: application/json" \
  -d '{
    "joints": {
      "nose_x": 0.5, "nose_y": 0.3,
      "left_shoulder_x": 0.4, "left_shoulder_y": 0.4
    }
  }'

# Resposta
{
  "label": "good",
  "score": 0.85
}
```

## 🔌 WebSocket Protocol

### Tipos de Mensagem

| Type | Direction | Description |
|------|-----------|-------------|
| `video_frame` | Client → Server | Send video frame for analysis |
| `audio_data` | Client → Server | Send audio data |
| `transcript` | Client → Server | Send transcript text |
| `get_stats` | Client → Server | Request session statistics |
| `reset_session` | Client → Server | Reset session data |
| `ping` | Client → Server | Ping/pong for connection test |
| `video_analysis` | Server → Client | Video analysis results |
| `audio_analysis` | Server → Client | Audio analysis results |
| `session_stats` | Server → Client | Session statistics |
| `error` | Server → Client | Error message |

### Exemplo JavaScript
```javascript
// Conectar ao WebSocket
const ws = new WebSocket('ws://localhost:8765');

// Enviar frame de vídeo
ws.send(JSON.stringify({
  type: 'video_frame',
  frame: base64_encoded_frame
}));

// Receber análise
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'video_analysis') {
    console.log('Nervousness:', data.metrics.nervousness_score);
  }
};
```

## 🧠 Componentes de IA

### MediaPipe Processing
- **Detecção de Poses**: 33 pontos corporais
- **Malha Facial**: 468 landmarks faciais  
- **Detecção de Mãos**: Até 2 mãos simultaneamente
- **Métricas Automáticas**: Nervosismo, piscadas, movimento

### Análise de Áudio
- **Processamento em Tempo Real**: Chunks de 1024 samples
- **Extração de Features**: Volume, zero-crossings, energia
- **Buffer Circular**: Mantém 5 segundos de histórico

### IA Local (Ollama)
- **Modelo Padrão**: DeepSeek-R1:8b
- **Análise Contextual**: Combina métricas visuais e texto
- **Feedback Personalizado**: Dicas específicas em português
- **Fallback Local**: Funciona sem Ollama

## 🧪 Testes

### Teste de Endpoints
```bash
# Teste básico do servidor
python -c "
import requests
response = requests.get('http://localhost:8000/')
print(response.json())
"

# Teste de análise
python -c "
import requests
response = requests.post('http://localhost:8000/analyze', 
    json={'text': 'Tipo, então, né...'})
print(response.json())
"
```

### Teste WebSocket
```bash
python test_websocket.py
```

### Verificação de Dependências
```bash
python -c "
import mediapipe as mp
import cv2
import numpy as np
print('✅ Todas as dependências OK')
"
```

### Suite de Testes
```bash
cd tests
python -m pytest -v
```

## 📊 Métricas

### Métricas Visuais
- **Nervosismo**: Score 0-1 baseado em movimento e piscadas
- **Taxa de Piscadas**: Piscadas por minuto (normal: 12-20)
- **Movimento das Mãos**: Amplitude de gestos
- **Movimento da Cabeça**: Estabilidade postural
- **Detecções**: Contagem de faces/mãos detectadas

### Métricas de Áudio
- **Volume**: RMS do sinal
- **Zero Crossings**: Indicador de vocalização
- **Energia**: Potência do sinal

### Análise de Texto
- **Vícios de Linguagem**: "tipo", "né", "então", "basicamente", etc.
- **Repetições**: Frases/palavras recorrentes
- **Sugestões**: Recomendações automáticas

### Cálculo do Score de Nervosismo
```python
# Fatores considerados:
blink_nervousness = (blink_rate - 12) / 20  # Normal: 12-20/min
hand_nervousness = hand_movement * 10       # Normalizado
head_nervousness = head_movement * 5        # Normalizado

nervousness_score = mean([blink_nervousness, hand_nervousness, head_nervousness])
nervousness_score = clamp(nervousness_score, 0, 1)
```

## 🛠️ Ferramentas Avançadas

### Extração de Keypoints
```bash
# Extrair landmarks de vídeo
python tools/extract_keypoints_mediapipe.py \
  --video input.mp4 \
  --out keypoints.csv \
  --frame-step 2
```

### Treinamento de Modelo de Pose
```bash
# Treinar classificador personalizado
python train_pose_model.py \
  --csv labeled_data.csv \
  --out pose_model.joblib
```

### Inferência em Lote
```bash
# Processar CSV de keypoints
python tools/pose_inference_batch.py \
  --csv keypoints.csv \
  --model pose_model.joblib \
  --out results.json
```

### Pipeline Completo
```bash
# Executar pipeline completo
python tools/run_pipeline_example.py \
  --video presentation.mp4 \
  --outdir ./analysis_results
```

## 🚨 Solução de Problemas

### Erros Comuns

#### "Module not found"
```bash
pip install -r requirements_minimal.txt
```

#### "Ollama connection failed"
```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Iniciar Ollama
ollama serve
```

#### "Camera not found"
```bash
# Verificar câmeras disponíveis
python -c "
import cv2
for i in range(3):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f'Camera {i}: OK')
    cap.release()
"
```

#### "Port already in use"
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill
```

#### Performance Issues
- Reduza a taxa de quadros: `frame_step=2` ou mais
- Use `model_complexity=0` no MediaPipe
- Diminua resolução do vídeo se necessário
- Monitore uso de CPU/memória

## 📝 Desenvolvimento

### Estrutura de Classes

#### MediaPipeProcessor
```python
from core_processing import MediaPipeProcessor

processor = MediaPipeProcessor()
results = processor.process_frame(frame)
# Returns: metrics, joints, landmarks, annotated_frame
```

#### FeatureTracker
```python
from core_processing import FeatureTracker

tracker = FeatureTracker(window_size=30)
metrics = tracker.extract_metrics(face, pose, hands)
# Returns: nervousness_score, blink_stats, movements
```

#### OllamaClient
```python
from ollama_client import OllamaClient

client = OllamaClient()
feedback = client.analyze_presentation(transcript, metrics)
# Returns: AI-generated coaching feedback
```

### Adicionando Novos Endpoints
```python
@app.post("/meu-endpoint")
async def meu_endpoint(data: MeuModel):
    # Sua lógica aqui
    return {"resultado": "sucesso"}
```

### Configuração Avançada
```bash
# Variáveis de ambiente
export OLLAMA_URL="http://localhost:11434/api/generate"
export OLLAMA_MODEL="deepseek-r1:8b"
export LOG_LEVEL="DEBUG"
```

### Logs e Debug
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Em main.py
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

## 📋 Changelog

### Version 2.0.0 - Consolidated Architecture (2025-08-31)

#### 🚀 Major Changes
- **Consolidated Architecture**: Reduced from 20+ files to 6 core files
- **Unified Processing**: All MediaPipe logic consolidated
- **Single WebSocket Server**: Combined multiple implementations
- **Improved Documentation**: Comprehensive single README

#### ✨ New Features
- **Real-time WebSocket Processing**: Live video/audio analysis
- **Enhanced AI Integration**: Better Ollama client with fallbacks
- **Session Management**: Complete session lifecycle handling
- **Multi-client Support**: WebSocket broadcasting
- **Built-in Test Client**: HTML interface for testing

#### 📁 File Structure Changes
**Consolidated Files:**
- `core_processing.py` ← `features.py` + `media_pipe_utils.py` + `analyze.py`
- `websocket_server.py` ← Multiple server implementations

**Core Files Enhanced:**
- `main.py` - Better error handling and validation
- `ollama_client.py` - Connection testing and fallbacks
- `pose_model.py` - Improved heuristics

#### 🔧 API Changes
**New Endpoints:**
- `POST /transcript` - Handle audio transcriptions
- `GET /analysis` - Get available analyses
- `POST /analysis/generate` - Force analysis generation
- `POST /reset` - Reset session data

#### 📋 Dependencies
- **Minimal Requirements**: Essential packages only
- **Better Error Handling**: Graceful fallbacks
- **Improved Imports**: Relative/absolute handling

### Future Roadmap

#### Version 2.1.0 (Planned)
- [ ] Enhanced AI models integration
- [ ] Real-time collaboration features
- [ ] Mobile app support
- [ ] Cloud deployment options

#### Version 2.2.0 (Planned)
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Custom model training pipeline
- [ ] Performance optimizations

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das mudanças (`git commit -am 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### Guidelines de Desenvolvimento
- Mantenha operação 100% local
- Documente todas as funções públicas
- Adicione testes para novas funcionalidades
- Siga padrões de código Python (PEP 8)
- Use type hints quando possível

## 📄 Licença

Este projeto é parte do Edge AI Hackathon e segue as diretrizes de uso local e privacidade.

**Edge Coach v2.0.0** - Sistema de Análise de Apresentações com IA  
Desenvolvido pela equipe Edge AI Hackathon Team  
Build: 2025-08-31
