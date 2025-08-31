#!/usr/bin/env python3
"""
Camera Management Module
Gerenciamento robusto de câmera com detecção automática
"""

import os
import json
import platform
import cv2
import time
from pathlib import Path

class CameraManager:
    def __init__(self):
        self.script_dir = Path(__file__).parent.parent
        self.config_file = self.script_dir / 'camera_config.json'
        self.camera_config = None
        
    def load_camera_config(self):
        """Carrega configuração da câmera"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.camera_config = json.load(f)
                print(f"📁 Configuração carregada: {self.camera_config}")
                return self.camera_config['working']
            except Exception as e:
                print(f"❌ Erro ao carregar configuração: {e}")
        
        return False

    def find_working_camera(self):
        """Encontra câmera funcionando com configuração robusta"""
        print("🔍 Procurando câmera funcionando...")
        
        # Tentar carregar configuração salva
        if self.load_camera_config():
            return self.camera_config['camera_index']
        
        # Se não tiver configuração, procurar câmera
        system = platform.system()
        
        if system == "Windows":
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        else:
            backends = [cv2.CAP_ANY]
        
        for backend in backends:
            print(f"🎥 Testando backend: {backend}")
            
            for i in range(5):
                try:
                    cap = cv2.VideoCapture(i, backend)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            print(f"✅ Câmera {i} funcionando com backend {backend}")
                            
                            # Testar configurações
                            config = self.test_camera_config(cap, i, backend)
                            if config:
                                self.camera_config = config
                                cap.release()
                                return i
                            else:
                                cap.release()
                        else:
                            print(f"❌ Câmera {i} aberta mas não lê frames")
                            cap.release()
                    else:
                        print(f"❌ Câmera {i} não disponível")
                except Exception as e:
                    print(f"❌ Erro na câmera {i}: {e}")
        
        print("❌ Nenhuma câmera funcionando")
        return None

    def test_camera_config(self, cap, index, backend):
        """Testa configurações da câmera"""
        configs = [
            {'width': 640, 'height': 480, 'fps': 30},
            {'width': 1280, 'height': 720, 'fps': 30},
            {'width': 640, 'height': 480, 'fps': 60}
        ]
        
        for config in configs:
            print(f"🎯 Testando: {config['width']}x{config['height']} @ {config['fps']}fps")
            
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['width'])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['height'])
            cap.set(cv2.CAP_PROP_FPS, config['fps'])
            
            # Testar leitura de frames
            success_count = 0
            for _ in range(5):
                ret, frame = cap.read()
                if ret:
                    success_count += 1
                time.sleep(0.1)
            
            if success_count >= 4:  # 80% de sucesso
                print(f"✅ Configuração funcionando: {success_count}/5 frames")
                
                # Salvar configuração
                final_config = {
                    'camera_index': index,
                    'backend': backend,
                    'width': config['width'],
                    'height': config['height'],
                    'fps': config['fps'],
                    'working': True
                }
                
                with open(self.config_file, 'w') as f:
                    json.dump(final_config, f, indent=2)
                
                return final_config
        
        return None

    def initialize_camera(self, camera_index):
        """Inicializa câmera com configuração otimizada"""
        try:
            # Inicializar câmera com configuração
            if self.camera_config:
                cap = cv2.VideoCapture(camera_index, self.camera_config['backend'])
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_config['width'])
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_config['height'])
                cap.set(cv2.CAP_PROP_FPS, self.camera_config['fps'])
            else:
                cap = cv2.VideoCapture(camera_index)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
            
            if not cap.isOpened():
                raise Exception("Não foi possível abrir a câmera")
            
            print("✅ Câmera inicializada com sucesso")
            return cap
            
        except Exception as e:
            print(f"❌ Erro ao inicializar câmera: {e}")
            return None

    def get_camera_info(self):
        """Retorna informações da câmera"""
        if self.camera_config:
            return {
                'index': self.camera_config['camera_index'],
                'resolution': f"{self.camera_config['width']}x{self.camera_config['height']}",
                'fps': self.camera_config['fps'],
                'backend': self.camera_config['backend'],
                'working': self.camera_config['working']
            }
        return None

    def reset_camera_config(self):
        """Reseta configuração da câmera"""
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            self.camera_config = None
            print("🔄 Configuração da câmera resetada")
        except Exception as e:
            print(f"❌ Erro ao resetar configuração: {e}")
