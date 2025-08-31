# Extração de Áudio de Vídeos 🎵

Scripts para extrair áudio de arquivos de vídeo (MP4, AVI, MOV) e converter para WAV usando FFmpeg.

## 📁 Arquivos

- `extract_audio_from_video.py` - Script principal de extração
- `test_audio_extraction.py` - Script de teste automatizado  
- `extract_audio_text.py` - Script original de transcrição

## 🚀 Como Executar

### 1. Verificar Dependências

```bash
# Verificar se FFmpeg está instalado
ffmpeg -version

# Se não estiver instalado no Windows:
winget install FFmpeg
# ou baixe de: https://ffmpeg.org/download.html
```

### 2. Executar o Extrator

#### Modo Interativo (Recomendado)
```bash
cd src/outros
python extract_audio_from_video.py
```

O script irá:
- ✅ Verificar se FFmpeg está disponível
- 📁 Listar vídeos encontrados nas pastas
- 🎯 Permitir escolha do arquivo
- 📊 Mostrar informações do vídeo
- 🔄 Extrair áudio automaticamente

#### Modo Linha de Comando
```bash
# Uso básico
python extract_audio_from_video.py --input meu_video.mp4

# Configuração personalizada
python extract_audio_from_video.py \
  --input apresentacao.mp4 \
  --output apresentacao_audio.wav \
  --rate 22050 \
  --channels 2

# Ajuda
python extract_audio_from_video.py --help
```

### 3. Testar Funcionalidade

```bash
# Executar teste automatizado
python test_audio_extraction.py
```

Este teste irá:
- 🎬 Criar um vídeo de teste (3 segundos)
- 🎵 Adicionar áudio de teste (tom 440Hz)
- 🔄 Extrair áudio usando o script
- ✅ Verificar se funcionou corretamente
- 🧹 Limpar arquivos temporários

## 📋 Exemplos Práticos

### Exemplo 1: Vídeo Simples
```bash
python extract_audio_from_video.py --input presentation.mp4
# Resultado: presentation_audio.wav
```

### Exemplo 2: Alta Qualidade
```bash
python extract_audio_from_video.py \
  --input important_meeting.mp4 \
  --output meeting_audio.wav \
  --rate 48000 \
  --channels 2
```

### Exemplo 3: Otimizado para Speech Recognition
```bash
python extract_audio_from_video.py \
  --input speech.mp4 \
  --rate 16000 \
  --channels 1
# Ideal para transcrição com speech_recognition
```

## 🔧 Parâmetros de Configuração

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--rate` | 16000 | Taxa de amostragem (Hz) |
| `--channels` | 1 | Canais (1=mono, 2=stereo) |
| `--input` | - | Arquivo de vídeo de entrada |
| `--output` | auto | Arquivo WAV de saída |

### Recomendações por Uso

| Caso de Uso | Sample Rate | Canais | Observações |
|-------------|-------------|--------|-------------|
| **Speech Recognition** | 16000 Hz | 1 (mono) | Ideal para transcrição |
| **Música/Qualidade** | 44100 Hz | 2 (stereo) | Qualidade CD |
| **Broadcast** | 48000 Hz | 2 (stereo) | Padrão profissional |
| **Protótipo Rápido** | 16000 Hz | 1 (mono) | Arquivos menores |

## 🧪 Testando com Seus Vídeos

### 1. Preparar Vídeo de Teste
Coloque um arquivo MP4 na pasta `src/outros` ou em `assets/`

### 2. Executar Extração
```bash
python extract_audio_from_video.py
# Escolha seu vídeo da lista
```

### 3. Verificar Resultado
```bash
# Reproduzir áudio (Windows)
start audio_extraido.wav

# Verificar informações
ffprobe audio_extraido.wav
```

### 4. Usar para Transcrição
```bash
# Mover para pasta de áudios
move audio_extraido.wav ../../assets/Estudos-livros/audios/

# Executar transcrição
python extract_audio_text.py
```

## 📊 Análise de Performance

### Tempos Típicos de Processamento
- **Vídeo 1 min (HD)**: ~5-10 segundos
- **Vídeo 10 min (HD)**: ~30-60 segundos  
- **Vídeo 1 hora (HD)**: ~3-5 minutos

### Tamanhos de Arquivo
- **1 minuto mono 16kHz**: ~1.9 MB
- **1 minuto stereo 44kHz**: ~10.5 MB
- **1 hora mono 16kHz**: ~115 MB

## 🚨 Solução de Problemas

### "FFmpeg não encontrado"
```bash
# Windows - Instalar FFmpeg
winget install FFmpeg

# Ou adicionar ao PATH manualmente
# Baixar de: https://ffmpeg.org/download.html
```

### "Arquivo muito grande"
```bash
# Reduzir sample rate
python extract_audio_from_video.py --input video.mp4 --rate 16000 --channels 1
```

### "Erro de codec"
```bash
# Tentar com formato diferente
ffmpeg -i seu_video.mp4 -c:v libx264 -c:a aac video_convertido.mp4
```

### "Sem áudio no resultado"
```bash
# Verificar se vídeo original tem áudio
ffprobe -v quiet -select_streams a -show_entries stream=codec_name seu_video.mp4
```

## 🔗 Integração com Outros Scripts

### Pipeline Completo: Vídeo → Texto
```bash
# 1. Extrair áudio
python extract_audio_from_video.py --input presentation.mp4

# 2. Mover arquivo
move presentation_audio.wav ../../assets/Estudos-livros/audios/

# 3. Transcrever
python extract_audio_text.py
```

### Automatizar com Batch
```bash
# Windows batch file (process_videos.bat)
@echo off
for %%f in (*.mp4) do (
    python extract_audio_from_video.py --input "%%f"
)
```

## 📈 Próximos Passos

1. ✅ **Extração funcionando** - Script criado e testado
2. 🔄 **Integração** - Combinar com `extract_audio_text.py`
3. 🎯 **Interface** - Criar GUI ou web interface
4. 🚀 **Otimização** - Processamento em lote
5. 🧠 **IA Integration** - Conectar com sistema Edge Coach

## 🎉 Resultado Esperado

Após executar com sucesso, você terá:
- ✅ Arquivo WAV extraído com qualidade configurada
- 📊 Informações detalhadas do processo
- 🎵 Áudio pronto para transcrição ou análise
- 🔧 Log completo do que foi processado

Agora você pode processar qualquer vídeo MP4 e extrair o áudio em formato WAV otimizado para o sistema Edge Coach! 🚀
