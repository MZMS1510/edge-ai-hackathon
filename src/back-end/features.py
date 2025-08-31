import numpy as np
import cv2
import time
from collections import deque

class FeatureTracker:
    def __init__(self, window_size=30):
        self.window_size = window_size
        self.blink_history = deque(maxlen=window_size)
        self.hand_movement_history = deque(maxlen=window_size)
        self.head_movement_history = deque(maxlen=window_size)
        self.previous_landmarks = None
        self.last_blink_time = 0
        
        # Landmarks importantes
        self.LEFT_EYE_IDX = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_IDX = [33, 160, 158, 133, 153, 144]
        
    def calculate_eye_aspect_ratio(self, eye_landmarks):
        """Calcula Eye Aspect Ratio (EAR) para detecção de piscadas"""
        if len(eye_landmarks) < 6:
            return 0.3
            
        # Distâncias verticais
        v1 = np.linalg.norm(np.array(eye_landmarks[1]) - np.array(eye_landmarks[5]))
        v2 = np.linalg.norm(np.array(eye_landmarks[2]) - np.array(eye_landmarks[4]))
        
        # Distância horizontal
        h = np.linalg.norm(np.array(eye_landmarks[0]) - np.array(eye_landmarks[3]))
        
        # EAR
        ear = (v1 + v2) / (2.0 * h)
        return ear
    
    def detect_blink(self, face_landmarks, frame_time):
        """Detecta piscadas baseado no EAR"""
        if not face_landmarks or not face_landmarks.landmark:
            return False
        
        # Extrair coordenadas dos olhos
        h, w = frame_time.shape[:2] if hasattr(frame_time, 'shape') else (480, 640)
        
        left_eye_coords = []
        right_eye_coords = []
        
        for idx in self.LEFT_EYE_IDX:
            landmark = face_landmarks.landmark[idx]
            left_eye_coords.append([landmark.x * w, landmark.y * h])
            
        for idx in self.RIGHT_EYE_IDX:
            landmark = face_landmarks.landmark[idx]
            right_eye_coords.append([landmark.x * w, landmark.y * h])
        
        # Calcular EAR para ambos os olhos
        left_ear = self.calculate_eye_aspect_ratio(left_eye_coords)
        right_ear = self.calculate_eye_aspect_ratio(right_eye_coords)
        
        avg_ear = (left_ear + right_ear) / 2.0
        
        # Threshold para detectar piscada
        EAR_THRESHOLD = 0.25
        is_blink = avg_ear < EAR_THRESHOLD
        
        self.blink_history.append(avg_ear)
        
        return is_blink
    
    def calculate_hand_movement(self, hand_results):
        """Calcula movimento das mãos"""
        if not hand_results or not hand_results.multi_hand_landmarks:
            self.hand_movement_history.append(0.0)
            return 0.0
        
        total_movement = 0.0
        
        for hand_landmarks in hand_results.multi_hand_landmarks:
            # Calcular centro da mão
            hand_center = np.mean([[lm.x, lm.y] for lm in hand_landmarks.landmark], axis=0)
            
            if self.previous_landmarks is not None:
                # Calcular movimento desde o frame anterior
                prev_center = self.previous_landmarks.get('hand_center', hand_center)
                movement = np.linalg.norm(hand_center - prev_center)
                total_movement += movement
            
            # Armazenar para próximo frame
            if not hasattr(self, 'previous_landmarks') or self.previous_landmarks is None:
                self.previous_landmarks = {}
            self.previous_landmarks['hand_center'] = hand_center
        
        self.hand_movement_history.append(total_movement)
        return total_movement
    
    def calculate_head_movement(self, face_results):
        """Calcula movimento da cabeça"""
        if not face_results or not face_results.multi_face_landmarks:
            self.head_movement_history.append(0.0)
            return 0.0
        
        face_landmarks = face_results.multi_face_landmarks[0]
        
        # Usar ponto do nariz como referência (landmark 1)
        nose_tip = face_landmarks.landmark[1]
        head_pos = np.array([nose_tip.x, nose_tip.y])
        
        if self.previous_landmarks is not None and 'head_pos' in self.previous_landmarks:
            movement = np.linalg.norm(head_pos - self.previous_landmarks['head_pos'])
        else:
            movement = 0.0
        
        if self.previous_landmarks is None:
            self.previous_landmarks = {}
        self.previous_landmarks['head_pos'] = head_pos
        
        self.head_movement_history.append(movement)
        return movement
    
    def calculate_nervousness_score(self):
        """Calcula score de nervosismo baseado nas métricas"""
        if len(self.blink_history) < 5:
            return 0.0
        
        # Métricas
        blink_rate = sum(1 for ear in self.blink_history if ear < 0.25) / len(self.blink_history)
        avg_hand_movement = np.mean(self.hand_movement_history) if self.hand_movement_history else 0
        avg_head_movement = np.mean(self.head_movement_history) if self.head_movement_history else 0
        
        # Normalizar e calcular score
        blink_score = min(blink_rate * 2, 1.0)  # Normal ~15%, alto >30%
        hand_score = min(avg_hand_movement * 50, 1.0)  # Movimento normalizado
        head_score = min(avg_head_movement * 100, 1.0)  # Movimento normalizado
        
        # Score combinado (0-1)
        nervousness_score = (blink_score * 0.4 + hand_score * 0.4 + head_score * 0.2)
        
        return min(nervousness_score, 1.0)

