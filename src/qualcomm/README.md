# Qualcomm Voice Pitch Monitor

Sistema de monitoramento de voz em tempo real para auxílio de pitch, otimizado para Snapdragon X.

## �� Objetivo
Monitorar e analisar pitch vocal em tempo real para auxiliar em apresentações, canto, ou comunicação.

## 🚀 Características
- **Tempo Real**: Análise contínua de pitch
- **Snapdragon X**: Otimizado para Qualcomm AI Engine
- **Baixa Latência**: Processamento local
- **Visualização**: Interface gráfica do pitch
- **Feedback**: Alertas e sugestões

## 📁 Estrutura
```
qualcomm/
├── README.md
├── requirements.txt
├── run.py
├── app.py                    # Aplicação Flask principal
├── pitch_monitor.py          # Monitor principal
├── templates/
│   └── index.html           # Interface web
└── utils/
    └── qualcomm_utils.py     # Utilitários Qualcomm
```

## 🎵 Funcionalidades
- Detecção de pitch em tempo real
- Visualização de frequência
- Análise de estabilidade vocal
- Feedback de melhoria
- Gravação e análise

## 🔧 Instalação
```bash
cd src/qualcomm
pip install -r requirements.txt
python run.py
```

## 🌐 Uso
1. Execute `python run.py`
2. Acesse `http://localhost:5000`
3. Clique em "Iniciar Monitoramento"
4. Veja os dados em tempo real

## 🎤 Para testar com áudio real:
1. Instale PyAudio: `pip install pyaudio`
2. Modifique `pitch_monitor.py` para captura real
3. Substitua dados simulados por captura do microfone

## 🔧 Otimizações Snapdragon X
- Detecção automática do hardware
- Configurações otimizadas para ARM64
- Threading otimizado para 8 cores
- Processamento local sem nuvem

##  Interface
- Status do sistema em tempo real
- Gráfico interativo de pitch
- Estatísticas detalhadas
- Controles de monitoramento
- WebSocket para dados em tempo real
```

Agora todos os arquivos estão criados no repositório! Para testar:

## 🚀 **Como executar:**

### **1. Navegar para a pasta:**
```bash
cd src/qualcomm
```

### **2. Instalar dependências:**
```bash
pip install -r requirements.txt
```

### **3. Executar o monitor:**
```bash
python run.py
```

### **4. Acessar interface:**
- Abra: `http://localhost:5000`
- Clique em "Iniciar Monitoramento"
- Veja os dados em tempo real

## 🎯 **Funcionalidades disponíveis:**

### **📊 Status do Sistema:**
- Detecção automática do Snapdragon X
- Informações do hardware
- Status das ferramentas Qualcomm

### **🎵 Dados em Tempo Real:**
- Pitch atual (Hz)
- Nota musical
- Volume (dB)
- Estabilidade (%)

### ** Gráfico Interativo:**
- Pitch em tempo real
- Plotly.js para visualização
- Atualização automática via WebSocket

### **📊 Estatísticas:**
- Pitch médio
- Faixa de pitch
- Estabilidade
- Volume médio
- Total de amostras

### **🔧 Controles:**
- Iniciar/Parar monitoramento
- Interface responsiva
- WebSocket para dados em tempo real

A interface está pronta para testar! Os dados são simulados por enquanto, mas a estrutura está toda pronta para integrar com captura real de áudio. Quer que eu ajude a implementar a captura real do microfone?

