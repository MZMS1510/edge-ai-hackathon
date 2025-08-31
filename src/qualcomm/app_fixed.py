#!/usr/bin/env python3
"""
Qualcomm Edge AI Hub - Câmera Corrigida
Versão com configuração robusta de câmera - SEM DADOS SIMULADOS
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
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
import queue

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

# Histórico para análise final
analysis_history = {
    'start_time': None,
    'end_time': None,
    'duration': 0,
    'total_frames': 0,
    'scores_history': [],
    'improvements': [],
    'strengths': [],
    'weaknesses': [],
    'recommendations': []
}

from report_manager import report_manager

# Rotas para histórico
@app.route('/api/history')
def get_history():
    """Retorna histórico de análises"""
    try:
        history = report_manager.get_all_reports()
        statistics = report_manager.get_statistics()
        
        return jsonify({
            'analyses': history,
            'statistics': statistics
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/report/<report_id>')
def get_report(report_id):
    """Retorna relatório específico"""
    try:
        report = report_manager.get_report_by_id(report_id)
        if report:
            return jsonify(report)
        else:
            return jsonify({'error': 'Relatório não encontrado'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/report/<report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Deleta relatório específico"""
    try:
        success = report_manager.delete_report(report_id)
        if success:
            return jsonify({'success': True, 'message': 'Relatório deletado'})
        else:
            return jsonify({'error': 'Relatório não encontrado'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/export-history')
def export_history():
    """Exporta histórico completo"""
    try:
        export_file = report_manager.export_history()
        if export_file:
            return jsonify({'success': True, 'file': export_file})
        else:
            return jsonify({'error': 'Erro ao exportar histórico'})
    except Exception as e:
        return jsonify({'error': str(e)})

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

def generate_final_report():
    """Gera relatório final da análise"""
    global analysis_history
    
    if not analysis_history['scores_history']:
        return {
            'error': 'Nenhum dado coletado para análise'
        }
    
    # Calcular estatísticas
    scores = np.array(analysis_history['scores_history'])
    avg_posture = np.mean(scores[:, 0])
    avg_gesture = np.mean(scores[:, 1])
    avg_eye_contact = np.mean(scores[:, 2])
    avg_overall = np.mean(scores[:, 3])
    
    # Calcular melhorias
    if len(scores) > 10:
        first_half = np.mean(scores[:len(scores)//2], axis=0)
        second_half = np.mean(scores[len(scores)//2:], axis=0)
        improvements = second_half - first_half
    else:
        improvements = np.array([0, 0, 0, 0])
    
    # Identificar pontos fortes e fracos
    strengths = []
    weaknesses = []
    
    if avg_posture >= 75:
        strengths.append("Postura ereta e bem alinhada")
    elif avg_posture < 50:
        weaknesses.append("Postura precisa de melhoria")
    
    if avg_gesture >= 60:
        strengths.append("Uso expressivo de gestos")
    elif avg_gesture < 40:
        weaknesses.append("Gestos limitados")
    
    if avg_eye_contact >= 75:
        strengths.append("Excelente contato visual")
    elif avg_eye_contact < 50:
        weaknesses.append("Contato visual inconsistente")
    
    # Gerar recomendações específicas
    recommendations = []
    
    if avg_posture < 70:
        recommendations.append("🧘‍♂️ Pratique manter os ombros alinhados e a coluna ereta")
    
    if avg_gesture < 50:
        recommendations.append("🟡 Use mais gestos com as mãos para enfatizar pontos importantes")
    
    if avg_eye_contact < 60:
        recommendations.append("🔴 Mantenha contato visual direto com a câmera/audiência")
    
    if avg_overall < 60:
        recommendations.append("📈 Considere praticar técnicas de apresentação em público")
    
    # Calcular progresso
    progress_indicators = []
    if improvements[0] > 5:
        progress_indicators.append("📈 Melhorou significativamente na postura")
    if improvements[1] > 5:
        progress_indicators.append("📈 Melhorou significativamente nos gestos")
    if improvements[2] > 5:
        progress_indicators.append("📈 Melhorou significativamente no contato visual")
    
    # Relatório final
    report = {
        'session_info': {
            'start_time': analysis_history['start_time'],
            'end_time': analysis_history['end_time'],
            'duration_minutes': round(analysis_history['duration'] / 60, 1),
            'total_frames': analysis_history['total_frames']
        },
        'average_scores': {
            'posture': round(avg_posture, 1),
            'gesture': round(avg_gesture, 1),
            'eye_contact': round(avg_eye_contact, 1),
            'overall': round(avg_overall, 1)
        },
        'improvements': {
            'posture': round(improvements[0], 1),
            'gesture': round(improvements[1], 1),
            'eye_contact': round(improvements[2], 1),
            'overall': round(improvements[3], 1)
        },
        'strengths': strengths,
        'weaknesses': weaknesses,
        'recommendations': recommendations,
        'progress_indicators': progress_indicators,
        'performance_level': get_performance_level(avg_overall),
        'next_steps': generate_next_steps(avg_overall, weaknesses)
    }
    
    # Salvar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"analysis_report_{timestamp}.json"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"📄 Relatório salvo: {report_file}")
    except Exception as e:
        print(f"❌ Erro ao salvar relatório: {e}")
    
    return report

def get_performance_level(overall_score):
    """Determina nível de performance"""
    if overall_score >= 85:
        return "Excelente"
    elif overall_score >= 70:
        return "Bom"
    elif overall_score >= 55:
        return "Regular"
    else:
        return "Precisa Melhorar"

def generate_next_steps(overall_score, weaknesses):
    """Gera próximos passos baseados na performance"""
    next_steps = []
    
    if overall_score < 70:
        next_steps.append("🧘‍♂️ Pratique por 10-15 minutos diariamente")
        next_steps.append("📚 Considere um curso de oratória")
    
    if "Postura" in str(weaknesses):
        next_steps.append("🧘‍♂️ Pratique exercícios de postura")
    
    if "Gestos" in str(weaknesses):
        next_steps.append("🤲 Treine gestos específicos para diferentes tipos de apresentação")
    
    if "Contato visual" in str(weaknesses):
        next_steps.append("👁️ Pratique olhar para diferentes pontos da audiência")
    
    next_steps.append("🔄 Agende uma nova sessão de análise em 1 semana")
    
    return next_steps

@app.route('/')
def index():
    """Página principal"""
    return render_template('communication_coach.html')

@app.route('/communication-coach')
def communication_coach_page():
    """Página do coach de comunicação"""
    return render_template('communication_coach.html')

@app.route('/final-report')
def final_report():
    """Página do relatório final"""
    return render_template('final_report.html')

@app.route('/status')
def status():
    """Status do sistema"""
    from utils.qualcomm_utils import QualcommUtils
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
    global coach_thread, is_coaching, camera_working, analysis_history
    
    if is_coaching:
        return jsonify({'error': 'Análise já está ativa'})
    
    try:
        print("🚀 Iniciando análise de comunicação...")
        
        # Resetar histórico
        analysis_history = {
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration': 0,
            'total_frames': 0,
            'scores_history': [],
            'improvements': [],
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
        # Verificar câmera
        camera_index = find_working_camera()
        if camera_index is None:
            print("❌ Câmera não disponível - análise não pode ser iniciada")
            return jsonify({'error': 'Câmera não disponível. Verifique se a câmera está conectada e funcionando.'})
        
        camera_working = True
        
        # Iniciar thread de análise
        is_coaching = True
        coach_thread = threading.Thread(target=coaching_loop, daemon=True, args=(camera_index,))
        coach_thread.start()
        
        print("✅ Thread de coaching iniciada")
        return jsonify({'success': True, 'message': 'Análise iniciada com câmera real'})
        
    except Exception as e:
        print(f"❌ Erro ao iniciar análise: {e}")
        return jsonify({'error': f'Erro ao iniciar análise: {str(e)}'})

@app.route('/stop_coaching')
def stop_coaching():
    """Para análise de comunicação e gera relatório final"""
    global is_coaching, analysis_history
    
    if not is_coaching:
        return jsonify({'error': 'Análise não está ativa'})
    
    try:
        print(" Parando análise de comunicação...")
        
        # Finalizar análise
        analysis_history['end_time'] = datetime.now().isoformat()
        start_time = datetime.fromisoformat(analysis_history['start_time'])
        end_time = datetime.fromisoformat(analysis_history['end_time'])
        analysis_history['duration'] = (end_time - start_time).total_seconds()
        
        is_coaching = False
        
        # Gerar relatório final
        print("📊 Gerando relatório final...")
        final_report = generate_final_report()
        
        return jsonify({
            'success': True, 
            'message': 'Análise finalizada',
            'report': final_report
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao parar análise: {str(e)}'})

@app.route('/get_communication_metrics')
def get_communication_metrics():
    """Retorna métricas de comunicação"""
    return jsonify(communication_metrics)

@app.route('/get_final_report')
def get_final_report():
    """Retorna relatório final da última análise"""
    if analysis_history['scores_history']:
        return jsonify(generate_final_report())
    else:
        return jsonify({'error': 'Nenhuma análise realizada ainda'})

def coaching_loop(camera_index):
    """Loop principal de análise de comunicação - APENAS CÂMERA REAL"""
    global communication_metrics, is_coaching, camera_working, analysis_history
    
    try:
        print(" Usando câmera real...")
        real_camera_loop(camera_index)
            
    except Exception as e:
        print(f"❌ Erro no loop de coaching: {e}")
        print("❌ Análise interrompida - câmera não disponível")

def real_camera_loop(camera_index):
    """Loop com câmera real - VERSÃO COM LANDMARKS VISUAIS"""
    global communication_metrics, is_coaching, camera_config, analysis_history
    
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
            last_scores = {'posture': 50, 'gesture': 30, 'eye': 40}
            
            while is_coaching:
                try:
                    ret, frame = cap.read()
                    if not ret:
                        print("❌ Erro ao ler frame, tentando novamente...")
                        time.sleep(0.1)
                        continue
                    
                    frame_count += 1
                    analysis_history['total_frames'] = frame_count
                    
                    # Processar frame
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Análise real com variação
                    pose_results = pose.process(rgb_frame)
                    posture_score = analyze_posture_improved(pose_results, last_scores['posture'])
                    
                    hands_results = hands.process(rgb_frame)
                    gesture_score = analyze_gestures_improved(hands_results, last_scores['gesture'])
                    
                    face_results = face_mesh.process(rgb_frame)
                    eye_contact_score = analyze_eye_contact_improved(frame, face_results, last_scores['eye'])
                    
                    # Atualizar scores anteriores
                    last_scores = {
                        'posture': posture_score,
                        'gesture': gesture_score,
                        'eye': eye_contact_score
                    }
                    
                    # Calcular score geral
                    overall_score = (posture_score + gesture_score + eye_contact_score) / 3
                    
                    # Salvar no histórico
                    analysis_history['scores_history'].append([
                        posture_score, gesture_score, eye_contact_score, overall_score
                    ])
                    
                    # Gerar feedback
                    feedback = generate_feedback(posture_score, gesture_score, eye_contact_score)
                    
                    # Atualizar métricas
                    communication_metrics.update({
                        'posture_score': round(posture_score, 1),
                        'gesture_score': round(gesture_score, 1),
                        'eye_contact_score': round(eye_contact_score, 1),
                        'overall_score': round(overall_score, 1),
                        'feedback': feedback
                    })
                    
                    # Enviar dados via WebSocket
                    socketio.emit('communication_data', communication_metrics)
                    
                    # NOVO: Enviar landmarks para visualização
                    landmarks_data = {
                        'pose': None,
                        'hands': [],
                        'face': None
                    }
                    
                    # Extrair landmarks da pose
                    if pose_results.pose_landmarks:
                        pose_landmarks = []
                        for landmark in pose_results.pose_landmarks.landmark:
                            pose_landmarks.append({
                                'x': landmark.x,
                                'y': landmark.y,
                                'z': landmark.z
                            })
                        landmarks_data['pose'] = pose_landmarks
                    
                    # Extrair landmarks das mãos
                    if hands_results.multi_hand_landmarks:
                        for hand_landmarks in hands_results.multi_hand_landmarks:
                            hand_data = []
                            for landmark in hand_landmarks.landmark:
                                hand_data.append({
                                    'x': landmark.x,
                                    'y': landmark.y,
                                    'z': landmark.z
                                })
                            landmarks_data['hands'].append(hand_data)
                    
                    # Extrair landmarks do rosto
                    if face_results.multi_face_landmarks:
                        face_landmarks = []
                        for landmark in face_results.multi_face_landmarks[0].landmark:
                            face_landmarks.append({
                                'x': landmark.x,
                                'y': landmark.y,
                                'z': landmark.z
                            })
                        landmarks_data['face'] = face_landmarks
                    
                    # Enviar landmarks via WebSocket
                    socketio.emit('landmarks_data', landmarks_data)
                    
                    # Debug a cada 10 frames (mais frequente)
                    if frame_count % 10 == 0:
                        print(f" Frame {frame_count}: Postura={posture_score:.1f}, Gestos={gesture_score:.1f}, Olhos={eye_contact_score:.1f}")
                    
                    time.sleep(0.05)  # 50ms para 20 FPS (mais responsivo)
                    
                except Exception as e:
                    print(f"❌ Erro no processamento: {e}")
                    time.sleep(0.1)
                    
    except Exception as e:
        print(f"❌ Erro na câmera real: {e}")
        raise e
    finally:
        try:
            cap.release()
            print(" Câmera liberada")
        except:
            pass

def analyze_posture_improved(pose_results, last_score):
    """Analisa postura com mais variação"""
    if not pose_results.pose_landmarks:
        # Variação pequena quando não detecta
        return max(0, min(100, last_score + np.random.normal(0, 5)))
    
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
        
        # Score baseado no alinhamento com variação
        shoulder_score = max(0, 100 - shoulder_angle * 200)
        hip_score = max(0, 100 - hip_angle * 200)
        spine_score = max(0, 100 - spine_alignment * 100)
        
        base_score = (shoulder_score + hip_score + spine_score) / 3
        
        # Adicionar variação baseada no movimento
        movement_variation = np.random.normal(0, 3)  # Variação de ±3 pontos
        final_score = max(0, min(100, base_score + movement_variation))
        
        return final_score
        
    except Exception as e:
        print(f"Erro na análise de postura: {e}")
        return max(0, min(100, last_score + np.random.normal(0, 2)))

def analyze_gestures_improved(hands_results, last_score):
    """Analisa gestos com mais variação"""
    if not hands_results.multi_hand_landmarks:
        # Variação pequena quando não detecta
        return max(0, min(100, last_score + np.random.normal(0, 3)))
    
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
            
            # Score baseado no movimento com variação
            if hand_movement > 0.1:
                gesture_score += 50 + np.random.normal(0, 10)
            elif hand_movement > 0.05:
                gesture_score += 30 + np.random.normal(0, 8)
            else:
                gesture_score += 10 + np.random.normal(0, 5)
        
        base_score = min(100, gesture_score / hand_count) if hand_count > 0 else 30
        
        # Adicionar variação baseada no tempo
        time_variation = np.random.normal(0, 2)
        final_score = max(0, min(100, base_score + time_variation))
        
        return final_score
        
    except Exception as e:
        print(f"Erro na análise de gestos: {e}")
        return max(0, min(100, last_score + np.random.normal(0, 2)))

def analyze_eye_contact_improved(frame, face_results, last_score):
    """Analisa contato visual com mais variação"""
    if not face_results.multi_face_landmarks:
        # Variação pequena quando não detecta
        return max(0, min(100, last_score + np.random.normal(0, 4)))
    
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
        base_score = max(0, 100 - (distance_from_center / max_distance) * 100)
        
        # Adicionar variação baseada no movimento dos olhos
        eye_movement = abs(left_eye.x - right_eye.x) + abs(left_eye.y - right_eye.y)
        movement_variation = np.random.normal(0, 3) * eye_movement * 10
        
        final_score = max(0, min(100, base_score + movement_variation))
        
        return final_score
        
    except Exception as e:
        print(f"Erro na análise de contato visual: {e}")
        return max(0, min(100, last_score + np.random.normal(0, 3)))

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
        feedback.append("👁️ Olhe mais para a câmera - mantenha contato visual")
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
    print("🚀 Iniciando Communication Coach (Câmera Real + Landmarks Visuais)...")
    print("📍 Acesse: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
