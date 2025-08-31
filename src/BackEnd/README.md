# PitchPerfect AI - Backend

Este diretório contém o código do backend para o PitchPerfect AI, uma aplicação que utiliza tecnologias da Qualcomm para análise de apresentações em tempo real.

## Estrutura de Diretórios

```
src/BackEnd/
├── api/                # API REST para comunicação com o frontend
│   └── app.py          # Aplicação Flask com endpoints da API
├── models/             # Diretório para armazenar modelos de IA baixados
├── services/           # Serviços de análise
│   ├── speech_analyzer.py  # Análise de fala e áudio
│   ├── visual_analyzer.py  # Análise visual e de linguagem corporal
│   └── nlp_analyzer.py     # Análise de processamento de linguagem natural
├── requirements.txt    # Dependências do projeto
├── setup.py           # Script de configuração do ambiente
└── README.md          # Este arquivo
```

## Tecnologias Utilizadas

- **Flask**: Framework web para a API REST
- **Qualcomm AI Engine Direct**: Para otimização de modelos de IA em dispositivos Snapdragon
- **Qualcomm AI Hub Models**: Modelos pré-treinados otimizados para dispositivos edge
- **Whisper**: Modelo de reconhecimento de fala para transcrição e análise
- **MediaPipe**: Para análise de pose e expressões faciais
- **Transformers**: Para processamento de linguagem natural
- **OpenCV**: Para processamento de vídeo
- **Librosa**: Para processamento de áudio

## Configuração do Ambiente

### Pré-requisitos

- Python 3.8 ou superior
- Pip (gerenciador de pacotes Python)
- Acesso ao Qualcomm AI Hub (para obter API key)

### Instalação

1. Clone o repositório e navegue até o diretório do backend:

```bash
cd src/BackEnd
```

2. Execute o script de configuração:

```bash
python setup.py
```

Este script irá:
- Instalar todas as dependências necessárias
- Configurar o acesso ao Qualcomm AI Hub
- Baixar os modelos de IA necessários
- Configurar recursos do NLTK

### Opções de Configuração

O script de configuração aceita os seguintes argumentos:

- `--skip-models`: Pula o download dos modelos de IA
- `--skip-qualcomm`: Pula a configuração do Qualcomm AI Hub

Exemplo:

```bash
python setup.py --skip-models
```

## Executando o Servidor

Para iniciar o servidor de API, execute:

```bash
python api/app.py
```

O servidor será iniciado em `http://localhost:5000`.

## Endpoints da API

### Verificação de Saúde

```
GET /api/health
```

Retorna o status da API.

### Análise de Fala

```
POST /api/analyze/speech
```

Analisa um arquivo de áudio para extrair insights sobre a fala.

**Parâmetros**:
- `audio`: Arquivo de áudio (formato WAV recomendado)

### Análise Visual

```
POST /api/analyze/visual
```

Analisa um arquivo de vídeo para extrair insights sobre linguagem corporal.

**Parâmetros**:
- `video`: Arquivo de vídeo (formato MP4 recomendado)

### Análise de Texto

```
POST /api/analyze/text
```

Analisa o texto de uma apresentação para extrair insights sobre o conteúdo.

**Parâmetros**:
- `text`: Texto da apresentação (JSON)

### Análise Completa de Apresentação

```
POST /api/analyze/presentation
```

Realiza uma análise completa da apresentação, combinando análise de fala, visual e de texto.

**Parâmetros**:
- `audio`: Arquivo de áudio (opcional)
- `video`: Arquivo de vídeo (opcional)
- `text`: Texto da apresentação (opcional)

## Integração com Qualcomm AI Hub

O backend utiliza modelos do Qualcomm AI Hub otimizados para dispositivos Snapdragon. Para acessar esses modelos, é necessário obter uma API key em [https://aihub.qualcomm.com/](https://aihub.qualcomm.com/).

Os modelos são automaticamente otimizados para execução eficiente em dispositivos edge, aproveitando os recursos de hardware dos processadores Snapdragon.

## Desenvolvimento

### Adicionando Novos Analisadores

Para adicionar um novo analisador:

1. Crie uma nova classe no diretório `services/`
2. Implemente o método `analyze()` que recebe os dados e retorna um dicionário com os resultados
3. Registre o analisador em `api/app.py`

### Otimização para Dispositivos Edge

Para otimizar os modelos para dispositivos específicos da Qualcomm:

1. Utilize a biblioteca `qai_hub_models` para carregar e otimizar modelos
2. Especifique o dispositivo alvo durante a otimização
3. Salve os modelos otimizados no diretório `models/`

## Solução de Problemas

### Erro ao baixar modelos

Se encontrar erros ao baixar os modelos, tente:

```bash
python setup.py --skip-models
```

E depois baixe os modelos manualmente:

```python
from transformers import WhisperProcessor, WhisperForConditionalGeneration
WhisperProcessor.from_pretrained("openai/whisper-tiny")
WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")
```

### Erro de acesso ao Qualcomm AI Hub

Verifique se sua API key está correta e se você tem acesso aos modelos necessários no Qualcomm AI Hub.