# Qualcomm - Edge AI Developer Hackathon

<p align="center">
<a href= "https://www.qualcomm.com/developer/events/edge-ai-developer-hackathon/brazil"><img src="./assets/Qualcomm.jpeg" alt="Qualcomm - Foto" border="0" width="100%"></a>
</p>

# PitchPerfect AI - Análise Inteligente de Apresentações

## Coditores


## 👨‍🎓 Membros do time: 

 <div align="center">
  <table>
    <tr>
     <td align="center"><a href="https://www.linkedin.com/in/ana-cristina-jardim/"><img style="border-radius: 10%;" src="./assets/fotos/ana-cristina.jpg" width="100px;" alt="Ana Cristina - Foto" /><br><sub><b>Ana Cristina</b></sub></a></td>
     <td align="center"><a href="https://www.linkedin.com/in/carlosicaro"><img style="border-radius: 10%;" src="./assets/fotos/carlos-icaro.jpg" width="100px;" alt="Carlos Icaro Kauã Coelho Paiva - Foto" /><br><sub><b>Carlos Icaro</b></sub></a></td>
     <td align="center"><a href="https://www.linkedin.com/in/ifelipemartins"><img style="border-radius: 10%;" src="./assets/fotos/felipe-martins.jpg" width="100px;" alt="Felipe Martins - Foto" /><br><sub><b>Felipe Martins</b></sub></a></td>
     <td align="center"><a href="https://www.linkedin.com/in/gustavo-martinsg"><img style="border-radius: 10%;" src="./assets/fotos/gustavo-martins.jpg" width="100px;" alt="Gustavo Martins - Foto" /><br><sub><b>Gustavo Martins</b></sub></a></td>
     <td align="center"><a href="https://www.linkedin.com/in/lavinia-mendonca/"><img style="border-radius: 10%;" src="./assets/fotos/lavinia-mendonca.jpg" width="100px;" alt="Lavinia Mendonça - Foto" /><br><sub><b>Lavinia Mendonça</b></sub></a></td>
     <td align="center"><a href="https://www.linkedin.com/in/marcos-vinicius-m-silva/"><img style="border-radius: 10%;" src="./assets/fotos/marcos-marcondes.jpg" width="100px;" alt="Marcos Marcondes - Foto" /><br><sub><b>Marcos Marcondes</b></sub></a></td>
     

  </table>
</div>

## 📝 Descrição

&nbsp;&nbsp;&nbsp;&nbsp;O PitchPerfect AI é uma aplicação inovadora que utiliza tecnologias de Inteligência Artificial da Qualcomm para analisar apresentações, pitches e comunicações em tempo real. A aplicação captura áudio e vídeo durante uma apresentação, processa os dados utilizando modelos de IA otimizados para dispositivos Snapdragon Edge AI, e fornece insights valiosos sobre diversos aspectos da comunicação, como:

- Clareza e fluência do discurso
- Ritmo e entonação da fala
- Linguagem corporal e expressões faciais
- Engajamento da audiência
- Estrutura e coerência do conteúdo
- Uso efetivo de recursos visuais

&nbsp;&nbsp;&nbsp;&nbsp;Ao final da apresentação, o sistema gera um dashboard interativo com métricas detalhadas e recomendações personalizadas para melhorar as habilidades de comunicação do apresentador. A aplicação é projetada para funcionar localmente no dispositivo, garantindo privacidade e baixa latência, graças às capacidades de processamento de IA na borda dos chips Snapdragon.

## 📝 Vídeo demonstrativo

Clique [aqui]("Adicionar link aqui") para acessar o vídeo demonstrativo da ferramenta.

## 🚀 Tecnologias Utilizadas

### Hardware
- **Dispositivos Qualcomm Snapdragon**: Otimizado para Snapdragon 8 Elite, 8 Gen 3, X Elite
- **Sensores**: Câmera e microfone integrados ou externos

