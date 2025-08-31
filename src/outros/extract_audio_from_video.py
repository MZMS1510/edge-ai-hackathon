#!/usr/bin/env python3
"""
Extract Audio from Video - Edge AI Hackathon

Este script extrai áudio de arquivos de vídeo (MP4, AVI, MOV) e converte para WAV
usando FFmpeg. Ideal para preparar áudio para transcrição com speech recognition.

Uso:
    python extract_audio_from_video.py
    # ou
    python extract_audio_from_video.py --input video.mp4 --output audio.wav

Requisitos:
    - FFmpeg instalado no sistema
    - Python 3.6+

Autor: Edge AI Hackathon Team
"""

import subprocess
import os
import sys
import argparse
from pathlib import Path

def check_ffmpeg():
    """Verifica se FFmpeg está instalado e disponível"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg encontrado: {version_line}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ FFmpeg não encontrado!")
    print("📥 Instale FFmpeg:")
    print("   Windows: https://ffmpeg.org/download.html")
    print("   ou via winget: winget install FFmpeg")
    print("   Linux: sudo apt install ffmpeg")
    print("   Mac: brew install ffmpeg")
    return False

def get_video_info(video_path):
    """Obtém informações do arquivo de vídeo"""
    try:
        cmd = [
            'ffprobe', 
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            import json
            info = json.loads(result.stdout)
            
            # Procurar stream de áudio
            audio_streams = [s for s in info['streams'] if s['codec_type'] == 'audio']
            video_streams = [s for s in info['streams'] if s['codec_type'] == 'video']
            
            duration = float(info['format'].get('duration', 0))
            
            print(f"📁 Arquivo: {os.path.basename(video_path)}")
            print(f"⏱️  Duração: {duration:.1f}s ({duration//60:.0f}:{duration%60:04.1f})")
            print(f"🎥 Streams de vídeo: {len(video_streams)}")
            print(f"🎵 Streams de áudio: {len(audio_streams)}")
            
            if audio_streams:
                audio = audio_streams[0]
                print(f"🔊 Codec de áudio: {audio.get('codec_name', 'unknown')}")
                print(f"📡 Sample rate: {audio.get('sample_rate', 'unknown')} Hz")
                print(f"🔈 Canais: {audio.get('channels', 'unknown')}")
            else:
                print("⚠️  Nenhum stream de áudio encontrado!")
                return False
                
            return True
            
    except Exception as e:
        print(f"❌ Erro ao obter informações do vídeo: {e}")
        return False

def extract_audio_from_video(video_path, output_path, sample_rate=16000, channels=1):
    """
    Extrai áudio de vídeo usando FFmpeg
    
    Args:
        video_path (str): Caminho para o arquivo de vídeo
        output_path (str): Caminho para salvar o áudio WAV
        sample_rate (int): Taxa de amostragem (16000 ideal para speech recognition)
        channels (int): Número de canais (1=mono, 2=stereo)
    
    Returns:
        bool: True se sucesso, False se erro
    """
    try:
        print(f"\n🔄 Extraindo áudio...")
        print(f"📥 Input: {video_path}")
        print(f"📤 Output: {output_path}")
        print(f"🎛️  Config: {sample_rate}Hz, {channels} canal(is)")
        
        # Comando FFmpeg otimizado
        cmd = [
            'ffmpeg',
            '-i', video_path,                    # Input video
            '-vn',                               # No video output
            '-acodec', 'pcm_s16le',             # PCM 16-bit (WAV padrão)
            '-ar', str(sample_rate),            # Sample rate
            '-ac', str(channels),               # Audio channels
            '-y',                               # Overwrite output file
            output_path
        ]
        
        # Executar comando
        print("⚙️  Executando FFmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            # Verificar se arquivo foi criado
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ Áudio extraído com sucesso!")
                print(f"📊 Tamanho do arquivo: {file_size / (1024*1024):.1f} MB")
                return True
            else:
                print("❌ Arquivo de saída não foi criado!")
                return False
        else:
            print(f"❌ Erro no FFmpeg (código {result.returncode}):")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout: Operação demorou muito para completar")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def interactive_mode():
    """Modo interativo para selecionar arquivos"""
    print("🎯 Modo Interativo - Extração de Áudio")
    print("=" * 50)
    
    # Listar vídeos na pasta atual e assets
    current_dir = Path(".")
    assets_dir = Path("../../assets")
    
    video_files = []
    
    # Procurar em diretórios comuns
    search_dirs = [current_dir, assets_dir]
    if assets_dir.exists():
        search_dirs.extend([
            assets_dir / "videos",
            assets_dir / "Estudos-livros" 
        ])
    
    for search_dir in search_dirs:
        if search_dir.exists():
            for ext in ['*.mp4', '*.avi', '*.mov', '*.mkv']:
                video_files.extend(search_dir.glob(ext))
    
    if video_files:
        print(f"\n📹 Vídeos encontrados ({len(video_files)}):")
        for i, video in enumerate(video_files, 1):
            print(f"  {i}. {video}")
        
        # Selecionar arquivo
        try:
            choice = input(f"\n🎯 Escolha um vídeo (1-{len(video_files)}) ou digite o caminho completo: ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(video_files):
                video_path = str(video_files[int(choice) - 1])
            else:
                video_path = choice
                
        except (ValueError, IndexError):
            print("❌ Seleção inválida!")
            return
    else:
        print("📁 Nenhum vídeo encontrado nas pastas padrão.")
        video_path = input("🎬 Digite o caminho completo do vídeo: ").strip()
    
    # Verificar se arquivo existe
    if not os.path.exists(video_path):
        print(f"❌ Arquivo não encontrado: {video_path}")
        return
    
    # Gerar nome de saída automático
    video_name = Path(video_path).stem
    output_path = f"{video_name}_audio.wav"
    
    print(f"\n📤 Arquivo de saída será: {output_path}")
    
    # Confirmar
    confirm = input("🚀 Prosseguir? (Y/n): ").strip().lower()
    if confirm and confirm not in ['y', 'yes', 's', 'sim']:
        print("❌ Operação cancelada")
        return
    
    # Executar extração
    print("\n" + "="*50)
    
    # Mostrar informações do vídeo
    if not get_video_info(video_path):
        print("⚠️  Continuando mesmo com problemas nas informações...")
    
    # Extrair áudio
    if extract_audio_from_video(video_path, output_path):
        print(f"\n🎉 Sucesso! Áudio salvo em: {output_path}")
        print("\n💡 Próximos passos:")
        print(f"   1. Teste o áudio: abra {output_path} em um player")
        print(f"   2. Use para transcrição: python extract_audio_text.py")
    else:
        print("\n💥 Falha na extração!")

def main():
    parser = argparse.ArgumentParser(
        description="Extrai áudio de arquivos de vídeo usando FFmpeg",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python extract_audio_from_video.py
  python extract_audio_from_video.py --input video.mp4 --output audio.wav
  python extract_audio_from_video.py -i presentation.mp4 -r 22050 -c 2
        """
    )
    
    parser.add_argument('-i', '--input', help='Arquivo de vídeo de entrada')
    parser.add_argument('-o', '--output', help='Arquivo de áudio de saída (.wav)')
    parser.add_argument('-r', '--rate', type=int, default=16000, 
                       help='Taxa de amostragem (default: 16000 Hz)')
    parser.add_argument('-c', '--channels', type=int, default=1,
                       help='Número de canais (1=mono, 2=stereo, default: 1)')
    
    args = parser.parse_args()
    
    print("🎵 Extrator de Áudio - Edge AI Hackathon")
    print("=" * 50)
    
    # Verificar FFmpeg
    if not check_ffmpeg():
        return 1
    
    # Modo interativo se não forneceu argumentos
    if not args.input:
        interactive_mode()
        return 0
    
    # Modo linha de comando
    video_path = args.input
    
    # Verificar se arquivo existe
    if not os.path.exists(video_path):
        print(f"❌ Arquivo não encontrado: {video_path}")
        return 1
    
    # Gerar nome de saída se não fornecido
    if not args.output:
        video_name = Path(video_path).stem
        output_path = f"{video_name}_audio.wav"
    else:
        output_path = args.output
    
    print(f"📥 Input: {video_path}")
    print(f"📤 Output: {output_path}")
    
    # Mostrar informações do vídeo
    get_video_info(video_path)
    
    # Extrair áudio
    if extract_audio_from_video(video_path, output_path, args.rate, args.channels):
        print(f"\n✅ Áudio extraído com sucesso: {output_path}")
        return 0
    else:
        print("\n❌ Falha na extração!")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Operação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        sys.exit(1)
