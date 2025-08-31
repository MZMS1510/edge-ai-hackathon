#!/usr/bin/env python3
"""
Communication Coach - Main Application
Sistema de análise de comunicação em tempo real
"""

import os
import sys
import time
import threading
import numpy as np
import json
import cv2
import mediapipe as mp
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos core
from core.analysis import CommunicationAnalyzer
from core.camera import CameraManager
from core.report_manager import ReportManager
from utils.qualcomm_utils import QualcommUtils

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'communication-coach-edge-ai'
socketio = SocketIO(app, cors_allowed_origins="*")

# Instâncias globais
coach_thread = None
is_coaching = False
camera_working = False

# Função para resetar estado global
def reset_global_state():
    """Reseta o estado global do sistema"""
    global is_coaching, camera_working, coach_thread
    is_coaching = False
    camera_working = False
    coach_thread = None
    print("🔄 Estado global resetado na inicialização")

# Resetar estado na inicialização
reset_global_state()

# Inicializar módulos
analyzer = CommunicationAnalyzer()
camera_manager = CameraManager()
report_manager = ReportManager()
qualcomm_utils = QualcommUtils()

# Métricas de comunicação
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

# Rotas da API
@app.route('/')
def index():
    """Página principal"""
    return render_template('communication_coach.html')

@app.route('/pitch-practice')
def pitch_practice_page():
    """Página do Pitch Practice"""
    return render_template('communication_coach.html')

@app.route('/final-report')
def final_report():
    """Página do relatório final"""
    return render_template('final_report.html')

@app.route('/status')
def status():
    """Status do sistema"""
    system_info = qualcomm_utils.get_system_info()
    
    return jsonify({
        'snapdragon_detected': qualcomm_utils.snapdragon_detected,
        'system_info': system_info,
        'is_coaching': is_coaching,
        'camera_working': camera_working,
        'camera_config': camera_manager.get_camera_info(),
        'tools_available': qualcomm_utils.check_qualcomm_tools(),
        'analyzer_stats': analyzer.get_analysis_stats()
    })

@app.route('/reset')
def reset_state():
    """Reseta o estado do sistema"""
    global is_coaching, camera_working, coach_thread, analysis_history
    
    try:
        print("🔄 Resetando estado do sistema...")
        
        # Parar análise se estiver ativa
        if is_coaching:
            is_coaching = False
            camera_working = False
            if coach_thread and coach_thread.is_alive():
                # Aguardar thread terminar
                try:
                    coach_thread.join(timeout=2)
                    print("✅ Thread de coaching finalizada")
                except:
                    print("⚠️ Timeout ao aguardar thread")
        
        # Garantir que todas as variáveis estão resetadas
        is_coaching = False
        camera_working = False
        coach_thread = None
        
        # Resetar histórico
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
        
        # Resetar métricas
        communication_metrics.update({
            'posture_score': 0,
            'gesture_score': 0,
            'eye_contact_score': 0,
            'overall_score': 0,
            'feedback': []
        })
        
        print("✅ Estado do sistema resetado completamente")
        return jsonify({
            'success': True,
            'message': 'Estado do sistema resetado com sucesso',
            'is_coaching': is_coaching,
            'camera_working': camera_working
        })
        
    except Exception as e:
        print(f"❌ Erro ao resetar estado: {e}")
        # Forçar reset mesmo em caso de erro
        is_coaching = False
        camera_working = False
        coach_thread = None
        return jsonify({'error': str(e)})

