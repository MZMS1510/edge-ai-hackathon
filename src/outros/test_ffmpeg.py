#!/usr/bin/env python3
"""
Teste FFmpeg no Ambiente

Script para testar e configurar FFmpeg no ambiente Python
"""

import subprocess
import os
import sys

def test_ffmpeg_basic():
    """Teste básico do FFmpeg"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg funcionando!")
            print(f"Versão: {result.stdout.split()[2]}")
            return True
        else:
            print("❌ FFmpeg retornou erro")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg não encontrado no PATH")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar FFmpeg: {e}")
        return False

def reload_system_path():
    """Recarrega PATH do sistema Windows"""
    try:
        print("🔄 Recarregando PATH do sistema...")
        
        # Obter PATH do sistema
        import winreg
        
        machine_path = ''
        user_path = ''
        
        # PATH da máquina (todos os usuários)
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment') as key:
                machine_path = winreg.QueryValueEx(key, 'PATH')[0]
            print(f"✅ PATH da máquina carregado ({len(machine_path)} chars)")
        except Exception as e:
            print(f"⚠️  Erro ao carregar PATH da máquina: {e}")
        
        # PATH do usuário
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as key:
                user_path = winreg.QueryValueEx(key, 'PATH')[0]
            print(f"✅ PATH do usuário carregado ({len(user_path)} chars)")
        except Exception as e:
            print(f"⚠️  Erro ao carregar PATH do usuário: {e}")
        
        # Combinar PATHs
        full_path = machine_path + ';' + user_path
        
        # Atualizar PATH no ambiente atual
        os.environ['PATH'] = full_path
        print(f"✅ PATH atualizado no ambiente Python")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao recarregar PATH: {e}")
        return False

def find_ffmpeg_manually():
    """Procura FFmpeg em locais comuns"""
    common_paths = [
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
        r"C:\Program Files (x86)\ffmpeg\bin",
        r"C:\tools\ffmpeg\bin",
        r"C:\Users\{}\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-*\bin".format(os.getenv('USERNAME'))
    ]
    
    print("🔍 Procurando FFmpeg em locais comuns...")
    
    import glob
    
    for path_pattern in common_paths:
        if '*' in path_pattern:
            # Usar glob para padrões com wildcard
            matches = glob.glob(path_pattern)
            for match in matches:
                if os.path.exists(match):
                    ffmpeg_exe = os.path.join(match, 'ffmpeg.exe')
                    if os.path.exists(ffmpeg_exe):
                        print(f"✅ FFmpeg encontrado em: {match}")
                        return match
        else:
            ffmpeg_exe = os.path.join(path_pattern, 'ffmpeg.exe')
            if os.path.exists(ffmpeg_exe):
                print(f"✅ FFmpeg encontrado em: {path_pattern}")
                return path_pattern
    
    print("❌ FFmpeg não encontrado em locais comuns")
    return None

def add_ffmpeg_to_path(ffmpeg_path):
    """Adiciona FFmpeg ao PATH atual"""
    try:
        current_path = os.environ.get('PATH', '')
        if ffmpeg_path not in current_path:
            os.environ['PATH'] = current_path + ';' + ffmpeg_path
            print(f"✅ Adicionado ao PATH: {ffmpeg_path}")
            return True
        else:
            print(f"ℹ️  Já no PATH: {ffmpeg_path}")
            return True
    except Exception as e:
        print(f"❌ Erro ao adicionar ao PATH: {e}")
        return False

def main():
    print("🧪 Teste de FFmpeg - Edge AI Hackathon")
    print("=" * 50)
    
    # Teste inicial
    print("\n1. Teste inicial:")
    if test_ffmpeg_basic():
        print("🎉 FFmpeg já está funcionando!")
        return
    
    # Tentar recarregar PATH
    print("\n2. Recarregando PATH do sistema:")
    if reload_system_path():
        if test_ffmpeg_basic():
            print("🎉 FFmpeg funcionando após recarregar PATH!")
            return
    
    # Procurar manualmente
    print("\n3. Procura manual:")
    ffmpeg_path = find_ffmpeg_manually()
    
    if ffmpeg_path:
        if add_ffmpeg_to_path(ffmpeg_path):
            if test_ffmpeg_basic():
                print("🎉 FFmpeg funcionando após adicionar ao PATH!")
                print(f"\n💡 Para corrigir permanentemente, adicione ao PATH do sistema:")
                print(f"   {ffmpeg_path}")
                return
    
    # Se chegou aqui, não encontrou
    print("\n❌ FFmpeg não foi encontrado!")
    print("\n🛠️  Soluções:")
    print("1. Instalar via winget: winget install FFmpeg")
    print("2. Baixar de: https://ffmpeg.org/download.html")
    print("3. Adicionar ao PATH do sistema manualmente")

if __name__ == "__main__":
    main()
