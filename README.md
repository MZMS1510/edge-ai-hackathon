# Edge AI Hackathon - Communication Coach

## 🎯 Sobre o Projeto

Este é um sistema de análise de comunicação em tempo real que utiliza IA para avaliar postura, gestos e contato visual durante apresentações. Otimizado para dispositivos Qualcomm Snapdragon X.

## 🚀 Funcionalidades Principais

- **Análise de Postura**: Avalia alinhamento corporal e posicionamento
- **Detecção de Gestos**: Analisa expressividade e uso de gestos
- **Contato Visual**: Monitora direção do olhar e engajamento
- **Relatórios Detalhados**: Gera análises completas com recomendações
- **Interface Web**: Dashboard interativo com visualizações em tempo real

## 📁 Estrutura do Projeto

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
│   └── requirements.txt          # Dependências
├── assets/                       # Recursos (imagens, áudios)
├── docs/                         # Documentação
└── README.md                     # Este arquivo
```

## 🛠️ Instalação

1. **Clone o repositório**:
```bash
git clone <repository-url>
cd edge-ai-hackathon
```

2. **Instale as dependências**:
```bash
cd app
pip install -r requirements.txt
```

3. **Execute a aplicação**:
```bash
python main.py
```

4. **Acesse no navegador**:
```
http://localhost:5000
```

## 🎥 Como Usar

1. **Inicie uma sessão**: Clique em "Start Coaching"
2. **Posicione-se**: Fique em frente à câmera
3. **Apresente**: Fale naturalmente como em uma apresentação
4. **Monitore**: Acompanhe suas métricas em tempo real
5. **Analise**: Veja o relatório final com recomendações

## 🔧 Requisitos do Sistema

- **Sistema Operacional**: Windows 10/11
- **Processador**: Qualcomm Snapdragon X (recomendado)
- **Câmera**: Webcam funcional
- **Python**: 3.8+
- **RAM**: 4GB mínimo

## 📊 Tecnologias Utilizadas

- **Backend**: Flask, SocketIO
- **IA**: MediaPipe, OpenCV
- **Frontend**: HTML5, CSS3, JavaScript
- **Visualização**: Plotly, Chart.js
- **Otimização**: Qualcomm Snapdragon X

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🆘 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Consulte a documentação em `/docs`
- Verifique o [QUICK_START.md](QUICK_START.md)

---

**Desenvolvido para o Edge AI Hackathon - Qualcomm**