### Backend
- **Linguagem**: Python/Node.js
- **Framework de IA**: Qualcomm AI Engine Direct
- **Modelos de IA do Qualcomm AI Hub**:
  - Whisper-Base para reconhecimento de fala e transcrição
  - Modelos de visão computacional para análise de expressões faciais e linguagem corporal
  - Modelos de processamento de linguagem natural para análise de conteúdo

### Frontend
- **Framework**: React/React Native
- **Biblioteca de UI**: Material-UI/Tailwind CSS
- **Visualização de Dados**: D3.js/Chart.js

### Comunicação
- **API RESTful**: Express.js/FastAPI
- **WebSockets**: Para streaming de dados em tempo real

## 📁 Estrutura de Pastas

A estrutura de pastas do projeto é organizada da seguinte forma:

```plaintext
project/
│
├── assets/                           # Elementos não estruturais relacionados à documentação
│   ├── fotos/                        # Fotos dos desenvolvedores do projeto
│   └── images/                       # Imagens utilizadas na aplicação
│
├── documents/                        # Documentação técnica do projeto
│   ├── architecture/                 # Diagramas de arquitetura
│   ├── api/                          # Documentação da API
│   └── models/                       # Documentação dos modelos de IA
│
├── src/                              # Código-fonte do projeto
│   ├── FrontEnd/                     # Código do frontend
│   │   ├── components/               # Componentes reutilizáveis
│   │   │   ├── Dashboard/            # Componentes do dashboard
│   │   │   ├── Recording/            # Componentes de gravação
│   │   │   └── Feedback/             # Componentes de feedback
│   │   ├── pages/                    # Páginas da aplicação
│   │   │   ├── Home/                 # Página inicial
│   │   │   ├── Analysis/             # Página de análise
│   │   │   └── Results/              # Página de resultados
│   │   ├── services/                 # Serviços do frontend
│   │   │   ├── api.ts                # Serviço de comunicação com a API
│   │   │   └── storage.ts            # Serviço de armazenamento local
│   │   └── App.tsx                   # Componente principal da aplicação
│   │
│   └── BackEnd/                      # Código do backend
│       ├── api/                      # Endpoints da API
│       │   ├── routes/               # Rotas da API
│       │   └── controllers/          # Controladores da API
│       ├── models/                   # Modelos de IA e dados
│       │   ├── speech/               # Modelos de análise de fala
│       │   ├── vision/               # Modelos de visão computacional
│       │   └── nlp/                  # Modelos de processamento de linguagem natural
│       ├── services/                 # Serviços do backend
│       │   ├── analysis.js           # Serviço de análise de apresentações
│       │   ├── recording.js          # Serviço de gravação
│       │   └── insights.js           # Serviço de geração de insights
│       └── main.js                   # Ponto de entrada do backend
│
└── README.md                         # Documentação principal do projeto
```

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Node.js 16+ ou Python 3.8+
- Dispositivo com Snapdragon 8 Elite, 8 Gen 3, X Elite ou compatível
- Câmera e microfone
- Conta no Qualcomm AI Hub para acesso aos modelos de IA

### Configuração do Ambiente

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/pitchperfect-ai.git
cd pitchperfect-ai
```

2. Instale as dependências do Backend:
```bash
cd src/BackEnd
npm install
# ou se estiver usando Python
pip install -r requirements.txt
```

3. Instale as dependências do Frontend:
```bash
cd ../FrontEnd
npm install
```

4. Configure o acesso ao Qualcomm AI Hub:
```bash
# Obtenha sua API key em https://aihub.qualcomm.com/
qai-hub configure --api_token SUA_API_TOKEN
```

5. Baixe os modelos de IA necessários:
```bash
python -m qai_hub_models.models.whisper_base.export --target-runtime qdai --device "Snapdragon 8 Elite"
```

### Executando a Aplicação

1. Inicie o Backend:
```bash
cd src/BackEnd
npm start
# ou se estiver usando Python
python main.py
```

2. Inicie o Frontend:
```bash
cd ../FrontEnd
npm start
```

3. Acesse a aplicação em seu navegador: `http://localhost:3000`

