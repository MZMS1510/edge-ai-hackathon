#!/usr/bin/env python3
"""
Auto Video Processor - Processamento Automatizado de Vídeos

Sistema automatizado que:
1. Monitora pasta de entrada para novos vídeos
2. Extrai áudio automaticamente
3. Move arquivos processados
4. Gera logs de processamento

Uso:
    python auto_video_processor.py
    python auto_video_processor.py --input pasta_videos --output pasta_audios

Autor: Edge AI Hackathon Team
"""

import os
import sys
import time
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import json
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class VideoProcessorHandler(FileSystemEventHandler):
    """Handler para monitorar novos arquivos de vídeo"""
    
    def __init__(self, processor):
        self.processor = processor
        self.processing = set()  # Evitar processamento duplo
    
    def on_created(self, event):
        """Quando um novo arquivo é criado"""
        if not event.is_directory:
            self.process_file(event.src_path)
    
    def on_moved(self, event):
        """Quando um arquivo é movido para a pasta"""
        if not event.is_directory:
            self.process_file(event.dest_path)
    
    def process_file(self, file_path):
        """Processa um arquivo de vídeo"""
        # Aguardar que o arquivo termine de ser copiado
        time.sleep(1)
        
        if file_path in self.processing:
            return
            
        file_path = Path(file_path)
        
        # Verificar se é um vídeo
        if file_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']:
            print(f"🎬 Novo vídeo detectado: {file_path.name}")
            
            self.processing.add(str(file_path))
            
            # Processar em thread separada
            thread = threading.Thread(
                target=self.processor.process_video_file,
                args=(file_path,),
                daemon=True
            )
            thread.start()

