# Estrutura do Projeto - Communication Coach

## 📁 Organização dos Arquivos

### Estrutura Principal
```
edge-ai-hackathon/
├── app/                          # Aplicação principal
│   ├── core/                     # Lógica de negócio
│   │   ├── analysis.py          # Análise de comunicação
│   │   ├── camera.py            # Gerenciamento de câmera
│   │   └── report_manager.py    # Gerenciamento de relatórios
│   ├── utils/                    # Utilitários
│   │   └── qualcomm_utils.py    # Detecção Qualcomm
│   ├── static/                   # Arquivos estáticos
│   │   ├── css/
│   │   └── js/
│   ├── templates/                # Templates HTML
│   ├── main.py                   # Aplicação Flask
│   ├── run.py                    # Launcher da aplicação
│   └── requirements.txt          # Dependências
├── assets/                       # Recursos (imagens, áudios)
├── docs/                         # Documentação
└── README.md                     # Documentação principal
```

## 🔧 Módulos da Aplicação

### Core Modules (`app/core/`)

#### `analysis.py` - CommunicationAnalyzer
- **Responsabilidade**: Análise de postura, gestos e contato visual
- **Funcionalidades**:
  - `analyze_posture()`: Avalia alinhamento corporal
  - `analyze_gestures()`: Analisa expressividade dos gestos
  - `analyze_eye_contact()`: Monitora direção do olhar
  - `generate_feedback()`: Gera feedback personalizado
  - `extract_landmarks()`: Extrai landmarks para visualização

#### `camera.py` - CameraManager
- **Responsabilidade**: Gerenciamento robusto de câmera
- **Funcionalidades**:
  - `find_working_camera()`: Detecta câmera funcionando
  - `test_camera_config()`: Testa configurações
  - `initialize_camera()`: Inicializa com configuração otimizada
  - `get_camera_info()`: Retorna informações da câmera
  - `reset_camera_config()`: Reseta configuração

#### `report_manager.py` - ReportManager
- **Responsabilidade**: Gerenciamento de relatórios e histórico
- **Funcionalidades**:
  - `add_report()`: Adiciona novo relatório
  - `get_all_reports()`: Lista todos os relatórios
  - `get_statistics()`: Calcula estatísticas
  - `export_history()`: Exporta histórico completo
  - `delete_report()`: Remove relatório específico

### Utils (`app/utils/`)

#### `qualcomm_utils.py` - QualcommUtils
- **Responsabilidade**: Detecção e otimização Qualcomm
- **Funcionalidades**:
  - `detect_snapdragon_x_native()`: Detecta Snapdragon X
  - `get_system_info()`: Informações do sistema
  - `check_qualcomm_tools()`: Verifica ferramentas Qualcomm
  - `setup_native_optimizations()`: Configura otimizações

### Frontend (`app/templates/` e `app/static/`)

#### Templates HTML
- `communication_coach.html`: Interface principal
- `final_report.html`: Página de relatório final
- `pitch_practice.html`: Página de prática
- `index.html`: Página inicial

#### Arquivos Estáticos
- `css/history.css`: Estilos para histórico
- `js/history_manager.js`: Gerenciamento de histórico

## 🚀 Como Executar

### Opção 1: Usando o Launcher
```bash
cd app
python run.py
```

### Opção 2: Execução Direta
```bash
cd app
python main.py
```

### Opção 3: Instalação e Execução
```bash
cd app
pip install -r requirements.txt
python main.py
```

## 🔄 Fluxo de Dados

1. **Inicialização**: `run.py` → `main.py`
2. **Detecção de Câmera**: `CameraManager.find_working_camera()`
3. **Análise em Tempo Real**: `CommunicationAnalyzer` processa frames
4. **Geração de Relatórios**: `ReportManager` salva dados
5. **Interface Web**: Templates renderizam dados via WebSocket

## 📊 APIs Disponíveis

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

## 🛠️ Configuração

### Arquivos de Configuração
- `camera_config.json`: Configuração da câmera (gerado automaticamente)
- `requirements.txt`: Dependências Python
- `app/config/`: Configurações da aplicação (futuro)

### Variáveis de Ambiente
- `FLASK_ENV`: Ambiente de desenvolvimento
- `FLASK_DEBUG`: Modo debug
- `PORT`: Porta da aplicação (padrão: 5000)

## 🔍 Debugging

### Logs Importantes
- `📁 Configuração carregada`: Câmera configurada
- `✅ Câmera inicializada`: Câmera funcionando
- `✅ MediaPipe inicializado`: IA carregada
- `📊 Frame X`: Processamento em tempo real
- `📄 Relatório salvo`: Relatório gerado

### Troubleshooting
1. **Câmera não detectada**: Verificar drivers e permissões
2. **Erro MediaPipe**: Verificar instalação do OpenCV
3. **Erro WebSocket**: Verificar firewall e porta
4. **Erro Qualcomm**: Verificar arquitetura ARM64

## 📈 Melhorias Futuras

### Estrutura Planejada
```
app/
├── config/                       # Configurações
├── models/                       # Modelos de IA
├── services/                     # Serviços externos
├── tests/                        # Testes unitários
└── migrations/                   # Migrações de dados
```

### Funcionalidades Futuras
- Autenticação de usuários
- Banco de dados para histórico
- Modelos de IA customizados
- API REST completa
- Interface mobile
- Integração com Qualcomm Neural Processing SDK
