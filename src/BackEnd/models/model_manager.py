import os
import json
import torch
import nltk
from pathlib import Path

from .whisper_model import load_whisper_model
from .mediapipe_model import load_mediapipe_models
from .nlp_model import load_nlp_models

class ModelManager:
    """
    Gerencia o carregamento e acesso aos modelos de IA utilizados no sistema.
    """
    def __init__(self, use_qualcomm=True):
        self.use_qualcomm = use_qualcomm
        self.models = {}
        self.model_paths = {}
        self.download_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "downloads"
        self.download_dir.mkdir(exist_ok=True)
        
        # Configurar caminhos para download de recursos NLTK
        nltk.data.path.append(str(self.download_dir / "nltk_data"))
    
    def download_nltk_resources(self):
        """
        Baixa recursos necessários do NLTK.
        """
        print("Baixando recursos NLTK...")
        nltk_resources = [
            'punkt',           # Tokenizador de sentenças e palavras
            'stopwords',       # Stopwords para vários idiomas
            'wordnet',         # Base de dados léxica
            'averaged_perceptron_tagger'  # Marcador POS
        ]
        
        for resource in nltk_resources:
            try:
                nltk.download(resource, download_dir=str(self.download_dir / "nltk_data"))
                print(f"Recurso NLTK '{resource}' baixado com sucesso.")
            except Exception as e:
                print(f"Erro ao baixar recurso NLTK '{resource}': {str(e)}")
    
    def load_models(self):
        """
        Carrega todos os modelos necessários para o sistema.
        """
        print("Carregando modelos de IA...")
        
        # Carregar modelo de transcrição de fala (Whisper)
        try:
            print("Carregando modelo Whisper...")
            whisper_model = load_whisper_model(model_size="small", use_qualcomm=self.use_qualcomm)
            self.models['whisper_model'] = whisper_model
            print("Modelo Whisper carregado com sucesso.")
        except Exception as e:
            print(f"Erro ao carregar modelo Whisper: {str(e)}")
        
        # Carregar modelos de análise visual (MediaPipe)
        try:
            print("Carregando modelos MediaPipe...")
            face_mesh, pose = load_mediapipe_models(use_qualcomm=self.use_qualcomm)
            self.models['face_mesh'] = face_mesh
            self.models['pose'] = pose
            print("Modelos MediaPipe carregados com sucesso.")
        except Exception as e:
            print(f"Erro ao carregar modelos MediaPipe: {str(e)}")
        
        # Carregar modelos NLP
        try:
            print("Carregando modelos NLP...")
            sentiment_analyzer, text_classifier = load_nlp_models(use_qualcomm=self.use_qualcomm)
            self.models['sentiment_analyzer'] = sentiment_analyzer
            self.models['text_classifier'] = text_classifier
            print("Modelos NLP carregados com sucesso.")
        except Exception as e:
            print(f"Erro ao carregar modelos NLP: {str(e)}")
        
        print(f"Carregamento de modelos concluído. {len(self.models)} modelos carregados.")
        return self.models
    
    def get_model(self, model_name):
        """
        Retorna um modelo específico pelo nome.
        
        Args:
            model_name: Nome do modelo a ser retornado
            
        Returns:
            O modelo solicitado ou None se não encontrado
        """
        return self.models.get(model_name, None)
    
    def get_all_models(self):
        """
        Retorna todos os modelos carregados.
        
        Returns:
            dict: Dicionário com todos os modelos
        """
        return self.models