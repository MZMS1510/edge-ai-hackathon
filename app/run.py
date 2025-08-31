#!/usr/bin/env python3
"""
Communication Coach - Launcher
Arquivo de inicialização da aplicação
"""

import os
import sys
from pathlib import Path

# Adicionar diretório atual ao path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Função principal de inicialização"""
    print("🚀 Communication Coach - Edge AI Hackathon")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not (current_dir / "main.py").exists():
        print("❌ Erro: Execute este arquivo do diretório 'app'")
        print("   cd app && python run.py")
        return
    
    # Verificar dependências
    try:
        import flask
        import cv2
        import mediapipe
        import numpy
        print("✅ Todas as dependências estão disponíveis")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("   Execute: pip install -r requirements.txt")
        return
    
    # Importar e executar aplicação
    try:
        from main import app, socketio
        print("✅ Aplicação carregada com sucesso")
        print("📍 Acesse: http://localhost:5000")
        print("🔄 Pressione Ctrl+C para parar")
        print("-" * 50)
        
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")
        return

if __name__ == '__main__':
    main()
