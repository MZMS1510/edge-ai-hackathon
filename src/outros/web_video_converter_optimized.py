#!/usr/bin/env python3
"""
Edge Video/Audio Tools - Otimizado para Snapdragon X
Versão otimizada para Dell Latitude 5455 com Qualcomm AI Engine
"""

import os
import subprocess
import whisper
import torch
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

def transcribe_audio_file(audio_path, model_size="base", language="pt"):
    """Transcreve áudio para texto usando Whisper otimizado para Snapdragon X"""
    try:
        if not os.path.exists(audio_path):
            return None, f"Arquivo não encontrado: {audio_path}"
        
        # Otimizações para Snapdragon X
        optimizations = optimize_for_snapdragon()
        
        print(f"🎤 Carregando modelo Whisper ({model_size})...")
        print(f"🔧 Otimizações: Snapdragon X = {optimizations['snapdragon_detected']}")
        
        # Carregar modelo com otimizações
        model = whisper.load_model(
            model_size,
            device=optimizations['torch_device'],
            download_root=None  # Usar cache local
        )
        
        print(f"�� Transcrevendo arquivo: {os.path.basename(audio_path)}")
        
        # Configurações de transcrição otimizadas
        transcribe_options = {
            'language': language,
            'fp16': False,  # Forçar FP32 para compatibilidade
            'verbose': False,
            'condition_on_previous_text': False,  # Desabilitar para edge
            'compression_ratio_threshold': 2.4,
            'logprob_threshold': -1.0,
            'no_speech_threshold': 0.6,
        }
        
        # Se for Snapdragon X, usar configurações mais conservadoras
        if optimizations['snapdragon_detected']:
            transcribe_options.update({
                'beam_size': 1,  # Beam search menor
                'patience': 1,   # Menos paciência
                'length_penalty': 1.0,
            })
        
        result = model.transcribe(audio_path, **transcribe_options)
        
        return result["text"], None
        
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
    """Transcreve áudio para texto"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar se é áudio
        if not allowed_file(file.filename, 'audio'):
            return jsonify({'error': 'Formato de áudio não suportado. Use: WAV, MP3, M4A, FLAC, OGG, AAC'}), 400
        
        # Salvar arquivo
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Transcrever áudio
        transcription, error = transcribe_audio_file(file_path)
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
            'message': 'Áudio transcrito com sucesso!',
            'transcription_file': txt_filename,
            'transcription': transcription[:200] + "..." if len(transcription) > 200 else transcription,
            'optimized_for_snapdragon': detect_snapdragon_x()
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