# Instância global do tracker
feature_tracker = FeatureTracker()

def extract_features(face_results, hand_results, frame):
    """Extrai features principais do frame"""
    current_time = time.time()
    
    # Detectar piscadas
    is_blink = False
    if face_results and face_results.multi_face_landmarks:
        is_blink = feature_tracker.detect_blink(
            face_results.multi_face_landmarks[0], 
            frame
        )
    
    # Calcular movimentos
    hand_movement = feature_tracker.calculate_hand_movement(hand_results)
    head_movement = feature_tracker.calculate_head_movement(face_results)
    
    # Score de nervosismo
    nervousness_score = feature_tracker.calculate_nervousness_score()
    
    # Contadores
    hands_detected = len(hand_results.multi_hand_landmarks) if hand_results and hand_results.multi_hand_landmarks else 0
    face_detected = len(face_results.multi_face_landmarks) if face_results and face_results.multi_face_landmarks else 0
    
    # Estatísticas das janelas
    blink_stats = {
        'avg_ear': np.mean(feature_tracker.blink_history) if feature_tracker.blink_history else 0.3,
        'blink_rate': sum(1 for ear in feature_tracker.blink_history if ear < 0.25) / len(feature_tracker.blink_history) if feature_tracker.blink_history else 0
    }
    
    features = {
        'timestamp': current_time,
        'nervousness_score': nervousness_score,
        'blink_detected': is_blink,
        'blink_stats': blink_stats,
        'hand_movement': hand_movement,
        'head_movement': head_movement,
        'hands_detected': hands_detected,
        'face_detected': face_detected,
        'raw_metrics': {
            'avg_hand_movement': np.mean(feature_tracker.hand_movement_history) if feature_tracker.hand_movement_history else 0,
            'avg_head_movement': np.mean(feature_tracker.head_movement_history) if feature_tracker.head_movement_history else 0,
            'hand_movement_std': np.std(feature_tracker.hand_movement_history) if len(feature_tracker.hand_movement_history) > 1 else 0,
            'head_movement_std': np.std(feature_tracker.head_movement_history) if len(feature_tracker.head_movement_history) > 1 else 0
        }
    }
    
    return features

def get_summary_stats():
    """Retorna estatísticas resumidas da sessão"""
    if not feature_tracker.blink_history:
        return {}
    
    return {
        'total_frames': len(feature_tracker.blink_history),
        'avg_nervousness': feature_tracker.calculate_nervousness_score(),
        'blink_rate': sum(1 for ear in feature_tracker.blink_history if ear < 0.25) / len(feature_tracker.blink_history),
        'avg_hand_movement': np.mean(feature_tracker.hand_movement_history) if feature_tracker.hand_movement_history else 0,
        'avg_head_movement': np.mean(feature_tracker.head_movement_history) if feature_tracker.head_movement_history else 0
    }