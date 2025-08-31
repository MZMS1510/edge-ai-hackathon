#!/usr/bin/env python3
"""
Camera Fix - Solução para problemas de câmera
Testa e configura câmera para Communication Coach
"""

import cv2
import time
import platform
import subprocess
import os

def check_system_camera():
    """Verifica câmeras disponíveis no sistema"""
    print("🔍 Verificando câmeras do sistema...")
    
    # Verificar sistema operacional
    system = platform.system()
    print(f"📱 Sistema: {system}")
    
    if system == "Windows":
        return check_windows_camera()
    elif system == "Linux":
        return check_linux_camera()
    elif system == "Darwin":  # macOS
        return check_macos_camera()
    else:
        return check_generic_camera()

def check_windows_camera():
    """Verifica câmeras no Windows"""
    print("🪟 Verificando câmeras Windows...")
    
    # Lista de backends para tentar
    backends = [
        cv2.CAP_DSHOW,      # DirectShow
        cv2.CAP_MSMF,       # Media Foundation
        cv2.CAP_ANY,        # Qualquer backend
        cv2.CAP_FFMPEG      # FFmpeg
    ]
    
    for backend in backends:
        print(f"🎥 Testando backend: {backend}")
        
        for i in range(5):
            try:
                cap = cv2.VideoCapture(i, backend)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        print(f"✅ Câmera {i} funcionando com backend {backend}")
                        print(f"   Resolução: {frame.shape}")
                        cap.release()
                        return {'index': i, 'backend': backend, 'working': True}
                    else:
                        print(f"❌ Câmera {i} aberta mas não lê frames")
                        cap.release()
                else:
                    print(f"❌ Câmera {i} não disponível")
            except Exception as e:
                print(f"❌ Erro na câmera {i}: {e}")
    
    return {'working': False}

def check_linux_camera():
    """Verifica câmeras no Linux"""
    print("🐧 Verificando câmeras Linux...")
    
    # Verificar se v4l2 está disponível
    try:
        result = subprocess.run(['v4l2-ctl', '--list-devices'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ v4l2 disponível")
            print(result.stdout)
    except FileNotFoundError:
        print("⚠️ v4l2-ctl não encontrado")
    
    # Testar câmeras
    for i in range(5):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"✅ Câmera {i} funcionando")
                    print(f"   Resolução: {frame.shape}")
                    cap.release()
                    return {'index': i, 'backend': cv2.CAP_ANY, 'working': True}
                else:
                    print(f"❌ Câmera {i} aberta mas não lê frames")
                    cap.release()
            else:
                print(f"❌ Câmera {i} não disponível")
        except Exception as e:
            print(f"❌ Erro na câmera {i}: {e}")
    
    return {'working': False}

def check_macos_camera():
    """Verifica câmeras no macOS"""
    print("🍎 Verificando câmeras macOS...")
    
    for i in range(5):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"✅ Câmera {i} funcionando")
                    print(f"   Resolução: {frame.shape}")
                    cap.release()
                    return {'index': i, 'backend': cv2.CAP_ANY, 'working': True}
                else:
                    print(f"❌ Câmera {i} aberta mas não lê frames")
                    cap.release()
            else:
                print(f"❌ Câmera {i} não disponível")
        except Exception as e:
            print(f"❌ Erro na câmera {i}: {e}")
    
    return {'working': False}

def check_generic_camera():
    """Verificação genérica de câmera"""
    print("🌐 Verificação genérica...")
    
    for i in range(5):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"✅ Câmera {i} funcionando")
                    print(f"   Resolução: {frame.shape}")
                    cap.release()
                    return {'index': i, 'backend': cv2.CAP_ANY, 'working': True}
                else:
                    print(f"❌ Câmera {i} aberta mas não lê frames")
                    cap.release()
            else:
                print(f"❌ Câmera {i} não disponível")
        except Exception as e:
            print(f"❌ Erro na câmera {i}: {e}")
    
    return {'working': False}

def test_camera_settings(camera_info):
    """Testa diferentes configurações de câmera"""
    if not camera_info['working']:
        return None
    
    print("🔧 Testando configurações de câmera...")
    
    cap = cv2.VideoCapture(camera_info['index'], camera_info['backend'])
    
    if not cap.isOpened():
        print("❌ Não foi possível abrir a câmera")
        return None
    
    # Configurações para testar
    configs = [
        {'width': 640, 'height': 480, 'fps': 30},
        {'width': 1280, 'height': 720, 'fps': 30},
        {'width': 1920, 'height': 1080, 'fps': 30},
        {'width': 640, 'height': 480, 'fps': 60}
    ]
    
    best_config = None
    
    for config in configs:
        print(f"🎯 Testando: {config['width']}x{config['height']} @ {config['fps']}fps")
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['width'])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['height'])
        cap.set(cv2.CAP_PROP_FPS, config['fps'])
        
        # Ler alguns frames para testar
        success_count = 0
        for _ in range(10):
            ret, frame = cap.read()
            if ret:
                success_count += 1
            time.sleep(0.1)
        
        if success_count >= 8:  # 80% de sucesso
            print(f"✅ Configuração funcionando: {success_count}/10 frames")
            best_config = config.copy()
            break
        else:
            print(f"❌ Configuração falhou: {success_count}/10 frames")
    
    cap.release()
    return best_config

def create_camera_config(camera_info, best_config):
    """Cria arquivo de configuração da câmera"""
    config = {
        'camera_index': camera_info['index'],
        'backend': camera_info['backend'],
        'width': best_config['width'] if best_config else 640,
        'height': best_config['height'] if best_config else 480,
        'fps': best_config['fps'] if best_config else 30,
        'working': camera_info['working']
    }
    
    # Salvar configuração
    import json
    with open('camera_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("💾 Configuração salva em camera_config.json")
    return config

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico de câmera...")
    
    # Verificar câmeras
    camera_info = check_system_camera()
    
    if camera_info['working']:
        print("✅ Câmera encontrada!")
        
        # Testar configurações
        best_config = test_camera_settings(camera_info)
        
        # Criar configuração
        config = create_camera_config(camera_info, best_config)
        
        print("\n�� Configuração final:")
        print(f"   Índice: {config['camera_index']}")
        print(f"   Backend: {config['backend']}")
        print(f"   Resolução: {config['width']}x{config['height']}")
        print(f"   FPS: {config['fps']}")
        
    else:
        print("❌ Nenhuma câmera funcionando encontrada")
        print("\n💡 Soluções possíveis:")
        print("   1. Verificar se a câmera está conectada")
        print("   2. Verificar permissões de câmera")
        print("   3. Instalar drivers da câmera")
        print("   4. Verificar se outra aplicação está usando a câmera")
