#!/usr/bin/env python3
"""
Qualcomm Edge AI Hub - Câmera Corrigida
Versão com configuração robusta de câmera
"""

import os
import sys
import time
import threading
import numpy as np
import platform
import json
import cv2
import mediapipe as mp
from pathlib import Path
from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
import queue

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos locais
from utils.qualcomm_utils import QualcommUtils

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qualcomm-edge-ai-camera-fixed'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configurações
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, 'templates')

# Instâncias globais
coach_thread = None
is_coaching = False
camera_working = False
camera_config = None

communication_metrics = {
    'posture_score': 0,
    'gesture_score': 0,
    'eye_contact_score': 0,
    'overall_score': 0,
    'feedback': []
}

def load_camera_config():
    """Carrega configuração da câmera"""
    global camera_config
    
    config_file = os.path.join(SCRIPT_DIR, 'camera_config.json')
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                camera_config = json.load(f)
            print(f"📁 Configuração carregada: {camera_config}")
            return camera_config['working']
        except Exception as e:
            print(f"❌ Erro ao carregar configuração: {e}")
    
    return False

def find_working_camera():
    """Encontra câmera funcionando com configuração robusta"""
    global camera_config
    
    print("🔍 Procurando câmera funcionando...")
    
    # Tentar carregar configuração salva
    if load_camera_config():
        return camera_config['camera_index']
    
    # Se não tiver configuração, procurar câmera
    system = platform.system()
    
    if system == "Windows":
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    else:
        backends = [cv2.CAP_ANY]
    
    for backend in backends:
        print(f"🎥 Testando backend: {backend}")
        
        for i in range(5):
            try:
                cap = cv2.VideoCapture(i, backend)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        print(f"✅ Câmera {i} funcionando com backend {backend}")
                        
                        # Testar configurações
                        config = test_camera_config(cap, i, backend)
                        if config:
                            camera_config = config
                            cap.release()
                            return i
                        else:
                            cap.release()
                    else:
                        print(f"❌ Câmera {i} aberta mas não lê frames")
                        cap.release()
                else:
                    print(f"❌ Câmera {i} não disponível")
            except Exception as e:
                print(f"❌ Erro na câmera {i}: {e}")
    
    print("❌ Nenhuma câmera funcionando")
    return None

def test_camera_config(cap, index, backend):
    """Testa configurações da câmera"""
    configs = [
        {'width': 640, 'height': 480, 'fps': 30},
        {'width': 1280, 'height': 720, 'fps': 30},
        {'width': 640, 'height': 480, 'fps': 60}
    ]
    
    for config in configs:
        print(f"🎯 Testando: {config['width']}x{config['height']} @ {config['fps']}fps")
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['width'])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['height'])
        cap.set(cv2.CAP_PROP_FPS, config['fps'])
        
        # Testar leitura de frames
        success_count = 0
        for _ in range(5):
            ret, frame = cap.read()
            if ret:
                success_count += 1
            time.sleep(0.1)
        
        if success_count >= 4:  # 80% de sucesso
            print(f"✅ Configuração funcionando: {success_count}/5 frames")
            
            # Salvar configuração
            final_config = {
                'camera_index': index,
                'backend': backend,
                'width': config['width'],
                'height': config['height'],
                'fps': config['fps'],
                'working': True
            }
            
            with open('camera_config.json', 'w') as f:
                json.dump(final_config, f, indent=2)
            
            return final_config
    
    return None

@app.route('/')
def index():
    """Página principal"""
    return render_template('communication_coach.html')

@app.route('/communication-coach')
def communication_coach_page():
    """Página do coach de comunicação"""
    return render_template('communication_coach.html')

@app.route('/status')
def status():
    """Status do sistema"""
    qualcomm_utils = QualcommUtils()
    system_info = qualcomm_utils.get_system_info()
    
    return jsonify({
        'snapdragon_detected': qualcomm_utils.snapdragon_detected,
        'system_info': system_info,
        'is_coaching': is_coaching,
        'camera_working': camera_working,
        'camera_config': camera_config,
        'tools_available': qualcomm_utils.check_qualcomm_tools()
    })

@app.route('/start_coaching')
def start_coaching():
    """Inicia análise de comunicação"""
    global coach_thread, is_coaching, camera_working
    
    if is_coaching:
        return jsonify({'error': 'Análise já está ativa'})
    
    try:
        print("🚀 Iniciando análise de comunicação...")
        
        # Verificar câmera
        camera_index = find_working_camera()
        if camera_index is None:
            print("⚠️ Câmera não disponível, usando dados simulados")
            camera_working = False
        else:
            camera_working = True
        
        # Iniciar thread de análise
        is_coaching = True
        coach_thread = threading.Thread(target=coaching_loop, daemon=True, args=(camera_index,))
        coach_thread.start()
        
        print("✅ Thread de coaching iniciada")
        return jsonify({'success': True, 'message': 'Análise iniciada'})
        
    except Exception as e:
        print(f"❌ Erro ao iniciar análise: {e}")
        return jsonify({'error': f'Erro ao iniciar análise: {str(e)}'})

