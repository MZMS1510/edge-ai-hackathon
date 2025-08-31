#!/usr/bin/env python3
"""
Teste do Extrator de Áudio

Script para testar a funcionalidade de extração de áudio de vídeos.
Cria um vídeo de teste simples e testa a extração.
"""

import cv2
import numpy as np
import os
import subprocess
from pathlib import Path

def create_test_video(output_path="test_video.mp4", duration=5, fps=30, width=640, height=480):
    """
    Cria um vídeo de teste simples para demonstração
    
    Args:
        output_path: Caminho do vídeo de saída
        duration: Duração em segundos
        fps: Frames por segundo
        width, height: Dimensões do vídeo
    """
    print(f"🎬 Criando vídeo de teste: {output_path}")
    print(f"⏱️  Duração: {duration}s, {fps} FPS, {width}x{height}")
    
    # Configurar codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    total_frames = duration * fps
    
    for frame_num in range(total_frames):
        # Criar frame colorido com texto
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Cor de fundo que muda com o tempo
        color_intensity = int(128 + 127 * np.sin(frame_num * 0.1))
        frame[:, :] = [color_intensity, 100, 200 - color_intensity]
        
        # Adicionar texto
        time_sec = frame_num / fps
        text = f"Edge AI Test Video - {time_sec:.1f}s"
        
        cv2.putText(frame, text, (50, height//2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Frame counter
        counter_text = f"Frame: {frame_num}/{total_frames}"
        cv2.putText(frame, counter_text, (50, height//2 + 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
        
        out.write(frame)
        
        # Progresso
        if frame_num % (fps * 1) == 0:  # A cada segundo
            progress = (frame_num / total_frames) * 100
            print(f"📊 Progresso: {progress:.0f}%")
    
    out.release()
    print(f"✅ Vídeo criado: {output_path}")
    
    # Adicionar áudio com FFmpeg (opcional)
    try:
        print("🎵 Adicionando áudio de teste...")
        temp_video = "temp_" + output_path
        os.rename(output_path, temp_video)
        
        # Comando para adicionar tom de teste
        cmd = [
            'ffmpeg', '-y',
            '-i', temp_video,
            '-f', 'lavfi', '-i', f'sine=frequency=440:duration={duration}',
            '-c:v', 'copy', '-c:a', 'aac',
            '-shortest', output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            os.remove(temp_video)
            print("✅ Áudio adicionado com sucesso!")
        else:
            os.rename(temp_video, output_path)
            print("⚠️  Áudio não adicionado (FFmpeg issue), mas vídeo está OK")
            
    except Exception as e:
        print(f"⚠️  Erro ao adicionar áudio: {e}")

def test_extraction():
    """Testa a extração de áudio"""
    print("\n" + "="*60)
    print("🧪 TESTE DE EXTRAÇÃO DE ÁUDIO")
    print("="*60)
    
    # Criar vídeo de teste se não existir
    test_video = "test_video.mp4"
    if not os.path.exists(test_video):
        create_test_video(test_video, duration=3)  # Vídeo curto para teste
    
    # Importar e testar o extrator
    try:
        import sys
        sys.path.append('.')
        from extract_audio_from_video import extract_audio_from_video, get_video_info
        
        print(f"\n📹 Testando com: {test_video}")
        
        # Mostrar informações do vídeo
        print("\n📊 Informações do vídeo:")
        get_video_info(test_video)
        
        # Testar extração
        output_audio = "test_audio.wav"
        
        print(f"\n🔄 Extraindo áudio para: {output_audio}")
        success = extract_audio_from_video(test_video, output_audio)
        
        if success:
            print("✅ TESTE PASSOU! Áudio extraído com sucesso.")
            
            # Verificar arquivo
            if os.path.exists(output_audio):
                size = os.path.getsize(output_audio)
                print(f"📁 Arquivo criado: {output_audio} ({size:,} bytes)")
                
                # Tentar analisar o áudio
                try:
                    import wave
                    with wave.open(output_audio, 'rb') as wav_file:
                        frames = wav_file.getnframes()
                        sample_rate = wav_file.getframerate()
                        duration = frames / sample_rate
                        channels = wav_file.getnchannels()
                        
                        print(f"🎵 Áudio analisado:")
                        print(f"   Duração: {duration:.1f}s")
                        print(f"   Sample Rate: {sample_rate} Hz")
                        print(f"   Canais: {channels}")
                        print(f"   Frames: {frames:,}")
                        
                except Exception as e:
                    print(f"⚠️  Não foi possível analisar o áudio: {e}")
                
            else:
                print("❌ Arquivo de áudio não foi criado!")
                
        else:
            print("❌ TESTE FALHOU! Erro na extração.")
            
    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado no teste: {e}")

def cleanup():
    """Limpa arquivos de teste"""
    test_files = ["test_video.mp4", "test_audio.wav", "temp_test_video.mp4"]
    
    print("\n🧹 Limpando arquivos de teste...")
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️  Removido: {file}")

def main():
    print("🧪 Teste do Extrator de Áudio - Edge AI Hackathon")
    print("="*60)
    
    # Verificar dependências
    try:
        import cv2
        print("✅ OpenCV disponível")
    except ImportError:
        print("❌ OpenCV não encontrado! Instale com: pip install opencv-python")
        return
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg disponível")
        else:
            print("❌ FFmpeg não funcional")
            return
    except:
        print("❌ FFmpeg não encontrado!")
        return
    
    # Executar teste
    test_extraction()
    
    # Perguntar se quer manter arquivos
    print("\n" + "="*60)
    keep = input("🤔 Manter arquivos de teste? (y/N): ").strip().lower()
    if keep not in ['y', 'yes', 's', 'sim']:
        cleanup()
    else:
        print("📁 Arquivos mantidos para análise manual")
    
    print("\n🎉 Teste concluído!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Teste interrompido")
        cleanup()
    except Exception as e:
        print(f"\n💥 Erro no teste: {e}")
