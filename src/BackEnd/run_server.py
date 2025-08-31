#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para iniciar o servidor API do PitchPerfect AI
"""

import os
import sys
import argparse

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Iniciar o servidor API do PitchPerfect AI')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host para o servidor (padrão: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Porta para o servidor (padrão: 5000)')
    parser.add_argument('--debug', action='store_true', help='Executar em modo de depuração')
    args = parser.parse_args()
    
    print("="*80)
    print("Iniciando o servidor API do PitchPerfect AI")
    print("="*80)
    
    # Importar a aplicação Flask
    try:
        from api.app import app
        
        # Iniciar o servidor
        print(f"\nServidor iniciado em http://{args.host}:{args.port}")
        print("Pressione CTRL+C para encerrar.")
        app.run(host=args.host, port=args.port, debug=args.debug)
        
    except Exception as e:
        print(f"\nErro ao iniciar o servidor: {str(e)}")
        print("Verifique se o backend foi inicializado corretamente com 'python initialize.py'")
        sys.exit(1)

if __name__ == "__main__":
    main()