@app.route('/stop_coaching')
def stop_coaching():
    """Para análise de comunicação"""
    global is_coaching
    
    if not is_coaching:
        return jsonify({'error': 'Análise não está ativa'})
    
    try:
        print("�� Parando análise de comunicação...")
        is_coaching = False
        return jsonify({'success': True, 'message': 'Análise parada'})
        
    except Exception as e:
        return jsonify({'error': f'Erro ao parar análise: {str(e)}'})

@app.route('/get_communication_metrics')
def get_communication_metrics():
    """Retorna métricas de comunicação"""
    return jsonify(communication_metrics)

def coaching_loop(camera_index=None):
    """Loop principal de análise de comunicação"""
    global communication_metrics, is_coaching, camera_working
    
    try:
        if camera_index is not None and camera_working:
            print("�� Usando câmera real...")
            real_camera_loop(camera_index)
        else:
            print("🎭 Usando dados simulados...")
            simulated_loop()
            
    except Exception as e:
        print(f"❌ Erro no loop de coaching: {e}")
        print("🔄 Fallback para dados simulados...")
        simulated_loop()

def real_camera_loop(camera_index):
    """Loop com câmera real"""
    global communication_metrics, is_coaching, camera_config
    
    try:
        # Inicializar câmera com configuração
        if camera_config:
            cap = cv2.VideoCapture(camera_index, camera_config['backend'])
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_config['width'])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_config['height'])
            cap.set(cv2.CAP_PROP_FPS, camera_config['fps'])
        else:
            cap = cv2.VideoCapture(camera_index)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
        
        if not cap.isOpened():
            raise Exception("Não foi possível abrir a câmera")
        
        print("✅ Câmera inicializada com sucesso")
        
        # Inicializar MediaPipe
        mp_pose = mp.solutions.pose
        mp_hands = mp.solutions.hands
        mp_face_mesh = mp.solutions.face_mesh
        
        with mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as pose, mp_hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as hands, mp_face_mesh.FaceMesh(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as face_mesh:
            
            print("✅ MediaPipe inicializado")
            
            frame_count = 0
            
            while is_coaching:
                try:
                    ret, frame = cap.read()
                    if not ret:
                        print("❌ Erro ao ler frame, tentando novamente...")
                        time.sleep(0.1)
                        continue
                    
                    frame_count += 1
                    
                    # Processar frame
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Análise real
                    pose_results = pose.process(rgb_frame)
                    posture_score = analyze_posture(pose_results)
                    
                    hands_results = hands.process(rgb_frame)
                    gesture_score = analyze_gestures(hands_results)
                    
                    face_results = face_mesh.process(rgb_frame)
                    eye_contact_score = analyze_eye_contact(frame, face_results)
                    
                    # Calcular score geral
                    overall_score = (posture_score + gesture_score + eye_contact_score) / 3
                    
                    # Gerar feedback
                    feedback = generate_feedback(posture_score, gesture_score, eye_contact_score)
                    
                    # Atualizar métricas
                    communication_metrics.update({
                        'posture_score': posture_score,
                        'gesture_score': gesture_score,
                        'eye_contact_score': eye_contact_score,
                        'overall_score': overall_score,
                        'feedback': feedback
                    })
                    
                    # Enviar dados via WebSocket
                    socketio.emit('communication_data', communication_metrics)
                    
                    # Debug a cada 30 frames
                    if frame_count % 30 == 0:
                        print(f"�� Frame {frame_count}: Postura={posture_score:.1f}, Gestos={gesture_score:.1f}, Olhos={eye_contact_score:.1f}")
                    
                    time.sleep(0.1)  # 100ms para 10 FPS
                    
                except Exception as e:
                    print(f"❌ Erro no processamento: {e}")
                    time.sleep(0.1)
                    
    except Exception as e:
        print(f"❌ Erro na câmera real: {e}")
        raise e
    finally:
        try:
            cap.release()
        except:
            pass

def simulated_loop():
    """Loop com dados simulados"""
    global communication_metrics, is_coaching
    
    print("🎭 Iniciando dados simulados...")
    
    while is_coaching:
        try:
            # Gerar dados simulados realistas
            posture_score = np.random.normal(75, 15)
            posture_score = max(0, min(100, posture_score))
            
            gesture_score = np.random.normal(70, 20)
            gesture_score = max(0, min(100, gesture_score))
            
            eye_contact_score = np.random.normal(80, 10)
            eye_contact_score = max(0, min(100, eye_contact_score))
            
            overall_score = (posture_score + gesture_score + eye_contact_score) / 3
            
            # Gerar feedback
            feedback = generate_feedback(posture_score, gesture_score, eye_contact_score)
            
            # Atualizar métricas
            communication_metrics.update({
                'posture_score': posture_score,
                'gesture_score': gesture_score,
                'eye_contact_score': eye_contact_score,
                'overall_score': overall_score,
                'feedback': feedback
            })
            
            # Enviar dados via WebSocket
            socketio.emit('communication_data', communication_metrics)
            
            print(f"📊 Simulado: Postura={posture_score:.1f}, Gestos={gesture_score:.1f}, Olhos={eye_contact_score:.1f}")
            
            time.sleep(1)  # 1 segundo
            
        except Exception as e:
            print(f"❌ Erro nos dados simulados: {e}")
            time.sleep(1)

# Funções de análise (mantidas iguais)
def analyze_posture(pose_results):
    """Analisa postura usando MediaPipe Pose"""
    if not pose_results.pose_landmarks:
        return 50
    
    landmarks = pose_results.pose_landmarks.landmark
    
    try:
        # Pontos de referência para postura
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
        
        # Calcular alinhamento dos ombros
        shoulder_angle = abs(left_shoulder.y - right_shoulder.y)
        hip_angle = abs(left_hip.y - right_hip.y)
        
        # Calcular postura ereta
        spine_alignment = abs((left_shoulder.y + right_shoulder.y) / 2 - 
                            (left_hip.y + right_hip.y) / 2)
        
        # Score baseado no alinhamento
        shoulder_score = max(0, 100 - shoulder_angle * 200)
        hip_score = max(0, 100 - hip_angle * 200)
        spine_score = max(0, 100 - spine_alignment * 100)
        
        return (shoulder_score + hip_score + spine_score) / 3
        
    except Exception as e:
        print(f"Erro na análise de postura: {e}")
        return 50

def analyze_gestures(hands_results):
    """Analisa gestos usando MediaPipe Hands"""
    if not hands_results.multi_hand_landmarks:
        return 30
    
    try:
        gesture_score = 0
        hand_count = len(hands_results.multi_hand_landmarks)
        
        for hand_landmarks in hands_results.multi_hand_landmarks:
            # Analisar posição das mãos
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            
            # Calcular movimento das mãos
            hand_movement = abs(wrist.y - thumb_tip.y) + abs(wrist.y - index_tip.y)
            
            # Score baseado no movimento
            if hand_movement > 0.1:
                gesture_score += 50
            elif hand_movement > 0.05:
                gesture_score += 30
            else:
                gesture_score += 10
        
        return min(100, gesture_score / hand_count) if hand_count > 0 else 30
        
    except Exception as e:
        print(f"Erro na análise de gestos: {e}")
        return 30

def analyze_eye_contact(frame, face_results):
    """Analisa contato visual usando MediaPipe Face Mesh"""
    if not face_results.multi_face_landmarks:
        return 40
    
    try:
        # Pontos dos olhos
        left_eye = face_results.multi_face_landmarks[0].landmark[33]
        right_eye = face_results.multi_face_landmarks[0].landmark[133]
        
        # Calcular posição dos olhos em relação ao centro da tela
        frame_height, frame_width = frame.shape[:2]
        center_x = frame_width / 2
        center_y = frame_height / 2
        
        eye_center_x = (left_eye.x + right_eye.x) / 2 * frame_width
        eye_center_y = (left_eye.y + right_eye.y) / 2 * frame_height
        
        # Distância do centro
        distance_from_center = np.sqrt((eye_center_x - center_x)**2 + (eye_center_y - center_y)**2)
        
        # Score baseado na proximidade do centro
        max_distance = np.sqrt(center_x**2 + center_y**2)
        eye_contact_score = max(0, 100 - (distance_from_center / max_distance) * 100)
        
        return eye_contact_score
        
    except Exception as e:
        print(f"Erro na análise de contato visual: {e}")
        return 40

def generate_feedback(posture_score, gesture_score, eye_contact_score):
    """Gera feedback personalizado"""
    feedback = []
    
    # Feedback de postura
    if posture_score < 50:
        feedback.append("🔴 Mantenha a postura ereta - alinhe os ombros")
    elif posture_score < 75:
        feedback.append("🟡 Melhore o alinhamento dos ombros")
    else:
        feedback.append("🟢 Postura excelente!")
    
    # Feedback de gestos
    if gesture_score < 30:
        feedback.append("🔴 Use mais gestos com as mãos para expressividade")
    elif gesture_score < 60:
        feedback.append("🟡 Varie seus gestos para maior impacto")
    else:
        feedback.append("🟢 Gestos muito expressivos!")
    
    # Feedback de contato visual
    if eye_contact_score < 50:
        feedback.append("�� Olhe mais para a câmera - mantenha contato visual")
    elif eye_contact_score < 75:
        feedback.append("🟡 Mantenha contato visual consistente")
    else:
        feedback.append("🟢 Contato visual perfeito!")
    
    return feedback

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Cliente conectado"""
    print("🔌 Cliente conectado via WebSocket")
    emit('status', {'message': 'Conectado ao Communication Coach'})

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    print("🔌 Cliente desconectado")

if __name__ == '__main__':
    print("🚀 Iniciando Communication Coach (Câmera Corrigida)...")
    print("📍 Acesse: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
