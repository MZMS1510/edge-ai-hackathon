import os
import tempfile
import cv2
import numpy as np
import mediapipe as mp
from collections import deque

class VisualAnalyzer:
    """Classe para análise visual de apresentações usando modelos de IA da Qualcomm"""
    
    def __init__(self, model_manager=None):
        """Inicializa o analisador visual com modelos pré-treinados
        
        Args:
            model_manager: Instância do ModelManager para carregar modelos
        """
        # Inicializar MediaPipe para detecção facial e pose
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Carregar modelos do ModelManager se fornecido
        if model_manager:
            self.face_mesh = model_manager.get_model('face_mesh')
            self.pose = model_manager.get_model('pose')
        else:
            # Importar aqui para evitar dependência circular
            from ..models.mediapipe_model import load_mediapipe_models
            self.face_mesh, self.pose = load_mediapipe_models(use_qualcomm=True)
        
        # Pontos de referência para olhos
        # Índices baseados no modelo MediaPipe Face Mesh
        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        
        # Histórico de movimentos para análise de gestos
        self.movement_history = deque(maxlen=30)  # ~1 segundo a 30 fps
    
    def analyze(self, video_file):
        """Analisa um arquivo de vídeo para extrair insights sobre linguagem corporal
        
        Args:
            video_file: Arquivo de vídeo da apresentação
            
        Returns:
            dict: Resultados da análise contendo métricas visuais
        """
        # Salvar o arquivo temporariamente
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            video_file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Abrir o vídeo
            cap = cv2.VideoCapture(temp_path)
            if not cap.isOpened():
                raise ValueError("Não foi possível abrir o arquivo de vídeo")
            
            # Inicializar contadores e acumuladores
            frame_count = 0
            face_detected_frames = 0
            eye_contact_frames = 0
            smile_frames = 0
            pose_metrics = {
                "good_posture_frames": 0,
                "hand_gesture_frames": 0,
                "movement_frames": 0
            }
            
            # Processar cada frame
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break
                
                frame_count += 1
                
                # Processar apenas 1 frame a cada 5 para eficiência
                if frame_count % 5 != 0:
                    continue
                
                # Converter para RGB (MediaPipe requer RGB)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Analisar face
                face_results = self.face_mesh.process(frame_rgb)
                
                # Analisar pose
                pose_results = self.pose.process(frame_rgb)
                
                # Processar resultados faciais
                if face_results.multi_face_landmarks:
                    face_detected_frames += 1
                    face_landmarks = face_results.multi_face_landmarks[0]
                    
                    # Verificar contato visual
                    if self._check_eye_contact(face_landmarks):
                        eye_contact_frames += 1
                    
                    # Detectar sorriso
                    if self._detect_smile(face_landmarks):
                        smile_frames += 1
                
                # Processar resultados de pose
                if pose_results.pose_landmarks:
                    # Verificar postura
                    if self._check_good_posture(pose_results.pose_landmarks):
                        pose_metrics["good_posture_frames"] += 1
                    
                    # Detectar gestos com as mãos
                    if self._detect_hand_gestures(pose_results.pose_landmarks):
                        pose_metrics["hand_gesture_frames"] += 1
                    
                    # Analisar movimento
                    if self._analyze_movement(pose_results.pose_landmarks):
                        pose_metrics["movement_frames"] += 1
            
            # Liberar recursos
            cap.release()
            
            # Calcular métricas finais
            processed_frames = frame_count // 5
            results = {}
            
            # Métricas faciais
            if face_detected_frames > 0:
                face_detection_ratio = face_detected_frames / processed_frames
                results["face_visibility"] = float(face_detection_ratio)
                results["eye_contact"] = float(eye_contact_frames / max(1, face_detected_frames))
                results["smile_ratio"] = float(smile_frames / max(1, face_detected_frames))
            else:
                results["face_visibility"] = 0.0
                results["eye_contact"] = 0.0
                results["smile_ratio"] = 0.0
            
            # Métricas de postura e movimento
            results["posture"] = float(pose_metrics["good_posture_frames"] / max(1, processed_frames))
            results["gestures"] = float(pose_metrics["hand_gesture_frames"] / max(1, processed_frames))
            results["movement"] = float(pose_metrics["movement_frames"] / max(1, processed_frames))
            
            # Calcular pontuação de presença visual
            visual_presence_score = (
                results["face_visibility"] * 0.2 +
                results["eye_contact"] * 0.3 +
                results["posture"] * 0.2 +
                results["gestures"] * 0.15 +
                results["movement"] * 0.1 +
                results["smile_ratio"] * 0.05
            )
            
            results["visual_presence_score"] = float(visual_presence_score)
            
            return results
            
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def _check_eye_contact(self, face_landmarks):
        """Verifica se a pessoa está olhando para a câmera (contato visual)"""
        # Extrair pontos dos olhos
        left_eye_points = [face_landmarks.landmark[i] for i in self.LEFT_EYE_INDICES]
        right_eye_points = [face_landmarks.landmark[i] for i in self.RIGHT_EYE_INDICES]
        
        # Calcular centro dos olhos
        left_eye_center = np.mean([[p.x, p.y, p.z] for p in left_eye_points], axis=0)
        right_eye_center = np.mean([[p.x, p.y, p.z] for p in right_eye_points], axis=0)
        
        # Calcular direção do olhar baseado na posição relativa dos olhos
        # Simplificação: se os olhos estão relativamente centralizados e frontais, assume-se contato visual
        eye_direction = np.array([left_eye_center, right_eye_center])
        eye_depth_diff = abs(left_eye_center[2] - right_eye_center[2])
        
        # Verificar se os olhos estão aproximadamente no mesmo plano Z (olhando para frente)
        # e se a posição Y está dentro de um intervalo razoável (não olhando muito para cima/baixo)
        is_looking_forward = eye_depth_diff < 0.01
        is_looking_center = (left_eye_center[1] > 0.3 and left_eye_center[1] < 0.7 and
                            right_eye_center[1] > 0.3 and right_eye_center[1] < 0.7)
        
        return is_looking_forward and is_looking_center
    
    def _detect_smile(self, face_landmarks):
        """Detecta se a pessoa está sorrindo"""
        # Pontos da boca no MediaPipe Face Mesh
        mouth_top = face_landmarks.landmark[13]  # Lábio superior
        mouth_bottom = face_landmarks.landmark[14]  # Lábio inferior
        mouth_left = face_landmarks.landmark[78]  # Canto esquerdo
        mouth_right = face_landmarks.landmark[308]  # Canto direito
        
        # Calcular altura e largura da boca
        mouth_height = abs(mouth_top.y - mouth_bottom.y)
        mouth_width = abs(mouth_left.x - mouth_right.x)
        
        # Calcular proporção largura/altura
        # Um sorriso geralmente tem uma proporção maior (boca mais larga que alta)
        mouth_ratio = mouth_width / max(0.001, mouth_height)
        
        # Verificar cantos da boca (elevados em um sorriso)
        left_corner = face_landmarks.landmark[61]  # Canto esquerdo elevado
        right_corner = face_landmarks.landmark[291]  # Canto direito elevado
        
        # Verificar se os cantos estão acima da linha central da boca
        mouth_center_y = (mouth_top.y + mouth_bottom.y) / 2
        corners_elevated = (left_corner.y < mouth_center_y and right_corner.y < mouth_center_y)
        
        # Combinar critérios para detectar sorriso
        return mouth_ratio > 4.0 and corners_elevated
    
    def _check_good_posture(self, pose_landmarks):
        """Verifica se a pessoa está com boa postura"""
        # Pontos de referência para postura
        shoulders_left = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        shoulders_right = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        hip_left = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
        hip_right = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP]
        nose = pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
        
        # Verificar se os ombros estão nivelados
        shoulders_level = abs(shoulders_left.y - shoulders_right.y) < 0.05
        
        # Verificar se o corpo está ereto (linha vertical entre nariz e quadril)
        nose_x = (shoulders_left.x + shoulders_right.x) / 2
        hip_x = (hip_left.x + hip_right.x) / 2
        body_vertical = abs(nose_x - hip_x) < 0.1
        
        return shoulders_level and body_vertical
    
    def _detect_hand_gestures(self, pose_landmarks):
        """Detecta se a pessoa está usando gestos com as mãos"""
        # Pontos de referência para mãos e cotovelos
        wrist_left = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
        wrist_right = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
        elbow_left = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ELBOW]
        elbow_right = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ELBOW]
        shoulder_left = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        shoulder_right = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        # Verificar se as mãos estão visíveis
        hands_visible = (wrist_left.visibility > 0.7 or wrist_right.visibility > 0.7)
        
        # Verificar se os braços estão dobrados (gestos ativos)
        left_arm_bent = False
        if wrist_left.visibility > 0.7 and elbow_left.visibility > 0.7 and shoulder_left.visibility > 0.7:
            # Calcular ângulo do cotovelo esquerdo
            angle = self._calculate_angle(
                [shoulder_left.x, shoulder_left.y],
                [elbow_left.x, elbow_left.y],
                [wrist_left.x, wrist_left.y]
            )
            left_arm_bent = angle < 160  # Braço dobrado se ângulo < 160 graus
        
        right_arm_bent = False
        if wrist_right.visibility > 0.7 and elbow_right.visibility > 0.7 and shoulder_right.visibility > 0.7:
            # Calcular ângulo do cotovelo direito
            angle = self._calculate_angle(
                [shoulder_right.x, shoulder_right.y],
                [elbow_right.x, elbow_right.y],
                [wrist_right.x, wrist_right.y]
            )
            right_arm_bent = angle < 160  # Braço dobrado se ângulo < 160 graus
        
        # Considerar gesto se as mãos estão visíveis e pelo menos um braço está dobrado
        return hands_visible and (left_arm_bent or right_arm_bent)
    
    def _analyze_movement(self, pose_landmarks):
        """Analisa o movimento do apresentador"""
        # Usar o ponto central entre os ombros como referência de posição
        shoulder_left = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        shoulder_right = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        current_position = [
            (shoulder_left.x + shoulder_right.x) / 2,
            (shoulder_left.y + shoulder_right.y) / 2
        ]
        
        # Adicionar posição atual ao histórico
        self.movement_history.append(current_position)
        
        # Verificar se há movimento significativo
        if len(self.movement_history) < 2:
            return False
        
        # Calcular deslocamento em relação à posição anterior
        prev_position = self.movement_history[-2]
        displacement = np.sqrt(
            (current_position[0] - prev_position[0])**2 +
            (current_position[1] - prev_position[1])**2
        )
        
        # Considerar movimento se o deslocamento for significativo
        # mas não excessivo (o que poderia indicar movimento brusco)
        return 0.005 < displacement < 0.05
    
    def _calculate_angle(self, a, b, c):
        """Calcula o ângulo entre três pontos"""
        a = np.array(a)  # Primeiro ponto
        b = np.array(b)  # Ponto do meio (vértice)
        c = np.array(c)  # Último ponto
        
        # Calcular vetores
        ba = a - b
        bc = c - b
        
        # Calcular ângulo usando o produto escalar
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        
        # Converter para graus
        return np.degrees(angle)