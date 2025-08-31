#!/usr/bin/env python3
"""
Edge Video to Audio Converter - Frontend Web

Aplicação web Flask 100% local (edge computing) para:
- Upload de vídeos (MP4, AVI, MOV, etc.)
- Extração de áudio automatizada
- Download do áudio em formato WAV

Características:
- 100% local (nenhum dado sai do dispositivo)
- Interface web simples e intuitiva
- Processamento em tempo real
- Suporte a múltiplos formatos de vídeo

Uso:
    python web_video_converter.py
    # Acesse: http://localhost:5000

Autor: Edge AI Hackathon Team
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import json

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import uuid

# Configuração do Flask
app = Flask(__name__)
app.secret_key = 'edge-ai-hackathon-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Configurações
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'm4v'}

# Criar pastas necessárias
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_ffmpeg():
    """Verifica se FFmpeg está disponível"""
    try:
        # Primeiro tenta do PATH atual
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True
    except:
        pass
    
    # Se não funcionar, tenta recarregar PATH do sistema
    try:
        import os
        # Recarregar PATH do Windows
        machine_path = os.environ.get('PATH', '')
        user_path = ''
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as key:
                user_path = winreg.QueryValueEx(key, 'PATH')[0]
        except:
            pass
        
        # Combinar PATHs
        full_path = machine_path + ';' + user_path
        
        # Atualizar PATH atual
        os.environ['PATH'] = full_path
        
        # Tentar novamente
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_video_info(video_path):
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
            video_streams = [s for s in info['streams'] if s['codec_type'] == 'video']
            
            return {
                'duration': duration,
                'has_audio': len(audio_streams) > 0,
                'audio_codec': audio_streams[0].get('codec_name', 'unknown') if audio_streams else None,
                'video_codec': video_streams[0].get('codec_name', 'unknown') if video_streams else None,
                'size': os.path.getsize(video_path),
                'audio_sample_rate': audio_streams[0].get('sample_rate', 'unknown') if audio_streams else None,
                'audio_channels': audio_streams[0].get('channels', 'unknown') if audio_streams else None
            }
        else:
            return None
            
    except Exception as e:
        print(f"Erro ao obter info do vídeo: {e}")
        return None

def extract_audio(video_path, output_path, sample_rate=16000, channels=1):
    """Extrai áudio de vídeo usando FFmpeg"""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-vn',                               # No video
            '-acodec', 'pcm_s16le',             # PCM 16-bit
            '-ar', str(sample_rate),            # Sample rate
            '-ac', str(channels),               # Audio channels
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return True, None
        else:
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        return False, "Timeout: Vídeo muito longo para processar"
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    """Página principal"""
    ffmpeg_available = check_ffmpeg()
    return render_template('index.html', ffmpeg_available=ffmpeg_available)

@app.route('/upload', methods=['POST'])
def upload_video():
    """Processa upload de vídeo"""
    try:
        # Verificar se arquivo foi enviado
        if 'video' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['video']
        
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'Formato não suportado. Use: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        if not check_ffmpeg():
            return jsonify({'error': 'FFmpeg não está disponível. Clique em "Tentar Recarregar FFmpeg" ou instale FFmpeg: winget install FFmpeg'}), 500
        
        # Gerar nomes únicos
        session_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        video_path = os.path.join(UPLOAD_FOLDER, f"{session_id}_{filename}")
        
        # Salvar arquivo
        file.save(video_path)
        
        # Obter informações do vídeo
        video_info = get_video_info(video_path)
        
        if not video_info:
            os.remove(video_path)
            return jsonify({'error': 'Não foi possível ler o arquivo de vídeo'}), 400
        
        if not video_info['has_audio']:
            os.remove(video_path)
            return jsonify({'error': 'O vídeo não possui trilha de áudio'}), 400
        
        # Gerar nome do arquivo de áudio
        audio_filename = f"{session_id}_audio.wav"
        audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)
        
        # Configurações da extração
        sample_rate = int(request.form.get('sample_rate', 16000))
        channels = int(request.form.get('channels', 1))
        
        # Extrair áudio
        success, error = extract_audio(video_path, audio_path, sample_rate, channels)
        
        # Limpar arquivo de vídeo
        os.remove(video_path)
        
        if success:
            audio_size = os.path.getsize(audio_path)
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'audio_filename': audio_filename,
                'video_info': {
                    'duration': f"{video_info['duration']:.1f}s",
                    'original_size': f"{video_info['size'] / (1024*1024):.1f} MB",
                    'audio_codec': video_info['audio_codec'],
                    'video_codec': video_info['video_codec']
                },
                'audio_info': {
                    'size': f"{audio_size / (1024*1024):.1f} MB",
                    'sample_rate': f"{sample_rate} Hz",
                    'channels': channels,
                    'format': 'WAV PCM 16-bit'
                }
            })
        else:
            return jsonify({'error': f'Erro na extração de áudio: {error}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/download/<session_id>')
def download_audio(session_id):
    """Download do arquivo de áudio"""
    try:
        audio_filename = f"{session_id}_audio.wav"
        audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)
        
        if not os.path.exists(audio_path):
            return jsonify({'error': 'Arquivo de áudio não encontrado'}), 404
        
        # Nome original para download
        original_name = f"audio_extraido_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        
        def remove_file():
            """Remove arquivo após download"""
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except:
                pass
        
        # Agendar remoção do arquivo em 1 hora
        import threading
        import time
        def delayed_removal():
            time.sleep(3600)  # 1 hora
            remove_file()
        
        threading.Thread(target=delayed_removal, daemon=True).start()
        
        return send_file(
            audio_path,
            as_attachment=True,
            download_name=original_name,
            mimetype='audio/wav'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro no download: {str(e)}'}), 500

@app.route('/reload_ffmpeg')
def reload_ffmpeg():
    """Força recarregamento do FFmpeg"""
    try:
        # Recarregar PATH
        import os
        machine_path = ''
        user_path = ''
        
        try:
            import winreg
            # PATH da máquina
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment') as key:
                machine_path = winreg.QueryValueEx(key, 'PATH')[0]
        except:
            pass
            
        try:
            import winreg
            # PATH do usuário
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as key:
                user_path = winreg.QueryValueEx(key, 'PATH')[0]
        except:
            pass
        
        # Combinar e atualizar
        full_path = machine_path + ';' + user_path
        os.environ['PATH'] = full_path
        
        # Testar FFmpeg
        ffmpeg_ok = check_ffmpeg()
        
        return jsonify({
            'ffmpeg_available': ffmpeg_ok,
            'path_updated': True,
            'message': 'FFmpeg encontrado!' if ffmpeg_ok else 'FFmpeg ainda não encontrado'
        })
        
    except Exception as e:
        return jsonify({
            'ffmpeg_available': False,
            'path_updated': False,
            'error': str(e)
        })

@app.route('/status')
def status():
    """Status do sistema"""
    return jsonify({
        'ffmpeg_available': check_ffmpeg(),
        'upload_folder_size': len(os.listdir(UPLOAD_FOLDER)),
        'output_folder_size': len(os.listdir(OUTPUT_FOLDER)),
        'max_upload_size': '500 MB',
        'supported_formats': list(ALLOWED_EXTENSIONS)
    })

# Template HTML
def create_template():
    """Cria o template HTML"""
    template_dir = 'templates'
    os.makedirs(template_dir, exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edge Video to Audio Converter</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.2em;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .edge-badge {
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            margin-top: 10px;
        }
        
        .upload-area {
            border: 3px dashed #ccc;
            border-radius: 10px;
            padding: 40px 20px;
            text-align: center;
            margin-bottom: 30px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .upload-area:hover {
            border-color: #667eea;
            background: #f8f9ff;
        }
        
        .upload-area.dragover {
            border-color: #667eea;
            background: #e8f0fe;
        }
        
        .upload-icon {
            font-size: 3em;
            color: #ccc;
            margin-bottom: 20px;
        }
        
        .upload-text {
            color: #666;
            font-size: 1.1em;
            margin-bottom: 15px;
        }
        
        .file-input {
            display: none;
        }
        
        .btn {
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-success {
            background: #28a745;
        }
        
        .btn-success:hover {
            background: #218838;
        }
        
        .options {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .option-group {
            margin-bottom: 15px;
        }
        
        .option-group label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
        }
        
        .option-group select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
        }
        
        .progress {
            width: 100%;
            height: 20px;
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 20px 0;
            display: none;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s ease;
            position: relative;
        }
        
        .progress-bar::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            bottom: 0;
            right: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            animation: shine 1.5s infinite;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        .result {
            display: none;
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .error {
            display: none;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            color: #721c24;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 15px 0;
        }
        
        .info-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        
        .info-card h4 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1em;
        }
        
        .info-list {
            list-style: none;
            padding: 0;
        }
        
        .info-list li {
            padding: 5px 0;
            color: #666;
            font-size: 0.9em;
        }
        
        .warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            color: #856404;
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-ok { background: #28a745; }
        .status-error { background: #dc3545; }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
                margin: 10px;
            }
            
            .info-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Video to Audio Converter</h1>
            <p>Extração de áudio 100% local (edge computing)</p>
            <span class="edge-badge">🔒 100% Privado</span>
        </div>
        
        {% if not ffmpeg_available %}
        <div class="warning">
            <strong>⚠️ FFmpeg não encontrado!</strong><br>
            Para usar este conversor, instale o FFmpeg:<br>
            <code>winget install FFmpeg</code><br><br>
            <button class="btn" onclick="reloadFFmpeg()">🔄 Tentar Recarregar FFmpeg</button>
        </div>
        {% endif %}
        
        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">🎬</div>
            <div class="upload-text">
                Clique aqui ou arraste seu vídeo<br>
                <small>Formatos suportados: MP4, AVI, MOV, MKV, WMV, FLV (max 500MB)</small>
            </div>
            <input type="file" id="videoInput" class="file-input" accept=".mp4,.avi,.mov,.mkv,.wmv,.flv">
            <button class="btn" onclick="document.getElementById('videoInput').click()" {% if not ffmpeg_available %}disabled{% endif %}>
                Selecionar Vídeo
            </button>
        </div>
        
        <div class="options">
            <h3>⚙️ Configurações de Áudio</h3>
            <div class="option-group">
                <label for="sampleRate">Taxa de Amostragem:</label>
                <select id="sampleRate">
                    <option value="16000" selected>16 kHz (Recomendado para fala)</option>
                    <option value="22050">22 kHz (Qualidade média)</option>
                    <option value="44100">44.1 kHz (Qualidade CD)</option>
                    <option value="48000">48 kHz (Qualidade profissional)</option>
                </select>
            </div>
            <div class="option-group">
                <label for="channels">Canais:</label>
                <select id="channels">
                    <option value="1" selected>Mono (Recomendado)</option>
                    <option value="2">Stereo</option>
                </select>
            </div>
        </div>
        
        <div class="progress" id="progress">
            <div class="progress-bar" id="progressBar"></div>
        </div>
        
        <div class="error" id="error"></div>
        
        <div class="result" id="result">
            <h3>✅ Áudio extraído com sucesso!</h3>
            <div class="info-grid" id="infoGrid"></div>
            <div style="text-align: center; margin-top: 20px;">
                <a href="#" id="downloadBtn" class="btn btn-success">📥 Baixar Áudio WAV</a>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #666;">
            <small>
                <span class="status-indicator" id="statusIndicator"></span>
                <span id="statusText">Sistema carregando...</span>
            </small>
        </div>
    </div>

    <script>
        // Verificar status do sistema
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                const indicator = document.getElementById('statusIndicator');
                const text = document.getElementById('statusText');
                
                if (data.ffmpeg_available) {
                    indicator.className = 'status-indicator status-ok';
                    text.textContent = 'Sistema pronto para conversão';
                } else {
                    indicator.className = 'status-indicator status-error';
                    text.textContent = 'FFmpeg não disponível';
                }
            });

        // Upload area drag and drop
        const uploadArea = document.getElementById('uploadArea');
        const videoInput = document.getElementById('videoInput');
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                videoInput.files = files;
                processVideo();
            }
        });
        
        videoInput.addEventListener('change', processVideo);
        
        function processVideo() {
            const file = videoInput.files[0];
            if (!file) return;
            
            // Validar arquivo
            const validTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo'];
            const validExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv'];
            
            const fileName = file.name.toLowerCase();
            const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));
            
            if (!hasValidExtension) {
                showError('Formato de arquivo não suportado. Use: MP4, AVI, MOV, MKV, WMV, FLV');
                return;
            }
            
            if (file.size > 500 * 1024 * 1024) {
                showError('Arquivo muito grande. Máximo: 500MB');
                return;
            }
            
            // Criar FormData
            const formData = new FormData();
            formData.append('video', file);
            formData.append('sample_rate', document.getElementById('sampleRate').value);
            formData.append('channels', document.getElementById('channels').value);
            
            // Mostrar progresso
            showProgress();
            
            // Upload
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                hideProgress();
                
                if (data.success) {
                    showResult(data);
                } else {
                    showError(data.error || 'Erro desconhecido');
                }
            })
            .catch(error => {
                hideProgress();
                showError('Erro de conexão: ' + error.message);
            });
        }
        
        function showProgress() {
            document.getElementById('progress').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            document.getElementById('error').style.display = 'none';
            
            // Simular progresso
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                
                document.getElementById('progressBar').style.width = progress + '%';
            }, 500);
            
            // Guardar interval para limpar depois
            window.progressInterval = interval;
        }
        
        function hideProgress() {
            if (window.progressInterval) {
                clearInterval(window.progressInterval);
            }
            document.getElementById('progressBar').style.width = '100%';
            setTimeout(() => {
                document.getElementById('progress').style.display = 'none';
            }, 500);
        }
        
        function showResult(data) {
            const resultDiv = document.getElementById('result');
            const infoGrid = document.getElementById('infoGrid');
            const downloadBtn = document.getElementById('downloadBtn');
            
            // Criar cards de informação
            infoGrid.innerHTML = `
                <div class="info-card">
                    <h4>📹 Informações do Vídeo</h4>
                    <ul class="info-list">
                        <li><strong>Duração:</strong> ${data.video_info.duration}</li>
                        <li><strong>Tamanho:</strong> ${data.video_info.original_size}</li>
                        <li><strong>Codec Vídeo:</strong> ${data.video_info.video_codec}</li>
                        <li><strong>Codec Áudio:</strong> ${data.video_info.audio_codec}</li>
                    </ul>
                </div>
                <div class="info-card">
                    <h4>🎵 Áudio Extraído</h4>
                    <ul class="info-list">
                        <li><strong>Formato:</strong> ${data.audio_info.format}</li>
                        <li><strong>Tamanho:</strong> ${data.audio_info.size}</li>
                        <li><strong>Sample Rate:</strong> ${data.audio_info.sample_rate}</li>
                        <li><strong>Canais:</strong> ${data.audio_info.channels}</li>
                    </ul>
                </div>
            `;
            
            // Configurar download
            downloadBtn.href = `/download/${data.session_id}`;
            
            resultDiv.style.display = 'block';
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = '❌ ' + message;
            errorDiv.style.display = 'block';
            document.getElementById('result').style.display = 'none';
        }
        
        function reloadFFmpeg() {
            fetch('/reload_ffmpeg')
                .then(response => response.json())
                .then(data => {
                    if (data.ffmpeg_available) {
                        alert('✅ FFmpeg encontrado! Recarregue a página.');
                        location.reload();
                    } else {
                        alert('❌ FFmpeg ainda não encontrado. Certifique-se de que está instalado.');
                    }
                })
                .catch(error => {
                    alert('Erro ao tentar recarregar: ' + error.message);
                });
        }
    </script>
</body>
</html>'''
    
    with open(os.path.join(template_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

def install_flask():
    """Instala Flask se não estiver disponível"""
    try:
        import flask
        return True
    except ImportError:
        print("📦 Instalando Flask...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask'])
            print("✅ Flask instalado!")
            return True
        except Exception as e:
            print(f"❌ Erro ao instalar Flask: {e}")
            return False

def main():
    """Função principal"""
    print("🎯 Edge Video to Audio Converter - Web Interface")
    print("=" * 60)
    
    # Verificar dependências
    if not install_flask():
        print("💡 Instale Flask manualmente: pip install flask")
        return
    
    if not check_ffmpeg():
        print("⚠️  FFmpeg não encontrado. O conversor não funcionará.")
        print("💡 Instale FFmpeg: winget install FFmpeg")
    
    # Criar template
    create_template()
    
    # Configurar Flask
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    print(f"\n🌐 Servidor iniciando...")
    print(f"📁 Pasta de upload: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"📁 Pasta de saída: {os.path.abspath(OUTPUT_FOLDER)}")
    print(f"🔗 Acesse: http://localhost:5000")
    print(f"⏹️  Pressione Ctrl+C para parar\n")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n⏹️  Servidor parado")

if __name__ == '__main__':
    main()
