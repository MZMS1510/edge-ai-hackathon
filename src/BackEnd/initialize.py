#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de inicialização para o backend do PitchPerfect AI

Este script configura o ambiente, baixa os modelos necessários e prepara o sistema para uso.
"""

import os
import sys
import argparse
import time

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.model_manager import ModelManager
from setup import check_dependencies, setup_qualcomm_ai_hub, download_models, setup_nltk

def main():
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Inicializar o backend do PitchPerfect AI')
    parser.add_argument('--skip-models', action='store_true', help='Pular o download dos modelos de IA')
    parser.add_argument('--skip-qualcomm', action='store_true', help='Pular a configuração do Qualcomm AI Hub')
    parser.add_argument('--skip-deps', action='store_true', help='Pular a verificação e instalação de dependências')
    parser.add_argument('--skip-nltk', action='store_true', help='Pular o download de recursos NLTK')
    args = parser.parse_args()
    
    print("="*80)
    print("Inicializando o backend do PitchPerfect AI")
    print("="*80)
    
    # Verificar e instalar dependências
    if not args.skip_deps:
        print("\n[1/5] Verificando dependências...")
        check_dependencies()
    else:
        print("\n[1/5] Verificação de dependências ignorada.")
    
    # Configurar Qualcomm AI Hub
    if not args.skip_qualcomm:
        print("\n[2/5] Configurando Qualcomm AI Hub...")
        setup_qualcomm_ai_hub()
    else:
        print("\n[2/5] Configuração do Qualcomm AI Hub ignorada.")
    
    # Baixar recursos NLTK
    if not args.skip_nltk:
        print("\n[3/5] Baixando recursos NLTK...")
        setup_nltk()
    else:
        print("\n[3/5] Download de recursos NLTK ignorado.")
    
    # Baixar e preparar modelos
    if not args.skip_models:
        print("\n[4/5] Baixando e preparando modelos de IA...")
        download_models()
        
        # Verificar modelos com ModelManager
        print("Verificando modelos com ModelManager...")
        try:
            model_manager = ModelManager(use_qualcomm=not args.skip_qualcomm)
            models = model_manager.load_models()
            print("Modelos carregados com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar modelos com ModelManager: {str(e)}")
            print("Verifique sua conexão com a internet e tente novamente.")
    else:
        print("\n[4/5] Download de modelos ignorado.")
    
    # Verificar API
    print("\n[5/5] Verificando API...")
    try:
        from api.app import app
        print("API configurada com sucesso.")
    except Exception as e:
        print(f"Erro ao configurar API: {str(e)}")
    
    print("\n" + "="*80)
    print("Inicialização concluída!")
    print("Para iniciar o servidor API, execute: python -m api.app")
    print("="*80)

if __name__ == "__main__":
    main()