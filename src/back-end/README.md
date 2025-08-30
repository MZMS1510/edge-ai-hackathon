
# Edge AI - Analista de Apresentações (100% local)

Este repositório implementa um "Analista de Apresentações" que roda inteiramente em dispositivos locais (edge computing). O serviço oferece dois sistemas separados:

- Analisador de vícios de linguagem (`/analyze`): recebe texto transcrito e detecta muletas e repetições para uso em dashboards e no serviço de feedback.
- Serviço de feedback (`/feedback`): recebe transcrição, saídas de visão (poses), e a análise de vícios e gera um texto corrido com feedback profissional.

Tudo é pensado para operação offline: a integração com Ollama utiliza apenas endpoints locais (localhost) e chamadas remotas são bloqueadas.

Requisitos mínimos

- Python 3.10+
- Ollama instalado e rodando localmente (opcional — sem Ollama o serviço usará análises fallback locais)

Instalação rápida

```bash
cd src/back-end
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Instalando e executando Ollama localmente

1. Baixe e instale Ollama seguindo as instruções oficiais: https://ollama.com/download (instalação deve ocorrer na máquina edge).
2. Inicialize o daemon Ollama localmente e carregue o modelo desejado (ex.: llama2 local). Certifique-se que o daemon escute em localhost.

Nota: o backend exige que `OLLAMA_URL` aponte para `localhost` ou `127.0.0.1` para manter operação 100% local. Não configure hosts remotos.

Rodando o serviço (desenvolvimento)

```bash
# com Ollama disponível localmente
uvicorn src.back-end.main:app --host 0.0.0.0 --port 8000

# sem Ollama: o serviço ainda roda e usa fallbacks locais
uvicorn src.back-end.main:app --host 0.0.0.0 --port 8000
```

Endpoints principais

- POST /analyze
  - body: {"text": "...", "model": "nome_do_modelo_local"}
  - resposta: {summary, repetitions, suggestions}

- POST /feedback
  - body: {"transcript": "...", "poses": [...], "vices": [...], "extra": {...}}
  - resposta: {text, highlights}

