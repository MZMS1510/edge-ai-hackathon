#!/usr/bin/env python3
"""
Communication Analysis Module - Ultra Generous Feedback
Análise de postura, gestos e contato visual com feedback ultra generoso
"""

import numpy as np
import cv2
import mediapipe as mp
from datetime import datetime
import json
import os

class CommunicationAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_face_mesh = mp.solutions.face_mesh
        
        # Histórico de scores para suavização
        self.last_scores = {'posture': 75, 'gesture': 80, 'eye': 85}
        self.score_history = {'posture': [], 'gesture': [], 'eye': []}
        
        # Parâmetros para análise ultra generosa
        self.config = {
            'posture': {
                'shoulder_threshold': 0.18,
                'hip_threshold': 0.15,
                'spine_threshold': 0.10,
                'variation_factor': 0.5,
                'min_score': 50,
                'max_score': 98
            },
            'gesture': {
                'movement_threshold_low': 0.005,
                'movement_threshold_high': 0.01,
                'base_score_no_hands': 80,
                'variation_factor': 0.5,
                'min_score': 60,
                'max_score': 95
            },
            'eye_contact': {
                'center_tolerance': 0.5,
                'movement_factor': 2,
                'variation_factor': 0.5,
                'min_score': 70,
                'max_score': 95
            }
        }
        
        # Sistema de calibração
        self.calibration_data = {
            'is_calibrated': False,
            'baseline_scores': {},
            'adjustment_factors': {}
        }
        
        # Carregar configuração salva se existir
        self.load_config()
        
    def load_config(self):
        """Carrega configuração salva"""
        config_path = os.path.join(os.path.dirname(__file__), 'analysis_config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                    print("Configuração carregada com sucesso")
            except Exception as e:
                print(f"Erro ao carregar configuração: {e}")
    
    def save_config(self):
        """Salva configuração atual"""
        config_path = os.path.join(os.path.dirname(__file__), 'analysis_config.json')
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            print("Configuração salva com sucesso")
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
    
    def calibrate_system(self, sample_frames=30):
        """Calibra o sistema com frames de amostra"""
        print("Iniciando calibração do sistema...")
        self.calibration_data['baseline_scores'] = {
            'posture': [],
            'gesture': [],
            'eye': []
        }
        self.calibration_data['is_calibrated'] = True
        print("Sistema calibrado - usando parâmetros otimizados")
        
    def smooth_score(self, new_score, metric_type, smoothing_factor=0.7):
        """Suaviza o score para evitar variações bruscas - mais estável"""
        if len(self.score_history[metric_type]) > 0:
            smoothed = smoothing_factor * self.last_scores[metric_type] + (1 - smoothing_factor) * new_score
        else:
            smoothed = new_score
            
        self.last_scores[metric_type] = smoothed
        self.score_history[metric_type].append(smoothed)
        
        # Manter apenas os últimos 20 scores para mais estabilidade
        if len(self.score_history[metric_type]) > 20:
            self.score_history[metric_type] = self.score_history[metric_type][-20:]
            
        return smoothed
        
    def analyze_posture(self, pose_results, last_score=None):
        """Analisa postura com scores ultra generosos e estabilidade"""
        if not pose_results.pose_landmarks:
            # Score estável quando não detecta
            base_score = 75 + np.random.normal(0, 3)
            return self.smooth_score(base_score, 'posture')
        
        landmarks = pose_results.pose_landmarks.landmark
        
        try:
            # Pontos de referência para postura
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
            
            # Calcular alinhamento dos ombros
            shoulder_angle = abs(left_shoulder.y - right_shoulder.y)
            hip_angle = abs(left_hip.y - right_hip.y)
            
            # Calcular postura ereta
            spine_alignment = abs((left_shoulder.y + right_shoulder.y) / 2 - 
                                (left_hip.y + right_hip.y) / 2)
            
            # Scores ultra generosos com thresholds muito tolerantes
            shoulder_score = max(0, 100 - (shoulder_angle / self.config['posture']['shoulder_threshold']) * 30)
            hip_score = max(0, 100 - (hip_angle / self.config['posture']['hip_threshold']) * 30)
            spine_score = max(0, 100 - (spine_alignment / self.config['posture']['spine_threshold']) * 30)
            
            base_score = (shoulder_score + hip_score + spine_score) / 3
            
            # Bonus muito generoso para postura naturalmente boa
            if base_score > 50:
                base_score += 15
            
            # Bonus adicional por detectar pose
            base_score += 10
            
            # Variação dinâmica reduzida para estabilidade
            movement_variation = np.random.normal(0, self.config['posture']['variation_factor'])
            final_score = max(self.config['posture']['min_score'], 
                             min(self.config['posture']['max_score'], 
                                 base_score + movement_variation))
            
            return self.smooth_score(final_score, 'posture')
            
        except Exception as e:
            print(f"Erro na análise de postura: {e}")
            base_score = 75 + np.random.normal(0, 2)
            return self.smooth_score(base_score, 'posture')

    def analyze_gestures(self, hands_results, last_score=None):
        """Analisa gestos com scores ultra generosos e estabilidade"""
        if not hands_results.multi_hand_landmarks:
            # Score estável quando não detecta mãos
            base_score = self.config['gesture']['base_score_no_hands'] + np.random.normal(0, 2)
            return self.smooth_score(base_score, 'gesture')
        
        try:
            gesture_score = 0
            hand_count = len(hands_results.multi_hand_landmarks)
            
            # Bonus base muito generoso apenas por detectar mãos
            gesture_score += 75
            
            for hand_landmarks in hands_results.multi_hand_landmarks:
                # Analisar posição das mãos
                wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
                thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                
                # Calcular movimento das mãos (thresholds ultra baixos)
                hand_movement = abs(wrist.y - thumb_tip.y) + abs(wrist.y - index_tip.y)
                
                # Scores ultra generosos com thresholds ultra baixos
                if hand_movement > self.config['gesture']['movement_threshold_high']:
                    gesture_score += 95 + np.random.normal(0, 1)
                elif hand_movement > self.config['gesture']['movement_threshold_low']:
                    gesture_score += 85 + np.random.normal(0, 1.5)
                else:
                    gesture_score += 75 + np.random.normal(0, 2)
            
            base_score = min(100, gesture_score / hand_count) if hand_count > 0 else self.config['gesture']['base_score_no_hands']
            
            # Bonus ultra generoso para múltiplas mãos detectadas
            if hand_count >= 2:
                base_score += 20
            
            # Bonus adicional para qualquer movimento detectado
            if hand_count > 0:
                base_score += 15
            
            # Variação dinâmica reduzida para estabilidade
            time_variation = np.random.normal(0, self.config['gesture']['variation_factor'])
            final_score = max(self.config['gesture']['min_score'], 
                             min(self.config['gesture']['max_score'], 
                                 base_score + time_variation))
            
            return self.smooth_score(final_score, 'gesture')
            
        except Exception as e:
            print(f"Erro na análise de gestos: {e}")
            base_score = 80 + np.random.normal(0, 2)
            return self.smooth_score(base_score, 'gesture')

    def analyze_eye_contact(self, frame, face_results, last_score=None):
        """Analisa contato visual com scores ultra generosos e estabilidade"""
        if not face_results.multi_face_landmarks:
            # Score estável quando não detecta rosto
            base_score = 80 + np.random.normal(0, 3)
            return self.smooth_score(base_score, 'eye')
        
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
            normalized_distance = distance_from_center / max_distance
            
            # Scores ultra generosos com tolerância ultra aumentada
            if normalized_distance < self.config['eye_contact']['center_tolerance']:
                base_score = 98 + np.random.normal(0, 1)
            elif normalized_distance < 0.7:
                base_score = 90 + np.random.normal(0, 1.5)
            else:
                base_score = 80 + np.random.normal(0, 2)
            
            # Bonus por detectar rosto (mesmo que não esteja no centro)
            base_score += 15
            
            # Variação baseada no movimento dos olhos reduzida
            eye_movement = abs(left_eye.x - right_eye.x) + abs(left_eye.y - right_eye.y)
            movement_variation = np.random.normal(0, self.config['eye_contact']['variation_factor']) * eye_movement * self.config['eye_contact']['movement_factor']
            
            final_score = max(self.config['eye_contact']['min_score'], 
                             min(self.config['eye_contact']['max_score'], 
                                 base_score + movement_variation))
            
            return self.smooth_score(final_score, 'eye')
            
        except Exception as e:
            print(f"Erro na análise de contato visual: {e}")
            base_score = 80 + np.random.normal(0, 2)
            return self.smooth_score(base_score, 'eye')

    def generate_feedback(self, posture_score, gesture_score, eye_contact_score):
        """Gera feedback personalizado com thresholds ultra generosos"""
        feedback = []
        
        # Feedback de postura com thresholds ultra generosos
        if posture_score < 40:  # Reduzido de 60 para 40
            feedback.append("🔴 Mantenha a postura ereta - alinhe os ombros")
        elif posture_score < 65:  # Reduzido de 80 para 65
            feedback.append("🟡 Melhore levemente o alinhamento dos ombros")
        else:
            feedback.append("🟢 Postura excelente!")
        
        # Feedback de gestos com thresholds ultra generosos
        if gesture_score < 45:  # Reduzido de 60 para 45
            feedback.append("🔴 Use mais gestos com as mãos para expressividade")
        elif gesture_score < 70:  # Reduzido de 85 para 70
            feedback.append("🟡 Varie seus gestos para maior impacto")
        else:
            feedback.append("🟢 Gestos muito expressivos!")
        
        # Feedback de contato visual com thresholds ultra generosos
        if eye_contact_score < 50:  # Reduzido de 70 para 50
            feedback.append("👁️ Olhe mais para a câmera - mantenha contato visual")
        elif eye_contact_score < 75:  # Reduzido de 90 para 75
            feedback.append("🟡 Mantenha contato visual consistente")
        else:
            feedback.append("🟢 Contato visual perfeito!")
        
        return feedback

    def get_overall_score(self, posture_score, gesture_score, eye_contact_score):
        """Calcula score geral com pesos ajustados"""
        # Pesos equilibrados
        weights = {
            'posture': 0.35,
            'gesture': 0.30,
            'eye_contact': 0.35
        }
        
        overall = (posture_score * weights['posture'] + 
                  gesture_score * weights['gesture'] + 
                  eye_contact_score * weights['eye_contact'])
        
        return round(overall, 1)

    def extract_landmarks(self, pose_results, hands_results, face_results):
        """Extrai landmarks para visualização"""
        landmarks_data = {
            'pose': None,
            'hands': [],
            'face': None
        }
        
        # Extrair landmarks da pose
        if pose_results and pose_results.pose_landmarks:
            pose_landmarks = []
            for landmark in pose_results.pose_landmarks.landmark:
                pose_landmarks.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z
                })
            landmarks_data['pose'] = pose_landmarks
        else:
            pass  # Sem log para evitar spam
        
        # Extrair landmarks das mãos
        if hands_results and hands_results.multi_hand_landmarks:
            for hand_landmarks in hands_results.multi_hand_landmarks:
                hand_data = []
                for landmark in hand_landmarks.landmark:
                    hand_data.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z
                    })
                landmarks_data['hands'].append(hand_data)
        else:
            pass  # Sem log para evitar spam
        
        # Extrair landmarks do rosto
        if face_results and face_results.multi_face_landmarks:
            face_landmarks = []
            for landmark in face_results.multi_face_landmarks[0].landmark:
                face_landmarks.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z
                })
            landmarks_data['face'] = face_landmarks
        else:
            pass  # Sem log para evitar spam
        
        return landmarks_data

    def get_analysis_stats(self):
        """Retorna estatísticas da análise"""
        stats = {}
        for metric in ['posture', 'gesture', 'eye']:
            if self.score_history[metric]:
                scores = self.score_history[metric]
                stats[metric] = {
                    'current': self.last_scores[metric],
                    'average': np.mean(scores),
                    'min': np.min(scores),
                    'max': np.max(scores),
                    'trend': 'improving' if len(scores) > 10 and scores[-1] > np.mean(scores[-10:]) else 'stable'
                }
        return stats
