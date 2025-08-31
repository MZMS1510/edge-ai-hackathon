#!/bin/bash
echo "🔧 Instalando dependências para Qualcomm Edge AI Hub..."

# Instalar PyAudio (pode precisar de portaudio)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev python3-pyaudio
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew install portaudio
fi

# Instalar dependências Python
pip install -r requirements.txt

echo "✅ Dependências instaladas!"
echo "🚀 Execute: python run.py"