## 📊 Funcionalidades

### Captura de Apresentação
- Gravação de áudio e vídeo em tempo real
- Opção para importar arquivos de apresentações existentes
- Configuração de parâmetros de análise

### Análise em Tempo Real
- Transcrição automática do discurso
- Detecção de expressões faciais e linguagem corporal
- Análise de ritmo, entonação e clareza da fala
- Identificação de padrões de comunicação

### Dashboard de Insights
- Métricas quantitativas sobre a apresentação
- Gráficos de desempenho em diferentes aspectos
- Recomendações personalizadas para melhoria
- Comparação com apresentações anteriores

## 🔄 Fluxo de Dados

1. **Captura**: A aplicação captura áudio e vídeo da apresentação.
2. **Processamento**: Os dados são processados localmente usando os modelos de IA da Qualcomm.
3. **Análise**: O sistema extrai métricas e padrões da apresentação.
4. **Visualização**: Os resultados são apresentados em um dashboard interativo.
5. **Feedback**: O usuário recebe recomendações personalizadas para melhorar suas habilidades de comunicação.

## 🧠 Modelos de IA Utilizados

### Análise de Fala
- **Whisper-Base**: Modelo de reconhecimento de fala para transcrição multilíngue
- **Análise de Prosódia**: Avaliação de ritmo, entonação e pausas

### Análise Visual
- **Detecção Facial**: Reconhecimento de expressões e emoções
- **Postura e Gestos**: Análise de linguagem corporal

### Processamento de Linguagem Natural
- **Análise de Conteúdo**: Avaliação da estrutura e coerência do discurso
- **Detecção de Hesitações**: Identificação de pausas e marcadores de hesitação

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 💻 Configuração e Execução da ferramenta

### Requisitos de Sistema

- **Sistema Operacional**: Windows 10/11, macOS, Linux
- **Hardware**: Dispositivo com processador Qualcomm Snapdragon (8 Elite, 8 Gen 3, X Elite recomendados)
- **Memória**: Mínimo 8GB RAM (16GB recomendado)
- **Armazenamento**: 2GB de espaço livre para a aplicação e modelos de IA

### Passos para Execução

1. **Preparação do Ambiente**:
   - Certifique-se de que o dispositivo tem acesso à câmera e microfone
   - Verifique se o ambiente tem iluminação adequada para captura de vídeo

2. **Inicialização**:
   - Inicie o backend e frontend conforme instruções na seção de instalação
   - Aguarde a inicialização completa dos modelos de IA (pode levar alguns segundos)

3. **Configuração da Sessão**:
   - Na tela inicial, configure os parâmetros da sessão de análise
   - Selecione quais aspectos da apresentação deseja analisar

4. **Gravação**:
   - Inicie a gravação quando estiver pronto para começar a apresentação
   - A análise em tempo real será exibida em um painel lateral (opcional)

5. **Análise e Resultados**:
   - Ao finalizar a apresentação, o sistema processará os dados completos
   - O dashboard de insights será gerado automaticamente
   - Explore as diferentes métricas e recomendações

### Solução de Problemas

- **Erro de Inicialização dos Modelos**: Verifique sua conexão com o Qualcomm AI Hub e tente baixar os modelos novamente
- **Problemas de Desempenho**: Ajuste as configurações de qualidade de vídeo/áudio para melhorar o desempenho
- **Falha na Captura de Áudio/Vídeo**: Verifique as permissões do navegador e do sistema operacional

## 📱 Compatibilidade com Dispositivos

O PitchPerfect AI é otimizado para os seguintes dispositivos Qualcomm:

- **Smartphones**: Dispositivos com Snapdragon 8 Elite, 8 Gen 3, 8 Gen 2
- **Computadores**: Dispositivos com Snapdragon X Elite
- **Tablets**: Dispositivos com processadores Snapdragon compatíveis

A aplicação também pode funcionar em outros dispositivos, mas com desempenho reduzido ou funcionalidades limitadas.


## 📋 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

### Licença MIT

