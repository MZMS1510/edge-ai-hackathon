#!/usr/bin/env python3
"""
Script de execução do Qualcomm Voice Pitch Monitor
"""

import os
import sys
import subprocess

def check_dependencies():
    """Verifica dependências"""
    print("�� Verificando dependências...")
    
    required_packages = [
        'flask',
        'flask_socketio',
        'numpy',
        'scipy',
        'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Pacotes faltando: {', '.join(missing_packages)}")
        print("📦 Instalando dependências...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Dependências instaladas")
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar dependências")
            return False
    
    return True

def main():
    """Função principal"""
    print("🚀 Qualcomm Voice Pitch Monitor")
    print("=" * 40)
    
    # Verificar dependências
    if not check_dependencies():
        print("❌ Falha na verificação de dependências")
        return
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('app.py'):
        print("❌ Execute este script no diretório src/qualcomm/")
        return
    
    print("\n🎤 Iniciando monitor de pitch...")
    print("🌐 Interface web será aberta em: http://localhost:5000")
    print("🛑 Pressione Ctrl+C para parar")
    
    try:
        # Importar e executar app
        from app import app, socketio
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Monitor finalizado")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()

