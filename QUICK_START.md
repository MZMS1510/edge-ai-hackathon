# 🚀 Quick Start - Communication Coach

## ⚡ Execução Rápida

### 1. Instalação das Dependências
```bash
cd app
pip install -r requirements.txt
```

### 2. Execução da Aplicação
```bash
# Opção 1: Usando o launcher (recomendado)
python run.py

# Opção 2: Execução direta
python main.py
```

### 3. Acesso à Aplicação
```
http://localhost:5000
```

## 🎯 Funcionalidades Principais

### Análise de Comunicação
- **Postura**: Avalia alinhamento corporal
- **Gestos**: Analisa expressividade dos movimentos
- **Contato Visual**: Monitora direção do olhar

### Interface Web
- Dashboard em tempo real
- Visualização de métricas
- Relatórios detalhados
- Histórico de análises

## 🔧 Requisitos do Sistema

- **Sistema Operacional**: Windows 10/11
- **Processador**: Qualcomm Snapdragon X (recomendado)
- **Câmera**: Webcam funcional
- **Python**: 3.8+
- **RAM**: 4GB mínimo

## 📊 Como Usar

1. **Inicie a aplicação**: Execute `python run.py`
2. **Acesse o navegador**: Vá para `http://localhost:5000`
3. **Clique em "Start Coaching"**: Inicia a análise
4. **Posicione-se**: Fique em frente à câmera
5. **Apresente**: Fale naturalmente como em uma apresentação
6. **Monitore**: Acompanhe suas métricas em tempo real
7. **Clique em "Stop Coaching"**: Finaliza e gera relatório

## 🛠️ Troubleshooting

### Problemas Comuns

**Câmera não detectada:**
- Verifique se a câmera está conectada
- Confirme permissões de acesso
- Reinicie a aplicação

**Erro de dependências:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Erro MediaPipe:**
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

**Porta ocupada:**
- Mude a porta no arquivo `main.py`
- Ou feche outras aplicações usando a porta 5000

### Logs Importantes
- `✅ Câmera inicializada`: Câmera funcionando
- `✅ MediaPipe inicializado`: IA carregada
- `📊 Frame X`: Processamento em tempo real
- `📄 Relatório salvo`: Relatório gerado

## 📁 Estrutura do Projeto

```
app/
├── core/                     # Lógica de negócio
│   ├── analysis.py          # Análise de comunicação
│   ├── camera.py            # Gerenciamento de câmera
│   └── report_manager.py    # Gerenciamento de relatórios
├── utils/                    # Utilitários
│   └── qualcomm_utils.py    # Detecção Qualcomm
├── templates/                # Templates HTML
├── static/                   # Arquivos estáticos
├── main.py                   # Aplicação Flask
├── run.py                    # Launcher
└── requirements.txt          # Dependências
```

## 🔍 APIs Disponíveis

### Rotas Principais
- `GET /`: Página principal
- `GET /status`: Status do sistema
- `POST /start_coaching`: Inicia análise
- `POST /stop_coaching`: Para análise
- `GET /get_communication_metrics`: Métricas em tempo real

### APIs de Histórico
- `GET /api/history`: Lista histórico
- `GET /api/report/<id>`: Relatório específico
- `DELETE /api/report/<id>`: Remove relatório
- `GET /api/export-history`: Exporta histórico

## 🎨 Personalização

### Configuração da Câmera
- A configuração é salva automaticamente em `camera_config.json`
- Para resetar: delete o arquivo `camera_config.json`

### Estilos CSS
- Edite `static/css/` para personalizar aparência
- Templates em `templates/` para modificar interface

### Análise de IA
- Módulo principal: `core/analysis.py`
- Ajuste parâmetros de detecção conforme necessário

## 📈 Próximos Passos

1. **Teste a aplicação** com diferentes cenários
2. **Analise os relatórios** gerados
3. **Personalize** conforme suas necessidades
4. **Contribua** com melhorias no GitHub

## 🆘 Suporte

- **Issues**: Abra uma issue no GitHub
- **Documentação**: Consulte `/docs`
- **Código**: Analise os módulos em `/app/core`

---

**Desenvolvido para o Edge AI Hackathon - Qualcomm** 🚀
