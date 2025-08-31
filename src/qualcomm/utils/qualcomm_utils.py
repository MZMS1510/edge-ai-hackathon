#!/usr/bin/env python3
"""
Qualcomm Utils - Utilitários para Snapdragon X
"""

import os
import platform
import subprocess
import psutil

class QualcommUtils:
    def __init__(self):
        self.snapdragon_detected = self.detect_snapdragon_x()
        self.setup_optimizations()
    
    def detect_snapdragon_x(self):
        """Detecta se está rodando em Snapdragon X"""
        try:
            # Verificar arquitetura ARM64
            if platform.machine() == 'ARM64':
                # Verificar processador
                cpu_info = platform.processor().lower()
                if 'qualcomm' in cpu_info or 'snapdragon' in cpu_info:
                    return True
                
                # Verificar informações do sistema
                try:
                    result = subprocess.run(['wmic', 'cpu', 'get', 'name'], 
                                         capture_output=True, text=True)
                    if 'qualcomm' in result.stdout.lower() or 'snapdragon' in result.stdout.lower():
                        return True
                except:
                    pass
                
            return False
        except Exception as e:
            print(f"❌ Erro ao detectar Snapdragon X: {e}")
            return False
    
    def setup_optimizations(self):
        """Configura otimizações para Snapdragon X"""
        if self.snapdragon_detected:
            print("🚀 Snapdragon X detectado - Aplicando otimizações...")
            
            # Configurar threads para ARM64
            os.environ['OMP_NUM_THREADS'] = '8'
            os.environ['MKL_NUM_THREADS'] = '8'
            
            # Configurar para melhor performance ARM64
            os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
            
            print("✅ Otimizações Snapdragon X aplicadas")
        else:
            print("💻 CPU x86 detectado - Usando configurações padrão")
    
    def get_system_info(self):
        """Retorna informações do sistema"""
        info = {
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'snapdragon_detected': self.snapdragon_detected,
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total // (1024**3),  # GB
        }
        
        return info
    
    def get_performance_metrics(self):
        """Retorna métricas de performance"""
        metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available': psutil.virtual_memory().available // (1024**3),  # GB
        }
        
        return metrics
    
    def optimize_for_audio_processing(self):
        """Otimizações específicas para processamento de áudio"""
        if self.snapdragon_detected:
            # Configurar para processamento de áudio em tempo real
            os.environ['AUDIO_BUFFER_SIZE'] = '1024'
            os.environ['AUDIO_SAMPLE_RATE'] = '16000'
            
            print("🎵 Otimizações de áudio aplicadas para Snapdragon X")
        else:
            print("🎵 Usando configurações padrão de áudio")
    
    def check_qualcomm_tools(self):
        """Verifica se ferramentas Qualcomm estão disponíveis"""
        tools = {
            'qnn': self._check_qnn(),
            'hexagon_dsp': self._check_hexagon_dsp(),
            'voice_assistant': self._check_voice_assistant()
        }
        
        return tools
    
    def _check_qnn(self):
        """Verifica se QNN está disponível"""
        try:
            import qnn
            return True
        except ImportError:
            return False
    
    def _check_hexagon_dsp(self):
        """Verifica se Hexagon DSP está disponível"""
        hexagon_paths = [
            "/vendor/lib/rfsa/adsp",
            "/system/lib/rfsa/adsp"
        ]
        
        for path in hexagon_paths:
            if os.path.exists(path):
                return True
        return False
    
    def _check_voice_assistant(self):
        """Verifica se Voice Assistant SDK está disponível"""
        # Implementar verificação específica
        return False
```

```

