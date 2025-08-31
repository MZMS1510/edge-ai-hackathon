# 🎬➡️🎵 Sistema Completo de Conversão Vídeo para Áudio

## 📋 **Resumo das Soluções Criadas**

Este repositório agora contém um **sistema completo de extração de áudio de vídeos** com múltiples interfaces, tudo funcionando **100% edge computing (local)**.

### ✅ **Soluções Implementadas:**

1. **Script de Linha de Comando** (`extract_audio_from_video.py`)
2. **Interface Web Moderna** (`web_video_converter.py`) 
3. **Processador Automatizado** (`auto_video_processor.py`)
4. **Transcrição Edge Computing** (`extract_audio_text_edge.py`)

---

## 🚀 **1. Interface Web (Recomendada)**

### 📱 **Interface Moderna e Intuitiva**
- ✅ **Drag & Drop**: Arraste vídeos direto para a interface
- ✅ **Upload Simples**: Botão de seleção de arquivos
- ✅ **Configurações Avançadas**: Sample rate e canais ajustáveis  
- ✅ **Download Direto**: Baixe o áudio WAV com um clique
- ✅ **Progresso Visual**: Barra de progresso animada
- ✅ **100% Edge**: Nenhum dado sai do dispositivo

### 🎯 **Como Usar:**
```bash
# 1. Executar servidor web
cd src/outros
conda activate mediapipe-env
python web_video_converter.py

# 2. Abrir navegador
# http://localhost:5000

# 3. Arrastar vídeo ou clicar em "Selecionar Vídeo"
# 4. Aguardar processamento
# 5. Clicar em "Baixar Áudio WAV"
```

### 🎨 **Características da Interface:**
- **Design Responsivo**: Funciona em desktop e mobile
- **Validação em Tempo Real**: Verifica formato e tamanho
- **Feedback Visual**: Indicadores de status e erro
- **Informações Detalhadas**: Mostra dados do vídeo e áudio
- **Configurações Personalizáveis**: 16kHz-48kHz, mono/stereo

---

## ⚙️ **2. Script de Linha de Comando**

### 🖥️ **Para Usuários Técnicos**
```bash
# Modo interativo
python extract_audio_from_video.py

# Modo direto
python extract_audio_from_video.py --input video.mp4 --output audio.wav

# Configurações personalizadas
python extract_audio_from_video.py \
  --input presentation.mp4 \
  --rate 22050 \
  --channels 2
```

---

## 🤖 **3. Processador Automatizado**

### 📁 **Monitoramento de Pastas**
O sistema monitora uma pasta e processa automaticamente qualquer vídeo colocado nela.

```bash
# Executar processador
python auto_video_processor.py

# Configurar pastas personalizadas
python auto_video_processor.py \
  --input meus_videos \
  --output meus_audios
```

### 🔄 **Como Funciona:**
1. **Monitora** pasta `input_videos`
2. **Detecta** novos vídeos automaticamente
3. **Extrai** áudio em formato WAV
4. **Move** vídeos para `processed_videos`
5. **Gera** logs de processamento

---

## 🧠 **4. Transcrição Edge Computing**

### 📝 **Texto com Whisper Local**
```bash
# Transcrição 100% local (sem Google)
python extract_audio_text_edge.py

# Comparar métodos
python extract_audio_text_edge.py --compare
```

---

## 🎯 **Formatos Suportados**

### 📹 **Entrada (Vídeo):**
- **MP4** ⭐ (Recomendado)
- **AVI** 
- **MOV**
- **MKV**
- **WMV**
- **FLV**

### 🎵 **Saída (Áudio):**
- **WAV** (PCM 16-bit) ⭐
- Sample rates: 16kHz, 22kHz, 44.1kHz, 48kHz
- Canais: Mono ou Stereo

---

## 📊 **Configurações Recomendadas**

| Uso | Sample Rate | Canais | Observações |
|-----|-------------|--------|-------------|
| **Transcrição/Speech** | 16 kHz | Mono | Menor tamanho, ideal para fala |
| **Qualidade Média** | 22 kHz | Mono | Equilíbrio tamanho/qualidade |
| **Alta Qualidade** | 44.1 kHz | Stereo | Qualidade CD |
| **Profissional** | 48 kHz | Stereo | Máxima qualidade |

---

## 🔧 **Instalação e Configuração**

### 1. **Dependências Base**
```bash
# FFmpeg (essencial)
winget install FFmpeg

# Python packages
pip install flask opencv-python watchdog
```

### 2. **Ambiente Conda**
```bash
conda activate mediapipe-env
# ou create ambiente se necessário
```

### 3. **Teste de Funcionamento**
```bash
# Teste básico
python test_audio_extraction.py

# Teste web
python web_video_converter.py
# Acesse: http://localhost:5000
```

---

## 🎉 **Teste Realizado com Sucesso**

### ✅ **Resultados do Teste:**
- **Vídeo original**: `(UWA) Josie Quin-Conroy.mp4` (183.9s)
- **Áudio gerado**: `(UWA) Josie Quin-Conroy_audio.wav` (5.6 MB)
- **Configuração**: 16 kHz, Mono, PCM 16-bit
- **Processo**: 100% local, sem conexão externa

---

## 🔒 **Edge Computing Garantido**

### ✅ **100% Local:**
- **FFmpeg**: Processamento local
- **OpenCV**: Visão computacional local  
- **Whisper**: IA de transcrição local
- **Flask**: Servidor web local
- **Sem APIs externas**: Nenhum dado sai do dispositivo

### ❌ **Evitado:**
- Google Speech Recognition (envia dados)
- APIs cloud de processamento
- Serviços externos de conversão

---

## 🚀 **Próximos Passos Sugeridos**

### 🔄 **Integração com Edge Coach:**
1. **Conectar** ao sistema principal de análise
2. **Automatizar** pipeline: Vídeo → Áudio → Transcrição → Análise
3. **Dashboard** unificado com métricas em tempo real

### 🎯 **Melhorias Futuras:**
- **Batch Processing**: Múltiplos vídeos simultâneos
- **GPU Acceleration**: Processamento mais rápido
- **Mobile App**: Interface para smartphones
- **API REST**: Integração com outros sistemas

---

## 📋 **Como Começar AGORA**

### 🎬 **Opção 1: Interface Web (Mais Fácil)**
```bash
cd src/outros
python web_video_converter.py
# Abra: http://localhost:5000
# Arraste seu vídeo MP4
# Baixe o áudio WAV
```

### ⚙️ **Opção 2: Linha de Comando**
```bash
cd src/outros
python extract_audio_from_video.py --input "seu_video.mp4"
```

### 🤖 **Opção 3: Automatizado**
```bash
cd src/outros
python auto_video_processor.py
# Coloque vídeos na pasta input_videos/
# Pegue áudios na pasta output_audios/
```

---

## 🎯 **Resultado Final**

Você agora tem um **sistema completo e robusto** para:
- ✅ **Converter** qualquer vídeo em áudio WAV
- ✅ **Interface moderna** via web browser  
- ✅ **Processamento automático** de lotes
- ✅ **100% edge computing** (privacidade total)
- ✅ **Múltiplas interfaces** (web, CLI, automatizado)
- ✅ **Testado e funcionando** com vídeo real

**O sistema está pronto para uso em produção no projeto Edge AI Hackathon! 🚀**
