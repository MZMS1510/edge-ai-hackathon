import os
import torch
import whisper
# Comentando a importação do transformers que está causando problemas
# from transformers import WhisperProcessor, WhisperForConditionalGeneration

def load_whisper_model(model_size="small", use_qualcomm=True):
    """
    Carrega o modelo Whisper para transcrição de fala.
    
    Args:
        model_size: Tamanho do modelo (tiny, base, small, medium, large)
        use_qualcomm: Se True, tenta usar a versão otimizada para Qualcomm
        
    Returns:
        model: Modelo Whisper para processamento de áudio e transcrição
    """
    
    try:
        if use_qualcomm:
            # Tentar carregar modelo otimizado para Qualcomm
            try:
                print("A opção use_qualcomm=True foi ignorada devido à falta do módulo qai_hub_models")
                print("Usando modelo OpenAI Whisper padrão...")
            except Exception as e:
                print(f"Não foi possível carregar o modelo Whisper otimizado para Qualcomm: {str(e)}")
                print("Usando modelo OpenAI Whisper padrão...")
        
        # Carregar modelo padrão do OpenAI Whisper
        print(f"Carregando modelo Whisper-{model_size} padrão...")
        model = whisper.load_model(model_size)
        
        print("Modelo Whisper carregado com sucesso.")
        return model
    
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar modelo Whisper: {str(e)}")