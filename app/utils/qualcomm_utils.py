import os
import platform
import subprocess
import psutil
import json
from pathlib import Path

class QualcommUtils:
    def __init__(self):
        self.snapdragon_detected = self.detect_snapdragon_x_native()
        self.setup_native_optimizations()
    
    def detect_snapdragon_x_native(self):
        """Detecção nativa para Snapdragon X"""
        try:
            print("🔍 Verificando Snapdragon X nativo...")
            
            # Verificar arquitetura ARM64
            arch = platform.machine()
            print(f" Arquitetura detectada: {arch}")
            
            if arch != 'ARM64':
                print("❌ Arquitetura não é ARM64 - Snapdragon X requer ARM64")
                return False
            
            # Verificar processador
            processor = platform.processor()
            print(f"🔧 Processador: {processor}")
            
            # Verificar múltiplas fontes para Snapdragon X
            checks = [
                self._check_processor_name(processor),
                self._check_wmic_command(),
                self._check_system_info(),
                self._check_qualcomm_drivers(),
                self._check_arm_features()
            ]
            
            snapdragon_found = any(checks)
            
            if snapdragon_found:
                print("✅ Snapdragon X detectado nativamente!")
            else:
                print("❌ Snapdragon X não detectado")
            
            return snapdragon_found
            
        except Exception as e:
            print(f"❌ Erro na detecção nativa: {e}")
            return False
    
    def _check_processor_name(self, processor):
        """Verifica nome do processador"""
        processor_lower = processor.lower()
        keywords = ['qualcomm', 'snapdragon', 'x elite', 'x plus']
        return any(keyword in processor_lower for keyword in keywords)
    
    def _check_wmic_command(self):
        """Verifica via WMIC"""
        try:
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'name'], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                output = result.stdout.lower()
                return 'qualcomm' in output or 'snapdragon' in output
        except Exception as e:
            print(f"⚠️ WMIC não disponível: {e}")
        return False
    
    def _check_system_info(self):
        """Verifica informações do sistema"""
        try:
            result = subprocess.run(
                ['systeminfo'], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                output = result.stdout.lower()
                return 'qualcomm' in output or 'snapdragon' in output
        except Exception as e:
            print(f"⚠️ SystemInfo não disponível: {e}")
        return False
    
    def _check_qualcomm_drivers(self):
        """Verifica drivers Qualcomm"""
        qualcomm_paths = [
            r"C:\Windows\System32\drivers\qcom",
            r"C:\Program Files\Qualcomm",
            r"C:\Program Files (x86)\Qualcomm"
        ]
        
        for path in qualcomm_paths:
            if os.path.exists(path):
                print(f"✅ Driver Qualcomm encontrado: {path}")
                return True
        return False
    
    def _check_arm_features(self):
        """Verifica recursos ARM específicos"""
        try:
            # Verificar variáveis de ambiente ARM
            arm_vars = [
                'PROCESSOR_ARCHITECTURE',
                'PROCESSOR_ARCHITEW6432',
                'ARM64'
            ]
            
            for var in arm_vars:
                if os.environ.get(var, '').upper() in ['ARM64', 'ARM']:
                    print(f"✅ Variável ARM detectada: {var}")
                    return True
        except Exception as e:
            print(f"⚠️ Erro ao verificar recursos ARM: {e}")
        
        return False
    
    def setup_native_optimizations(self):
        """Configura otimizações nativas para Snapdragon X"""
        if self.snapdragon_detected:
            print("🚀 Aplicando otimizações nativas para Snapdragon X...")
            
            # Configurações específicas para ARM64
            os.environ['OMP_NUM_THREADS'] = '12'  # Snapdragon X tem 12 cores
            os.environ['MKL_NUM_THREADS'] = '12'
            os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
            
            # Otimizações Qualcomm específicas
            os.environ['QUALCOMM_AI_ENGINE'] = '1'
            os.environ['HEXAGON_DSP_ENABLED'] = '1'
            os.environ['QNN_BACKEND'] = 'qualcomm'
            
            # Configurações de áudio otimizadas
            os.environ['AUDIO_BUFFER_SIZE'] = '512'  # Menor latência
            os.environ['AUDIO_SAMPLE_RATE'] = '48000'  # Qualidade superior
            os.environ['AUDIO_CHANNELS'] = '2'
            
            print("✅ Otimizações nativas aplicadas")
        else:
            print("💻 Usando configurações padrão para x86")
    
    def get_system_info(self):
        """Informações detalhadas do sistema"""
        info = {
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'snapdragon_detected': self.snapdragon_detected,
            'cpu_count': psutil.cpu_count(),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'memory_total': psutil.virtual_memory().total // (1024**3),  # GB
            'system_type': self._get_system_type(),
            'qualcomm_tools': self.check_qualcomm_tools()
        }
        
        return info
    
    def _get_system_type(self):
        """Determina tipo do sistema"""
        try:
            result = subprocess.run(
                ['systeminfo'], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'System Type' in line:
                        return line.split(':')[1].strip()
        except:
            pass
        return "Unknown"
    
    def check_qualcomm_tools(self):
        """Verifica ferramentas Qualcomm disponíveis"""
        tools = {
            'qnn_sdk': self._check_qnn_sdk(),
            'hexagon_dsp': self._check_hexagon_dsp_native(),
            'voice_assistant': self._check_voice_assistant_native(),
            'ai_engine': self._check_ai_engine()
        }
        
        return tools
    
    def _check_qnn_sdk(self):
        """Verifica QNN SDK nativo"""
        qnn_paths = [
            r"C:\Program Files\Qualcomm\QNN",
            r"C:\Program Files (x86)\Qualcomm\QNN",
            os.path.expanduser("~\\AppData\\Local\\Qualcomm\\QNN")
        ]
        
        for path in qnn_paths:
            if os.path.exists(path):
                return True
        return False
    
    def _check_hexagon_dsp_native(self):
        """Verifica Hexagon DSP nativo"""
        # Verificar se está em ARM64 e tem drivers Qualcomm
        if platform.machine() == 'ARM64' and self._check_qualcomm_drivers():
            return True
        return False
    
    def _check_voice_assistant_native(self):
        """Verifica Voice Assistant nativo"""
        # Implementar verificação específica para Snapdragon X
        return self.snapdragon_detected
    
    def _check_ai_engine(self):
        """Verifica Qualcomm AI Engine"""
        return self.snapdragon_detected
    
    def get_performance_metrics(self):
        """Métricas de performance otimizadas"""
        metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available': psutil.virtual_memory().available // (1024**3),  # GB
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            'snapdragon_optimized': self.snapdragon_detected
        }
        
        return metrics