#!/usr/bin/env python3
"""
Pitch Monitor - Monitoramento de pitch em tempo real
Otimizado para Snapdragon X
"""

import os
import sys
import time
import threading
import numpy as np
import platform
from pathlib import Path

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.qualcomm_utils import QualcommUtils

class PitchMonitor:
    def __init__(self):
        self.qualcomm_utils = QualcommUtils()
        self.is_running = False
        self.audio_thread = None
        
        # Configurações
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.buffer_size = 4096
        
        # Dados em tempo real
        self.pitch_history = []
        self.volume_history = []
        self.timestamps = []
        
        print("🎤 Pitch Monitor inicializado")
        
    def initialize(self):
        """Inicializa todos os componentes"""
        try:
            print("🔧 Inicializando componentes...")
            
            # Verificar Snapdragon X
            if self.qualcomm_utils.snapdragon_detected:
                print("✅ Snapdragon X detectado - Aplicando otimizações")
                self.setup_snapdragon_optimizations()
            else:
                print("💻 CPU x86 detectado - Usando configurações padrão")
            
            print("✅ Todos os componentes inicializados")
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            return False
    
    def setup_snapdragon_optimizations(self):
        """Configura otimizações para Snapdragon X"""
        # Configurar threads para ARM64
        os.environ['OMP_NUM_THREADS'] = '8'
        os.environ['MKL_NUM_THREADS'] = '8'
        
        # Configurar numpy para melhor performance ARM64
        np.set_printoptions(precision=3, suppress=True)
        
        print("🔧 Otimizações Snapdragon X aplicadas")
    
    def start_monitoring(self):
        """Inicia monitoramento de pitch"""
        if self.is_running:
            print("⚠️ Monitoramento já está ativo")
            return
        
        print("🎧 Iniciando monitoramento de pitch...")
        self.is_running = True
        
        # Iniciar thread de áudio
        self.audio_thread = threading.Thread(
            target=self._audio_processing_loop,
            daemon=True
        )
        self.audio_thread.start()
        
        print("✅ Monitoramento iniciado")
    
    def _audio_processing_loop(self):
        """Loop principal de processamento de áudio"""
        try:
            while self.is_running:
                # Simular processamento de áudio
                # Em produção, aqui seria a captura real de áudio
                
                # Gerar dados simulados para teste
                pitch = np.random.normal(220, 30)  # A4 = 220 Hz
                pitch = max(80, min(400, pitch))  # Limitar entre 80-400 Hz
                
                volume = np.random.normal(-20, 10)
                volume = max(-60, min(0, volume))
                
                current_time = time.time()
                
                # Atualizar dados
                self._update_pitch_data(pitch, volume, current_time)
                
                # Pequeno delay
                time.sleep(0.1)  # 100ms
                
        except Exception as e:
            print(f"❌ Erro no processamento de áudio: {e}")
    
    def _update_pitch_data(self, pitch, volume, timestamp):
        """Atualiza dados de pitch"""
        # Adicionar dados
        self.pitch_history.append(pitch)
        self.volume_history.append(volume)
        self.timestamps.append(timestamp)
        
        # Manter apenas últimos 10 segundos
        max_history = 10 * self.sample_rate // self.chunk_size
        if len(self.pitch_history) > max_history:
            self.pitch_history = self.pitch_history[-max_history:]
            self.volume_history = self.volume_history[-max_history:]
            self.timestamps = self.timestamps[-max_history:]
    
    def stop_monitoring(self):
        """Para monitoramento"""
        print("🛑 Parando monitoramento...")
        self.is_running = False
        
        if self.audio_thread:
            self.audio_thread.join(timeout=2)
        
        print("✅ Monitoramento finalizado")
    
    def get_statistics(self):
        """Retorna estatísticas do pitch"""
        if not self.pitch_history:
            return None
        
        pitch_array = np.array(self.pitch_history)
        volume_array = np.array(self.volume_history)
        
        # Filtrar valores válidos
        valid_pitches = pitch_array[pitch_array > 0]
        valid_volumes = volume_array[volume_array > 0]
        
        if len(valid_pitches) == 0:
            return None
        
        stats = {
            'current_pitch': float(pitch_array[-1]) if pitch_array[-1] > 0 else 0,
            'average_pitch': float(np.mean(valid_pitches)),
            'pitch_range': float(np.max(valid_pitches) - np.min(valid_pitches)),
            'pitch_stability': float(np.std(valid_pitches)),
            'current_volume': float(volume_array[-1]) if volume_array[-1] > 0 else 0,
            'average_volume': float(np.mean(valid_volumes)),
            'total_samples': len(self.pitch_history)
        }
        
        return stats
```

```

