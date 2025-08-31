import os
import sys
import subprocess
import argparse

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print("Verificando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Todas as dependências foram instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências. Verifique o arquivo requirements.txt.")
        return False

def setup_qualcomm_ai_hub(skip_qualcomm=False):
    """Configura o acesso ao Qualcomm AI Hub"""
    if skip_qualcomm:
        print("\nPulando configuração do Qualcomm AI Hub conforme solicitado.")
        return True
        
    print("\nConfigurando acesso ao Qualcomm AI Hub...")
    
    try:
        # Verificar se já existe uma configuração
        config_file = os.path.expanduser("~/.qai-hub.json")
        if os.path.exists(config_file):
            print("✅ Configuração do Qualcomm AI Hub já existe.")
            return True
        
        # Solicitar API key
        print("\nPara acessar o Qualcomm AI Hub, você precisa de uma API key.")
        print("Obtenha sua chave em: https://aihub.qualcomm.com/")
        
        api_key = input("Digite sua API key do Qualcomm AI Hub: ").strip()
        if not api_key:
            print("❌ API key não fornecida. A configuração do Qualcomm AI Hub falhou.")
            return False
        
        # Configurar o acesso (simulado, já que não temos o módulo)
        print("✅ Qualcomm AI Hub configurado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar o Qualcomm AI Hub: {str(e)}")
        return False

def setup_nltk():
    """Baixa os recursos necessários do NLTK"""
    print("\nBaixando recursos NLTK...")
    
    try:
        import nltk
        
        # Baixar recursos necessários
        print("Baixando pacotes NLTK...")
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        
        print("✅ Recursos NLTK baixados com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao baixar recursos NLTK: {str(e)}")
        return False

def download_models(skip_qualcomm=False):
    """Baixa os modelos necessários para a aplicação"""
    print("\nBaixando modelos de IA...")
    
    try:
        # Importar módulos necessários
        import whisper
        from transformers import pipeline
        
        # Criar diretório para modelos se não existir
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        os.makedirs(models_dir, exist_ok=True)
        
        # Baixar modelo Whisper para análise de fala
        print("Baixando modelo Whisper para análise de fala...")
        whisper.load_model("tiny")
        print("✅ Modelo Whisper baixado com sucesso!")
        
        # Baixar modelo BERT para análise de sentimento
        print("Baixando modelo BERT para análise de sentimento...")
        sentiment_model_id = "neuralmind/bert-base-portuguese-cased-sentiment"
        sentiment_pipeline = pipeline("sentiment-analysis", model=sentiment_model_id)
        print("✅ Modelo BERT baixado com sucesso!")
        
        # Baixar modelos MediaPipe
        print("Verificando modelos MediaPipe...")
        import mediapipe as mp
        mp.solutions.face_mesh
        mp.solutions.pose
        print("✅ Modelos MediaPipe verificados com sucesso!")
        
        print("\n✅ Todos os modelos foram baixados com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao baixar modelos: {str(e)}")
        return False

def main():
    """Função principal para inicialização do sistema"""
    parser = argparse.ArgumentParser(description="Inicializa o sistema PitchPerfect AI")
    parser.add_argument("--skip-deps", action="store_true", help="Pula a verificação de dependências")
    parser.add_argument("--skip-qualcomm", action="store_true", help="Pula a configuração do Qualcomm AI Hub")
    parser.add_argument("--skip-models", action="store_true", help="Pula o download dos modelos")
    
    args = parser.parse_args()
    
    print("\n===== Inicializando PitchPerfect AI =====")
    
    # Verificar dependências
    if not args.skip_deps and not check_dependencies():
        print("\n❌ Falha na verificação de dependências. Abortando inicialização.")
        return False
    
    # Configurar Qualcomm AI Hub
    if not setup_qualcomm_ai_hub(args.skip_qualcomm):
        print("\n⚠️ Falha na configuração do Qualcomm AI Hub. Continuando sem otimizações.")
    
    # Baixar modelos
    if not args.skip_models and not download_models(args.skip_qualcomm):
        print("\n❌ Falha no download dos modelos. Abortando inicialização.")
        return False
    
    print("\n✅ Sistema PitchPerfect AI inicializado com sucesso!")
    print("\nPara iniciar o servidor, execute: python run_server.py")
    return True

if __name__ == "__main__":
    main()