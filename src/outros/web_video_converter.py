#!/usr/bin/env python3
"""
Edge Video/Audio Tools - Frontend Web

Aplicação web Flask 100% local (edge computing) com duas ferramentas:
1. Video to Audio Converter: Converte vídeos para áudio WAV
2. Audio to Text Transcriber: Transcreve áudio para texto

Características:
- 100% local (nenhum dado sai do dispositivo)
- Interface web simples e intuitiva
- Processamento em tempo real
- Suporte a múltiplos formatos

Uso:
    python web_video_converter.py
    # Acesse: http://localhost:5000

Autor: Edge AI Hackathon Team
"""

#!/usr/bin/env python3
"""
Edge Video/Audio Tools - Otimizado para Snapdragon X
Versão otimizada para Dell Latitude 5455 com Qualcomm AI Engine
"""

import os
import subprocess
import whisper
import torch
import time
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid
import platform

app = Flask(__name__)
app.secret_key = 'edge-video-converter-snapdragon-optimized'

# Configurações
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(SCRIPT_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(SCRIPT_DIR, 'outputs')
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'}
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'ogg', 'aac'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB máximo

# Criar pastas se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def detect_snapdragon_x():
    """Detecta se está rodando em Snapdragon X"""
    try:
        # Verificar arquitetura ARM64
        if platform.machine() == 'ARM64':
            # Verificar se é Snapdragon X (Windows on ARM)
            cpu_info = platform.processor().lower()
            if 'qualcomm' in cpu_info or 'snapdragon' in cpu_info:
                return True
        return False
    except:
        return False

def optimize_for_snapdragon():
    """Otimizações específicas para Snapdragon X"""
    optimizations = {
        'snapdragon_detected': detect_snapdragon_x(),
        'torch_device': 'cpu',  # Snapdragon X usa CPU otimizado
        'model_size': 'base',   # Modelo menor para edge
        'batch_size': 1,        # Processamento sequencial
        'num_workers': 1        # Single thread para eficiência
    }
    
    if optimizations['snapdragon_detected']:
        print("🚀 Snapdragon X detectado - Aplicando otimizações...")
        # Configurar torch para melhor performance no ARM64
        torch.set_num_threads(4)  # Usar 4 threads no Snapdragon X
        torch.backends.cudnn.enabled = False  # Desabilitar CUDA
    else:
        print("💻 CPU x86 detectado - Usando configurações padrão")
    
    return optimizations

def check_ffmpeg():
    """Verifica se FFmpeg está disponível"""
    try:
        # Adicionar FFmpeg ao PATH se necessário
        ffmpeg_paths = [
            r"C:\ffmpeg\bin",
            r"C:\Program Files\ffmpeg\bin",
            os.path.expanduser("~\\scoop\\apps\\ffmpeg\\current\\bin"),
            os.path.expanduser("~\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-7.1-full_build\\bin")
        ]
        
        current_path = os.environ.get('PATH', '')
        for path in ffmpeg_paths:
            if os.path.exists(path) and path not in current_path:
                os.environ['PATH'] = f"{path};{current_path}"
        
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def allowed_file(filename, file_type='video'):
    """Verifica se o arquivo tem extensão permitida"""
    if file_type == 'video':
        allowed_extensions = ALLOWED_VIDEO_EXTENSIONS
    else:
        allowed_extensions = ALLOWED_AUDIO_EXTENSIONS
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def extract_audio_from_video(video_path, output_audio_path):
    """Extrai áudio de vídeo usando FFmpeg otimizado"""
    try:
        # Otimizações para Snapdragon X
        if detect_snapdragon_x():
            # Usar codec mais eficiente para ARM64
            cmd = [
                'ffmpeg', 
                '-i', video_path,
                '-vn',                      # No video
                '-acodec', 'aac',          # AAC é mais eficiente que PCM
                '-ar', '16000',            # Sample rate 16kHz
                '-ac', '1',                # Mono channel
                '-b:a', '64k',             # Bitrate otimizado
                '-y',                      # Overwrite output
                output_audio_path
            ]
        else:
            # Configuração padrão para x86
            cmd = [
                'ffmpeg', 
                '-i', video_path,
                '-vn',                      # No video
                '-acodec', 'pcm_s16le',     # PCM 16-bit
                '-ar', '16000',             # Sample rate 16kHz
                '-ac', '1',                 # Mono channel
                '-y',                       # Overwrite output
                output_audio_path
            ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Erro FFmpeg: {e}")
        return False

def transcribe_audio_file(audio_path, model_size="base", language=None, speed_mode="balanced"):
    """Transcreve áudio para texto com detecção automática de idioma"""
    try:
        if not os.path.exists(audio_path):
            return None, f"Arquivo não encontrado: {audio_path}"
        
        # Otimizações para Snapdragon X
        optimizations = optimize_for_snapdragon()
        
        print(f"🎤 Carregando modelo Whisper ({model_size})...")
        print(f"🔧 Otimizações: Snapdragon X = {optimizations['snapdragon_detected']}")
        print(f"⚡ Modo de velocidade: {speed_mode}")
        print(f"🌍 Idioma: {'Detecção automática' if language is None else language}")
        
        # Carregar modelo com otimizações
        model = whisper.load_model(
            model_size,
            device=optimizations['torch_device'],
            download_root=None
        )
        
        print(f"🔄 Transcrevendo arquivo: {os.path.basename(audio_path)}")
        
        # Configurações otimizadas para inglês
        if speed_mode == "fast":
            transcribe_options = {
                'language': language,  # None para detecção automática
                'fp16': False,
                'verbose': True,
                'beam_size': 2,  # Melhor que 1 para inglês
                'patience': 2,    # Mais paciência para melhor qualidade
                'length_penalty': 0.0,
                'condition_on_previous_text': False,
                'compression_ratio_threshold': 1.0,
                'logprob_threshold': -1.0,  # Otimizado para inglês
                'no_speech_threshold': 0.6,
            }
        elif speed_mode == "balanced":
            transcribe_options = {
                'language': language,  # None para detecção automática
                'fp16': False,
                'verbose': True,
                'beam_size': 4 if not optimizations['snapdragon_detected'] else 3,
                'patience': 4 if not optimizations['snapdragon_detected'] else 3,
                'length_penalty': 1.0,
                'condition_on_previous_text': True,
                'compression_ratio_threshold': 2.4,
                'logprob_threshold': -0.8,  # Mais restritivo para inglês
                'no_speech_threshold': 0.6,
            }
        else:  # quality
            transcribe_options = {
                'language': language,  # None para detecção automática
                'fp16': False,
                'verbose': True,
                'beam_size': 5,
                'patience': 5,
                'length_penalty': 1.0,
                'condition_on_previous_text': True,
                'compression_ratio_threshold': 2.4,
                'logprob_threshold': -0.6,  # Muito restritivo para máxima qualidade
                'no_speech_threshold': 0.6,
            }
        
        start_time = time.time()
        result = model.transcribe(audio_path, **transcribe_options)
        end_time = time.time()
        
        # Mostrar informações detalhadas sobre a transcrição
        detected_language = result.get("language", "desconhecido")
        language_prob = result.get("language_prob", 0.0)
        print(f"🌍 Idioma detectado: {detected_language} (probabilidade: {language_prob:.2f})")
        print(f"⏱️ Tempo de transcrição: {end_time - start_time:.2f}s")
        print(f"📝 Tamanho da transcrição: {len(result['text'])} caracteres")
        
        # Limpar e validar texto
        text = result["text"].strip()
        if text:
            print(f"✅ Transcrição bem-sucedida")
            return text, None
        else:
            print(f"❌ Nenhum texto transcrito")
            return None, "Nenhum texto foi transcrito"
        
    except Exception as e:
        return None, f"Erro na transcrição: {str(e)}"

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/status')
def status():
    """Verifica status do sistema"""
    ffmpeg_ok = check_ffmpeg()
    optimizations = optimize_for_snapdragon()
    
    return jsonify({
        'ffmpeg': ffmpeg_ok,
        'whisper': True,
        'snapdragon_x': optimizations['snapdragon_detected'],
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'status': 'ok' if ffmpeg_ok else 'ffmpeg_missing'
    })

@app.route('/convert-video-to-audio', methods=['POST'])
def convert_video_to_audio():
    """Converte vídeo para áudio"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar se é vídeo
        if not allowed_file(file.filename, 'video'):
            return jsonify({'error': 'Formato de vídeo não suportado. Use: MP4, AVI, MOV, MKV, WebM, FLV'}), 400
        
        # Verificar FFmpeg
        if not check_ffmpeg():
            return jsonify({'error': 'FFmpeg não encontrado. Instale o FFmpeg primeiro.'}), 500
        
        # Salvar arquivo
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Extrair áudio do vídeo
        audio_filename = f"{Path(unique_filename).stem}_audio.wav"
        audio_path = os.path.join(app.config['OUTPUT_FOLDER'], audio_filename)
        
        if not extract_audio_from_video(file_path, audio_path):
            os.remove(file_path)
            return jsonify({'error': 'Falha na extração de áudio'}), 500
        
        # Limpar arquivo original
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'message': 'Vídeo convertido para áudio com sucesso!',
            'audio_file': audio_filename,
            'optimized_for_snapdragon': detect_snapdragon_x()
        })
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/transcribe-audio', methods=['POST'])
def transcribe_audio():
    """Transcreve áudio para texto com opções de velocidade"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar se é áudio
        if not allowed_file(file.filename, 'audio'):
            return jsonify({'error': 'Formato de áudio não suportado. Use: WAV, MP3, M4A, FLAC, OGG, AAC'}), 400
        
        # Obter configurações de velocidade
        speed_mode = request.form.get('speed_mode', 'balanced')  # fast, balanced, quality
        model_size = request.form.get('model_size', 'base')  # tiny, base, small, medium, large
        
        # Salvar arquivo
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Transcrever áudio - detectar idioma automaticamente
        transcription, error = transcribe_audio_file(file_path, model_size, None, speed_mode)
        if error:
            os.remove(file_path)
            return jsonify({'error': f'Falha na transcrição: {error}'}), 500
        
        # Salvar transcrição
        txt_filename = f"{Path(unique_filename).stem}_transcricao.txt"
        txt_path = os.path.join(app.config['OUTPUT_FOLDER'], txt_filename)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(transcription)
        
        # Limpar arquivo original
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'message': f'Áudio transcrito com sucesso! (Modo: {speed_mode}, Modelo: {model_size})',
            'transcription_file': txt_filename,
            'transcription': transcription[:200] + "..." if len(transcription) > 200 else transcription,
            'optimized_for_snapdragon': detect_snapdragon_x(),
            'speed_mode': speed_mode,
            'model_size': model_size
        })
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download de arquivo processado"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'Arquivo não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro no download: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Iniciando Edge Video/Audio Tools - Otimizado para Snapdragon X")
    print("�� Video to Audio: MP4, AVI, MOV, MKV, WebM, FLV")
    print("🎵 Audio to Text: WAV, MP3, M4A, FLAC, OGG, AAC")
    
    # Detectar e mostrar informações do hardware
    optimizations = optimize_for_snapdragon()
    print(f"🔧 Arquitetura: {platform.machine()}")
    print(f"🔧 Processador: {platform.processor()}")
    print(f"🔧 Snapdragon X: {optimizations['snapdragon_detected']}")
    
    print("🌐 Acesse: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