class AutoVideoProcessor:
    """Processador automatizado de vídeos"""
    
    def __init__(self, input_dir="input_videos", output_dir="output_audios", 
                 processed_dir="processed_videos", log_file="processing.log"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.processed_dir = Path(processed_dir)
        self.log_file = Path(log_file)
        
        # Criar diretórios
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
        
        # Estatísticas
        self.stats = {
            'processed': 0,
            'failed': 0,
            'total_size': 0,
            'start_time': datetime.now().isoformat()
        }
        
        print(f"📁 Pasta de entrada: {self.input_dir.absolute()}")
        print(f"📁 Pasta de áudio: {self.output_dir.absolute()}")
        print(f"📁 Pasta processados: {self.processed_dir.absolute()}")
    
    def check_ffmpeg(self):
        """Verifica se FFmpeg está disponível"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def extract_audio(self, video_path, output_path, sample_rate=16000, channels=1):
        """Extrai áudio de vídeo usando FFmpeg"""
        try:
            cmd = [
                'ffmpeg', '-y',
                '-i', str(video_path),
                '-vn',
                '-acodec', 'pcm_s16le',
                '-ar', str(sample_rate),
                '-ac', str(channels),
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and output_path.exists():
                return True, None
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "Timeout: Operação demorou muito"
        except Exception as e:
            return False, str(e)
    
    def get_video_info(self, video_path):
        """Obtém informações do vídeo"""
        try:
            cmd = [
                'ffprobe', 
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                format_info = info.get('format', {})
                duration = float(format_info.get('duration', 0))
                
                # Procurar stream de áudio
                audio_streams = [s for s in info['streams'] if s['codec_type'] == 'audio']
                
                return {
                    'duration': duration,
                    'has_audio': len(audio_streams) > 0,
                    'audio_codec': audio_streams[0].get('codec_name', 'unknown') if audio_streams else None,
                    'size': os.path.getsize(video_path)
                }
            else:
                return None
                
        except Exception:
            return None
    
    def log_processing(self, video_path, success, duration=None, error=None):
        """Registra o processamento no log"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'video': str(video_path),
            'success': success,
            'duration': duration,
            'error': error
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"⚠️  Erro ao escrever log: {e}")
    
    def process_video_file(self, video_path):
        """Processa um único arquivo de vídeo"""
        start_time = time.time()
        video_path = Path(video_path)
        
        try:
            print(f"\n🔄 Processando: {video_path.name}")
            
            # Verificar se arquivo existe e não está vazio
            if not video_path.exists() or video_path.stat().st_size == 0:
                raise Exception("Arquivo não existe ou está vazio")
            
            # Obter informações do vídeo
            video_info = self.get_video_info(video_path)
            if not video_info:
                raise Exception("Não foi possível obter informações do vídeo")
            
            if not video_info['has_audio']:
                raise Exception("Vídeo não possui stream de áudio")
            
            print(f"⏱️  Duração: {video_info['duration']:.1f}s")
            print(f"🔊 Codec: {video_info['audio_codec']}")
            print(f"📊 Tamanho: {video_info['size'] / (1024*1024):.1f} MB")
            
            # Gerar nome do arquivo de áudio
            audio_filename = video_path.stem + "_audio.wav"
            audio_path = self.output_dir / audio_filename
            
            # Extrair áudio
            print("🎵 Extraindo áudio...")
            success, error = self.extract_audio(video_path, audio_path)
            
            if success:
                audio_size = audio_path.stat().st_size
                processing_time = time.time() - start_time
                
                print(f"✅ Áudio extraído: {audio_filename}")
                print(f"📊 Tamanho áudio: {audio_size / (1024*1024):.1f} MB")
                print(f"⏱️  Tempo processamento: {processing_time:.1f}s")
                
                # Mover vídeo para pasta de processados
                processed_path = self.processed_dir / video_path.name
                shutil.move(str(video_path), str(processed_path))
                print(f"📁 Vídeo movido para: {processed_path}")
                
                # Atualizar estatísticas
                self.stats['processed'] += 1
                self.stats['total_size'] += video_info['size']
                
                # Log
                self.log_processing(video_path, True, processing_time)
                
            else:
                raise Exception(f"Erro na extração: {error}")
                
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"❌ Erro ao processar {video_path.name}: {e}")
            
            # Mover para pasta de erro
            error_dir = self.input_dir / "errors"
            error_dir.mkdir(exist_ok=True)
            
            try:
                error_path = error_dir / video_path.name
                shutil.move(str(video_path), str(error_path))
                print(f"📁 Vídeo com erro movido para: {error_path}")
            except:
                pass
            
            self.stats['failed'] += 1
            self.log_processing(video_path, False, processing_time, str(e))
    
    def process_existing_files(self):
        """Processa vídeos que já estão na pasta"""
        print("\n🔍 Verificando vídeos existentes...")
        
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        existing_videos = []
        
        for ext in video_extensions:
            existing_videos.extend(self.input_dir.glob(f'*{ext}'))
        
        if existing_videos:
            print(f"📹 Encontrados {len(existing_videos)} vídeos para processar")
            
            for video_path in existing_videos:
                self.process_video_file(video_path)
        else:
            print("📁 Nenhum vídeo encontrado na pasta")
    
    def start_monitoring(self):
        """Inicia monitoramento da pasta"""
        if not self.check_ffmpeg():
            print("❌ FFmpeg não encontrado! Instale FFmpeg primeiro.")
            return
        
        print("\n🎯 Auto Video Processor - Edge AI Hackathon")
        print("=" * 60)
        
        # Processar arquivos existentes
        self.process_existing_files()
        
        # Iniciar monitoramento
        print(f"\n👁️  Monitorando pasta: {self.input_dir.absolute()}")
        print("📝 Para processar um vídeo, simplesmente coloque-o na pasta")
        print("⏹️  Pressione Ctrl+C para parar")
        
        event_handler = VideoProcessorHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.input_dir), recursive=False)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
                
                # Mostrar estatísticas a cada 30 segundos
                if int(time.time()) % 30 == 0:
                    self.print_stats()
                    
        except KeyboardInterrupt:
            print("\n⏹️  Parando monitoramento...")
            observer.stop()
        
        observer.join()
        self.print_final_stats()
    
    def print_stats(self):
        """Mostra estatísticas atuais"""
        print(f"\n📊 Estatísticas: {self.stats['processed']} processados, {self.stats['failed']} falhas")
    
    def print_final_stats(self):
        """Mostra estatísticas finais"""
        total_size_mb = self.stats['total_size'] / (1024*1024)
        
        print("\n" + "="*60)
        print("📊 ESTATÍSTICAS FINAIS")
        print("="*60)
        print(f"✅ Vídeos processados: {self.stats['processed']}")
        print(f"❌ Falhas: {self.stats['failed']}")
        print(f"📊 Total processado: {total_size_mb:.1f} MB")
        print(f"📁 Áudios gerados em: {self.output_dir.absolute()}")
        print(f"📝 Log completo em: {self.log_file.absolute()}")

def main():
    parser = argparse.ArgumentParser(
        description="Processador automatizado de vídeos para extração de áudio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python auto_video_processor.py
  python auto_video_processor.py --input meus_videos --output meus_audios
  python auto_video_processor.py --input C:/Videos --output C:/Audios

Como usar:
  1. Execute o script
  2. Coloque vídeos na pasta 'input_videos'
  3. Os áudios aparecerão em 'output_audios'
  4. Vídeos processados vão para 'processed_videos'
        """
    )
    
    parser.add_argument('--input', default='input_videos',
                       help='Pasta de entrada para vídeos (default: input_videos)')
    parser.add_argument('--output', default='output_audios',
                       help='Pasta de saída para áudios (default: output_audios)')
    parser.add_argument('--processed', default='processed_videos',
                       help='Pasta para vídeos processados (default: processed_videos)')
    
    args = parser.parse_args()
    
    # Instalar watchdog se não estiver disponível
    try:
        import watchdog
    except ImportError:
        print("📦 Instalando watchdog para monitoramento de arquivos...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'watchdog'])
            print("✅ Watchdog instalado!")
        except Exception as e:
            print(f"❌ Erro ao instalar watchdog: {e}")
            print("💡 Instale manualmente: pip install watchdog")
            return
    
    # Criar processador
    processor = AutoVideoProcessor(
        input_dir=args.input,
        output_dir=args.output,
        processed_dir=args.processed
    )
    
    # Iniciar monitoramento
    processor.start_monitoring()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Processo interrompido pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
