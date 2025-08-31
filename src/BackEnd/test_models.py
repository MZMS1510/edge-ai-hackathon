#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para testar os modelos de IA do PitchPerfect AI

Este script verifica se todos os modelos de IA estão carregando corretamente
e realiza testes básicos para garantir seu funcionamento.
"""

import os
import sys
import time
import argparse

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.model_manager import ModelManager

def test_whisper_model(model_manager):
    """Testa o modelo Whisper para transcrição de fala"""
    print("\nTestando modelo Whisper...")
    try:
        whisper_model = model_manager.get_model('whisper_model')
        
        if whisper_model:
            print("✅ Modelo Whisper carregado com sucesso!")
            return True
        else:
            print("❌ Falha ao carregar modelo Whisper.")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar modelo Whisper: {str(e)}")
        return False

def test_mediapipe_models(model_manager):
    """Testa os modelos MediaPipe para análise visual"""
    print("\nTestando modelos MediaPipe...")
    try:
        face_mesh = model_manager.get_model('face_mesh')
        pose = model_manager.get_model('pose')
        
        if face_mesh and pose:
            print("✅ Modelos MediaPipe carregados com sucesso!")
            return True
        else:
            print("❌ Falha ao carregar modelos MediaPipe.")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar modelos MediaPipe: {str(e)}")
        return False

def test_nlp_models(model_manager):
    """Testa os modelos NLP para análise de texto"""
    print("\nTestando modelos NLP...")
    try:
        sentiment_analyzer = model_manager.get_model('sentiment_analyzer')
        text_classifier = model_manager.get_model('text_classifier')
        
        if sentiment_analyzer and text_classifier:
            print("✅ Modelos NLP carregados com sucesso!")
            
            # Teste básico do analisador de sentimento
            test_text = "I love this presentation, it's amazing!"
            result = sentiment_analyzer(test_text)
            print(f"Teste de sentimento: '{test_text}' → {result}")
            
            return True
        else:
            print("❌ Falha ao carregar modelos NLP.")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar modelos NLP: {str(e)}")
        return False

def main():
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Testar modelos de IA do PitchPerfect AI')
    parser.add_argument('--use-qualcomm', action='store_true', help='Usar otimizações do Qualcomm AI Hub')
    args = parser.parse_args()
    
    print("="*80)
    print("Testando modelos de IA do PitchPerfect AI")
    print("="*80)
    
    # Inicializar gerenciador de modelos
    print("\nInicializando ModelManager...")
    start_time = time.time()
    try:
        model_manager = ModelManager(use_qualcomm=args.use_qualcomm)
        model_manager.download_nltk_resources()
        models = model_manager.load_models()
        load_time = time.time() - start_time
        print(f"✅ ModelManager inicializado em {load_time:.2f} segundos.")
    except Exception as e:
        print(f"❌ Erro ao inicializar ModelManager: {str(e)}")
        sys.exit(1)
    
    # Testar cada tipo de modelo
    results = {
        "whisper": test_whisper_model(model_manager),
        "mediapipe": test_mediapipe_models(model_manager),
        "nlp": test_nlp_models(model_manager)
    }
    
    # Resumo dos resultados
    print("\n" + "="*80)
    print("Resumo dos testes:")
    for model_name, success in results.items():
        status = "✅ Passou" if success else "❌ Falhou"
        print(f"{model_name}: {status}")
    
    # Verificar se todos os testes passaram
    if all(results.values()):
        print("\n✅ Todos os modelos estão funcionando corretamente!")
        sys.exit(0)
    else:
        print("\n❌ Alguns modelos apresentaram problemas. Verifique os erros acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()