@app.route('/calibrate')
def calibrate_system():
    """Calibra o sistema de análise"""
    try:
        analyzer.calibrate_system()
        return jsonify({
            'success': True,
            'message': 'Sistema calibrado com sucesso',
            'config': analyzer.config
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/config', methods=['GET', 'POST'])
def manage_config():
    """Gerencia configuração do sistema"""
    if request.method == 'POST':
        try:
            new_config = request.json
            analyzer.config.update(new_config)
            analyzer.save_config()
            return jsonify({
                'success': True,
                'message': 'Configuração atualizada',
                'config': analyzer.config
            })
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return jsonify({
            'config': analyzer.config,
            'stats': analyzer.get_analysis_stats()
        })

@app.route('/start_coaching')
def start_coaching():
    """Inicia análise de comunicação"""
    global coach_thread, is_coaching, camera_working, analysis_history
    
    # Verificar se já está ativo
    if is_coaching:
        print("⚠️ Tentativa de iniciar análise já ativa")
        return jsonify({'error': 'Análise já está ativa'})
    
    # Verificar se há thread ativa
    if coach_thread and coach_thread.is_alive():
        print("⚠️ Thread de coaching ainda ativa, aguardando...")
        try:
            coach_thread.join(timeout=1)
        except:
            pass
    
    try:
        print("🚀 Iniciando análise de comunicação...")
        
        # Garantir que o estado está limpo
        is_coaching = False
        camera_working = False
        coach_thread = None
        
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
        camera_index = camera_manager.find_working_camera()
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
        # Garantir que o estado seja resetado em caso de erro
        is_coaching = False
        camera_working = False
        coach_thread = None
        return jsonify({'error': f'Erro ao iniciar análise: {str(e)}'})

@app.route('/stop_coaching')
def stop_coaching():
    """Para análise de comunicação e gera relatório final"""
    global is_coaching, camera_working, coach_thread, analysis_history
    
    if not is_coaching:
        return jsonify({'error': 'Análise não está ativa'})
    
    try:
        print("🛑 Parando análise de comunicação...")
        
        # Finalizar análise
        analysis_history['end_time'] = datetime.now().isoformat()
        start_time = datetime.fromisoformat(analysis_history['start_time'])
        end_time = datetime.fromisoformat(analysis_history['end_time'])
        analysis_history['duration'] = (end_time - start_time).total_seconds()
        
        # Resetar estado global
        is_coaching = False
        camera_working = False
        
        # Aguardar thread terminar se estiver ativa
        if coach_thread and coach_thread.is_alive():
            try:
                coach_thread.join(timeout=2)
                print("✅ Thread de coaching finalizada")
            except:
                print("⚠️ Timeout ao aguardar thread")
        
        coach_thread = None
        
        # Gerar relatório final
        print("📊 Gerando relatório final...")
        final_report = generate_final_report()
        
        # Salvar relatório
        if report_manager:
            report_manager.add_report(final_report)
        
        print("✅ Análise finalizada com sucesso")
        return jsonify({
            'success': True, 
            'message': 'Análise finalizada',
            'report': final_report
        })
        
    except Exception as e:
        print(f"❌ Erro ao parar análise: {e}")
        # Garantir que o estado seja resetado mesmo em caso de erro
        is_coaching = False
        camera_working = False
        coach_thread = None
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

# Rotas da API para histórico
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

@app.route('/test_mediapipe')
def test_mediapipe():
    """Testa se o MediaPipe está funcionando"""
    try:
        import cv2
        import mediapipe as mp
        
        # Tentar inicializar a câmera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return jsonify({'error': 'Câmera não disponível'})
        
        # Ler um frame
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return jsonify({'error': 'Não foi possível ler frame da câmera'})
        
        # Inicializar MediaPipe
        mp_pose = mp.solutions.pose
        with mp_pose.Pose(
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3
        ) as pose:
            # Processar frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)
            
            # Verificar se detectou algo
            if results.pose_landmarks:
                landmarks_count = len(results.pose_landmarks.landmark)
                return jsonify({
                    'success': True,
                    'message': f'MediaPipe funcionando! Detectou {landmarks_count} landmarks de pose',
                    'landmarks_count': landmarks_count
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'MediaPipe não detectou landmarks. Verifique se há uma pessoa na frente da câmera.',
                    'landmarks_count': 0
                })
        
        cap.release()
        
    except Exception as e:
        return jsonify({'error': f'Erro ao testar MediaPipe: {str(e)}'})

def coaching_loop(camera_index):
    """Loop principal de análise de comunicação"""
    global communication_metrics, is_coaching, camera_working, analysis_history
    
    try:
        print("🎥 Usando câmera real...")
        real_camera_loop(camera_index)
            
    except Exception as e:
        print(f"❌ Erro no loop de coaching: {e}")
        print("❌ Análise interrompida - câmera não disponível")

def real_camera_loop(camera_index):
    """Loop com câmera real"""
    global communication_metrics, is_coaching, analysis_history
    
    try:
        # Inicializar câmera
        cap = camera_manager.initialize_camera(camera_index)
        if not cap:
            raise Exception("Não foi possível inicializar a câmera")
        
        # Inicializar MediaPipe
        mp_pose = mp.solutions.pose
        mp_hands = mp.solutions.hands
        mp_face_mesh = mp.solutions.face_mesh
        
        with mp_pose.Pose(
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3,
            model_complexity=1,
            smooth_landmarks=True
        ) as pose, mp_hands.Hands(
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3,
            max_num_hands=2,
            model_complexity=1
        ) as hands, mp_face_mesh.FaceMesh(
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3,
            max_num_faces=1
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
                    analysis_history['total_frames'] = frame_count
                    
                    # Processar frame
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Análise real
                    pose_results = pose.process(rgb_frame)
                    posture_score = analyzer.analyze_posture(pose_results)
                    
                    hands_results = hands.process(rgb_frame)
                    gesture_score = analyzer.analyze_gestures(hands_results)
                    
                    face_results = face_mesh.process(rgb_frame)
                    eye_contact_score = analyzer.analyze_eye_contact(frame, face_results)
                    
                    # Debug MediaPipe a cada 30 frames
                    if frame_count % 30 == 0:
                        print(f"🎯 MediaPipe Debug: Pose={bool(pose_results.pose_landmarks)}, Mãos={len(hands_results.multi_hand_landmarks) if hands_results.multi_hand_landmarks else 0}, Rosto={len(face_results.multi_face_landmarks) if face_results.multi_face_landmarks else 0}")
                    
                    # Calcular score geral com pesos otimizados
                    overall_score = analyzer.get_overall_score(posture_score, gesture_score, eye_contact_score)
                    
                    # Salvar no histórico
                    analysis_history['scores_history'].append([
                        posture_score, gesture_score, eye_contact_score, overall_score
                    ])
                    
                    # Gerar feedback
                    feedback = analyzer.generate_feedback(posture_score, gesture_score, eye_contact_score)
                    
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
                    
                    # Enviar landmarks para visualização
                    landmarks_data = analyzer.extract_landmarks(pose_results, hands_results, face_results)
                    
                    # Debug landmarks a cada 30 frames
                    if frame_count % 30 == 0:
                        print(f"🎯 Landmarks extraídos: Pose={bool(landmarks_data['pose'])}, Mãos={len(landmarks_data['hands'])}, Rosto={bool(landmarks_data['face'])}")
                    
                    socketio.emit('landmarks_data', landmarks_data)
                    
                    # Debug a cada 10 frames
                    if frame_count % 10 == 0:
                        print(f"📊 Frame {frame_count}: Postura={posture_score:.1f}, Gestos={gesture_score:.1f}, Olhos={eye_contact_score:.1f}")
                    
                    time.sleep(0.05)  # 50ms para 20 FPS
                    
                except Exception as e:
                    print(f"❌ Erro no processamento: {e}")
                    time.sleep(0.1)
                    
    except Exception as e:
        print(f"❌ Erro na câmera real: {e}")
        raise e
    finally:
        try:
            cap.release()
            print("🔒 Câmera liberada")
        except:
            pass

def generate_final_report():
    """Gera relatório final da análise"""
    global analysis_history
    
    if not analysis_history['scores_history']:
        return {
            'error': 'Nenhum dado coletado para análise'
        }
    
    # Calcular estatísticas
    scores = np.array(analysis_history['scores_history'])
    avg_posture = float(np.mean(scores[:, 0]))
    avg_gesture = float(np.mean(scores[:, 1]))
    avg_eye_contact = float(np.mean(scores[:, 2]))
    avg_overall = float(np.mean(scores[:, 3]))
    
    # Calcular melhorias
    if len(scores) > 10:
        first_half = np.mean(scores[:len(scores)//2], axis=0)
        second_half = np.mean(scores[len(scores)//2:], axis=0)
        improvements = second_half - first_half
        # Converter para tipos Python nativos
        improvements = [float(x) for x in improvements]
    else:
        improvements = [0.0, 0.0, 0.0, 0.0]
    
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
    print("🚀 Iniciando Communication Coach...")
    print("📍 Acesse: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
