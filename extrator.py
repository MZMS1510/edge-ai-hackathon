#!/usr/bin/env python3
"""
Extrator - Comando Global
Execute de qualquer lugar: python extrator.py
"""

import os
import sys
import subprocess
from pathlib import Path

# Encontrar o diretório do projeto automaticamente
def find_project_dir():
    """Encontra o diretório do projeto baseado na localização deste arquivo"""
    current_file = Path(__file__).resolve()
    
    # Se o arquivo está em src/outros, voltar para src/outros
    if current_file.parent.name == "outros":
        return current_file.parent
    
    # Procurar pasta outros a partir do diretório atual
    current_dir = Path.cwd()
    
    # Procurar nos diretórios pais
    for parent in [current_dir] + list(current_dir.parents):
        outros_dir = parent / "src" / "outros"
        if outros_dir.exists() and (outros_dir / "web_video_converter.py").exists():
            return outros_dir
    
    # Procurar no diretório atual e subdiretórios
    for root, dirs, files in os.walk(current_dir):
        if "web_video_converter.py" in files and "outros" in Path(root).name:
            return Path(root)
    
    return None

def setup_environment():
    """Configura o ambiente Python se necessário"""
    try:
        import flask
        return True
    except ImportError:
        print("⚠️ Flask não encontrado. Tentando instalar...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "opencv-python"])
            print("✅ Dependências instaladas!")
            return True
        except:
            print("❌ Erro ao instalar dependências")
            return False

def main():
    """Função principal - executa o extrator"""
    print("🎯 Edge Video Extractor")
    print("=" * 30)
    
    # Encontrar diretório do projeto
    project_dir = find_project_dir()
    
    if not project_dir:
        print("❌ Não foi possível encontrar o projeto")
        print("💡 Execute este arquivo de dentro do projeto edge-ai-hackathon")
        return 1
    
    print(f"📁 Projeto encontrado: {project_dir}")
    
    # Mudar para o diretório do projeto
    os.chdir(project_dir)
    
    # Verificar dependências
    if not setup_environment():
        return 1
    
    # Verificar se arquivo principal existe
    main_script = project_dir / "web_video_converter.py"
    if not main_script.exists():
        print(f"❌ Arquivo principal não encontrado: {main_script}")
        return 1
    
    print("🚀 Iniciando interface web...")
    print("🌐 Acesse: http://localhost:5000")
    print()
    
    # Executar o servidor
    try:
        subprocess.run([sys.executable, "web_video_converter.py"])
    except KeyboardInterrupt:
        print("\n👋 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
