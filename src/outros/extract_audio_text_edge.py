#!/usr/bin/env python3
"""
Extract Audio Text - 100% Edge Computing Version

Versão corrigida que usa Whisper local ao invés do Google Speech Recognition
para manter operação 100% edge computing (offline).

ANTES (❌ Não Edge):
- recognize_google() -> Envia dados para Google

DEPOIS (✅ 100% Edge):
- faster-whisper local -> Processamento totalmente local

Autor: Edge AI Hackathon Team
"""

import os
import sys
from pathlib import Path

def install_whisper():
    """Instala faster-whisper se não estiver disponível"""
    try:
        from faster_whisper import WhisperModel
        return True
    except ImportError:
        print("📦 Instalando faster-whisper para operação 100% edge...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'faster-whisper'])
            print("✅ faster-whisper instalado!")
            return True
        except Exception as e:
            print(f"❌ Erro ao instalar faster-whisper: {e}")
            return False

def extract_audio_text_edge():
    """
    Extrai texto de arquivos de áudio usando Whisper 100% local
    """
    print("🎯 Extract Audio Text - 100% Edge Computing")
    print("=" * 60)
    
    # Verificar/instalar Whisper
    if not install_whisper():
        print("❌ Não foi possível instalar Whisper. Abortando.")
        return
    
    from faster_whisper import WhisperModel
    
    # Caminhos
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    audio_dir = os.path.join(ROOT_DIR, 'assets', 'Estudos-livros', 'audios')
    output_txt = os.path.join(ROOT_DIR, 'assets', 'Estudos-livros', 'audios_transcritos_edge.txt')
    
    print(f"📁 Pasta de áudios: {audio_dir}")
    print(f"📤 Arquivo de saída: {output_txt}")
    
    # Verificar se pasta existe
    if not os.path.exists(audio_dir):
        print(f"❌ Pasta não encontrada: {audio_dir}")
        return
    
    # Carregar modelo Whisper local
    print("\n🧠 Carregando modelo Whisper local...")
    print("⏱️  Primeira execução pode demorar (download do modelo)")
    
    try:
        # Modelo pequeno para velocidade, mantém qualidade razoável
        model = WhisperModel("small", device="cpu", compute_type="int8")
        print("✅ Modelo Whisper carregado (100% local)!")
    except Exception as e:
        print(f"❌ Erro ao carregar Whisper: {e}")
        return
    
    # Buscar arquivos de áudio
    audio_files = []
    for ext in ['.wav', '.aiff', '.flac', '.mp3', '.m4a']:
        audio_files.extend(Path(audio_dir).glob(f'*{ext}'))
    
    if not audio_files:
        print(f"⚠️  Nenhum arquivo de áudio encontrado em {audio_dir}")
        return
    
    print(f"\n🎵 Encontrados {len(audio_files)} arquivos de áudio:")
    for audio_file in audio_files:
        print(f"   📄 {audio_file.name}")
    
    # Processar cada arquivo
    all_texts = []
    total_files = len(audio_files)
    
    for i, audio_path in enumerate(audio_files, 1):
        filename = audio_path.name
        print(f"\n📝 [{i}/{total_files}] Transcrevendo: {filename}")
        
        try:
            # Transcrever com Whisper local
            segments, info = model.transcribe(
                str(audio_path), 
                language="pt",  # Português
                word_timestamps=False,
                vad_filter=True,  # Filtro de detecção de voz
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Juntar segmentos
            texto = " ".join([segment.text.strip() for segment in segments])
            
            if texto.strip():
                print(f"✅ Transcrição: {texto[:100]}{'...' if len(texto) > 100 else ''}")
                
                # Adicionar informações extras
                transcription_info = (
                    f"Arquivo: {filename}\n"
                    f"Idioma detectado: {info.language} (confiança: {info.language_probability:.2f})\n"
                    f"Duração: {info.duration:.1f}s\n"
                    f"Texto: {texto}\n"
                    f"---\n"
                )
                all_texts.append(transcription_info)
            else:
                print("⚠️  Nenhum texto detectado")
                all_texts.append(f"Arquivo: {filename}\n[Nenhum texto detectado]\n---\n")
                
        except Exception as e:
            error_msg = f"Arquivo: {filename}\n[Erro na transcrição: {e}]\n---\n"
            all_texts.append(error_msg)
            print(f"❌ Erro: {e}")
    
    # Salvar resultados
    try:
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write("# Transcrições de Áudio - 100% Edge Computing\n")
            f.write(f"# Processado com Whisper local\n")
            f.write(f"# Total de arquivos: {total_files}\n\n")
            f.write('\n'.join(all_texts))
        
        print(f"\n✅ Todas as transcrições salvas em: {output_txt}")
        print(f"📊 Total processado: {len(all_texts)} arquivos")
        print("🔒 100% Edge Computing - Nenhum dado saiu do dispositivo!")
        
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")

def compare_methods():
    """Compara os métodos de transcrição"""
    print("\n📊 COMPARAÇÃO DE MÉTODOS")
    print("=" * 60)
    print("❌ Google Speech Recognition:")
    print("   - Envia áudio para servidores Google")
    print("   - Requer internet")
    print("   - Possível coleta de dados")
    print("   - Latência de rede")
    print("   - Quebra edge computing")
    
    print("\n✅ Whisper Local:")
    print("   - Processamento 100% local")
    print("   - Funciona offline")
    print("   - Privacidade total")
    print("   - Baixa latência")
    print("   - Verdadeiro edge computing")
    print("   - Suporte a múltiplos idiomas")
    print("   - Qualidade profissional")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Transcrição de áudio 100% edge computing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python extract_audio_text_edge.py
  python extract_audio_text_edge.py --compare
        """
    )
    
    parser.add_argument('--compare', action='store_true',
                       help='Mostrar comparação entre métodos')
    
    args = parser.parse_args()
    
    if args.compare:
        compare_methods()
    else:
        extract_audio_text_edge()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Operação interrompida")
    except Exception as e:
        print(f"\n💥 Erro: {e}")
