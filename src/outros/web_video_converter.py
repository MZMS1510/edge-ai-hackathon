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

import os
import subprocess
import whisper
from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid

app = Flask(__name__)
app.secret_key = 'edge-video-converter-secret-key'

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
    """Extrai áudio de vídeo usando FFmpeg"""
    try:
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
    """Transcreve áudio para texto usando Whisper local"""
    try:
        if not os.path.exists(audio_path):
            return None, f"Arquivo não encontrado: {audio_path}"
        
        print(f"🎤 Carregando modelo Whisper ({model_size})...")
        model = whisper.load_model(model_size)
        
        print(f"🔄 Transcrevendo arquivo: {os.path.basename(audio_path)}")
        result = model.transcribe(audio_path, language=language)
        
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
    return jsonify({
        'ffmpeg': ffmpeg_ok,
        'whisper': True,  # Whisper é instalado via pip
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
            'audio_file': audio_filename
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
            'transcription': transcription[:200] + "..." if len(transcription) > 200 else transcription
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
    print("🚀 Iniciando Edge Video/Audio Tools...")
    print("📹 Video to Audio: MP4, AVI, MOV, MKV, WebM, FLV")
    print("🎵 Audio to Text: WAV, MP3, M4A, FLAC, OGG, AAC")
    print("🌐 Acesse: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
