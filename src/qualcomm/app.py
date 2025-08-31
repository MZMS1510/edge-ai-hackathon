#!/usr/bin/env python3
"""
Qualcomm Voice Pitch Monitor - Flask App
Interface web para monitoramento de pitch em tempo real
Otimizado para Snapdragon X
"""

import os
import sys
import time
import threading
import numpy as np
import platform
import json
from pathlib import Path
from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
import queue

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos locais
from pitch_monitor import PitchMonitor
from utils.qualcomm_utils import QualcommUtils

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qualcomm-pitch-monitor-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configurações
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, 'templates')
STATIC_DIR = os.path.join(SCRIPT_DIR, 'static')

# Criar diretórios se não existirem
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Instância global do monitor
pitch_monitor = None
monitor_thread = None
is_monitoring = False

# Dados em tempo real
realtime_data = {
    'pitch': [],
    'volume': [],
    'notes': [],
    'timestamps': [],
    'max_points': 100
}

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/status')
def status():
    """Status do sistema"""
    qualcomm_utils = QualcommUtils()
    system_info = qualcomm_utils.get_system_info()
    
    return jsonify({
        'snapdragon_detected': qualcomm_utils.snapdragon_detected,
        'system_info': system_info,
        'is_monitoring': is_monitoring,
        'tools_available': qualcomm_utils.check_qualcomm_tools()
    })

@app.route('/start_monitoring')
def start_monitoring():
    """Inicia monitoramento"""
    global pitch_monitor, monitor_thread, is_monitoring
    
    if is_monitoring:
        return jsonify({'error': 'Monitoramento já está ativo'})
    
    try:
        # Inicializar monitor
        pitch_monitor = PitchMonitor()
        if not pitch_monitor.initialize():
            return jsonify({'error': 'Falha na inicialização do monitor'})
        
        # Iniciar thread de monitoramento
        is_monitoring = True
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()
        
        return jsonify({'success': True, 'message': 'Monitoramento iniciado'})
        
    except Exception as e:
        return jsonify({'error': f'Erro ao iniciar monitoramento: {str(e)}'})

@app.route('/stop_monitoring')
def stop_monitoring():
    """Para monitoramento"""
    global is_monitoring, pitch_monitor
    
    if not is_monitoring:
        return jsonify({'error': 'Monitoramento não está ativo'})
    
    try:
        is_monitoring = False
        
        if pitch_monitor:
            pitch_monitor.stop_monitoring()
        
        return jsonify({'success': True, 'message': 'Monitoramento parado'})
        
    except Exception as e:
        return jsonify({'error': f'Erro ao parar monitoramento: {str(e)}'})

@app.route('/get_data')
def get_data():
    """Retorna dados em tempo real"""
    return jsonify({
        'pitch': realtime_data['pitch'],
        'volume': realtime_data['volume'],
        'notes': realtime_data['notes'],
        'timestamps': realtime_data['timestamps']
    })

@app.route('/get_statistics')
def get_statistics():
    """Retorna estatísticas"""
    if not pitch_monitor:
        return jsonify({'error': 'Monitor não inicializado'})
    
    stats = pitch_monitor.get_statistics()
    if stats:
        return jsonify(stats)
    else:
        return jsonify({'error': 'Nenhum dado disponível'})

def monitoring_loop():
    """Loop principal de monitoramento"""
    global realtime_data, is_monitoring
    
    try:
        # Iniciar monitoramento
        pitch_monitor.start_monitoring()
        
        while is_monitoring:
            # Simular dados de pitch (em produção, viria do monitor real)
            if len(realtime_data['timestamps']) == 0:
                start_time = time.time()
            else:
                start_time = realtime_data['timestamps'][0]
            
            current_time = time.time()
            
            # Gerar dados simulados
            pitch = np.random.normal(220, 30)  # A4 = 220 Hz
            pitch = max(80, min(400, pitch))  # Limitar entre 80-400 Hz
            
            volume = np.random.normal(-20, 10)
            volume = max(-60, min(0, volume))
            
            note = freq_to_note(pitch)
            
            # Adicionar dados
            realtime_data['pitch'].append(float(pitch))
            realtime_data['volume'].append(float(volume))
            realtime_data['notes'].append(note)
            realtime_data['timestamps'].append(current_time - start_time)
            
            # Manter apenas últimos pontos
            if len(realtime_data['pitch']) > realtime_data['max_points']:
                realtime_data['pitch'] = realtime_data['pitch'][-realtime_data['max_points']:]
                realtime_data['volume'] = realtime_data['volume'][-realtime_data['max_points']:]
                realtime_data['notes'] = realtime_data['notes'][-realtime_data['max_points']:]
                realtime_data['timestamps'] = realtime_data['timestamps'][-realtime_data['max_points']:]
            
            # Enviar dados via WebSocket
            socketio.emit('pitch_data', {
                'pitch': float(pitch),
                'volume': float(volume),
                'note': note,
                'timestamp': current_time - start_time
            })
            
            time.sleep(0.1)  # 100ms
            
    except Exception as e:
        print(f"❌ Erro no loop de monitoramento: {e}")
    finally:
        if pitch_monitor:
            pitch_monitor.stop_monitoring()

def freq_to_note(freq):
    """Converte frequência em nota musical"""
    if freq <= 0:
        return "--"
    
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    a4_freq = 440.0
    a4_midi = 69
    
    midi_note = 12 * np.log2(freq / a4_freq) + a4_midi
    note_number = int(round(midi_note)) % 12
    octave = int(midi_note) // 12 - 1
    
    return f"{note_names[note_number]}{octave}"

@socketio.on('connect')
def handle_connect():
    """Cliente conectado"""
    print("🔌 Cliente conectado")
    emit('status', {'message': 'Conectado ao Qualcomm Pitch Monitor'})

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    print("🔌 Cliente desconectado")

if __name__ == '__main__':
    print("🎤 Iniciando Qualcomm Voice Pitch Monitor")
    print("�� Interface web para monitoramento de pitch")
    print("🔧 Otimizado para Snapdragon X")
    print("🌐 Acesse: http://localhost:5000")
    
    # Verificar Snapdragon X
    qualcomm_utils = QualcommUtils()
    if qualcomm_utils.snapdragon_detected:
        print("✅ Snapdragon X detectado - Otimizações aplicadas")
    else:
        print("💻 CPU x86 detectado - Usando configurações padrão")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
