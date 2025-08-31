"""
Edge Coach - Core Processing Module

Consolidated processing module that handles all MediaPipe operations,
feature extraction, and analysis logic. This module combines functionality
from multiple previous files into a unified processing pipeline.

Key Components:
- FeatureTracker: Analyzes facial expressions, blinks, and body movement
- MediaPipeProcessor: Unified interface for pose, face, and hand detection
- AudioProcessor: Real-time audio analysis and feature extraction
- PresentationAnalyzer: High-level session analysis and recommendations

MediaPipe Integration:
- 33-point pose detection
- 468-point facial landmark detection
- Multi-hand tracking (up to 2 hands)
- Real-time metric calculation

Features Extracted:
- Nervousness score (0-1) based on movement patterns
- Blink rate and eye aspect ratio
- Hand and head movement amplitude
- Audio volume, energy, and zero-crossings
- Session-level statistics and trends

Usage:
    from core_processing import MediaPipeProcessor
    
    processor = MediaPipeProcessor()
    results = processor.process_frame(frame)
    metrics = results['metrics']

Author: Edge AI Hackathon Team
License: MIT
"""

import numpy as np
import cv2
import time
from collections import deque
from typing import Dict, List, Optional, Any, Tuple
import mediapipe as mp

# MediaPipe Pose landmark names (33 landmarks)
LANDMARK_NAMES = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer", "right_eye_inner", "right_eye",
    "right_eye_outer", "left_ear", "right_ear", "mouth_left", "mouth_right", "left_shoulder",
    "right_shoulder", "left_elbow", "right_elbow", "left_wrist", "right_wrist", "left_pinky",
    "right_pinky", "left_index", "right_index", "left_thumb", "right_thumb", "left_hip",
    "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle", "left_heel",
    "right_heel", "left_foot_index", "right_foot_index"
]

class FeatureTracker:
    """Tracks facial and body features for presentation analysis"""
    
    def __init__(self, window_size=30):
        self.window_size = window_size
        self.blink_history = deque(maxlen=window_size)
        self.hand_movement_history = deque(maxlen=window_size)
        self.head_movement_history = deque(maxlen=window_size)
        self.previous_landmarks = None
        self.last_blink_time = 0
        
        # Eye landmark indices for blink detection
        self.LEFT_EYE_IDX = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_IDX = [33, 160, 158, 133, 153, 144]
        
    def calculate_eye_aspect_ratio(self, eye_landmarks):
        """Calculate Eye Aspect Ratio (EAR) for blink detection"""
        if len(eye_landmarks) < 6:
            return 0.3
        
        # Vertical distances
        v1 = np.linalg.norm(np.array(eye_landmarks[1]) - np.array(eye_landmarks[5]))
        v2 = np.linalg.norm(np.array(eye_landmarks[2]) - np.array(eye_landmarks[4]))
        
        # Horizontal distance
        h = np.linalg.norm(np.array(eye_landmarks[0]) - np.array(eye_landmarks[3]))
        
        if h == 0:
            return 0.3
        
        ear = (v1 + v2) / (2.0 * h)
        return ear
    
    def detect_blink(self, face_landmarks, ear_threshold=0.25):
        """Detect blink from face landmarks"""
        try:
            if not face_landmarks:
                return False, 0.0
            
            # Extract eye landmarks
            left_eye = [(face_landmarks[i].x, face_landmarks[i].y) for i in self.LEFT_EYE_IDX]
            right_eye = [(face_landmarks[i].x, face_landmarks[i].y) for i in self.RIGHT_EYE_IDX]
            
            # Calculate EAR for both eyes
            left_ear = self.calculate_eye_aspect_ratio(left_eye)
            right_ear = self.calculate_eye_aspect_ratio(right_eye)
            
            avg_ear = (left_ear + right_ear) / 2.0
            
            # Detect blink
            blink_detected = avg_ear < ear_threshold
            
            if blink_detected:
                self.last_blink_time = time.time()
            
            return blink_detected, avg_ear
            
        except Exception as e:
            return False, 0.3
    
    def calculate_movement(self, current_landmarks, previous_landmarks):
        """Calculate movement between frames"""
        if not previous_landmarks or not current_landmarks:
            return 0.0
        
        total_movement = 0.0
        count = 0
        
        for curr, prev in zip(current_landmarks, previous_landmarks):
            if hasattr(curr, 'x') and hasattr(prev, 'x'):
                dx = curr.x - prev.x
                dy = curr.y - prev.y
                movement = np.sqrt(dx**2 + dy**2)
                total_movement += movement
                count += 1
        
        return total_movement / count if count > 0 else 0.0
    
    def extract_metrics(self, face_landmarks, pose_landmarks, hand_landmarks):
        """Extract comprehensive metrics from MediaPipe landmarks"""
        current_time = time.time()
        
        # Blink detection
        blink_detected, ear_value = self.detect_blink(face_landmarks)
        
        # Calculate movements
        hand_movement = 0.0
        head_movement = 0.0
        
        if hand_landmarks and self.previous_landmarks:
            hand_movement = self.calculate_movement(hand_landmarks, self.previous_landmarks.get('hands', []))
        
        if face_landmarks and self.previous_landmarks:
            head_movement = self.calculate_movement(face_landmarks[:10], self.previous_landmarks.get('face', [])[:10])
        
        # Update histories
        self.blink_history.append(blink_detected)
        self.hand_movement_history.append(hand_movement)
        self.head_movement_history.append(head_movement)
        
        # Calculate statistics
        blink_rate = sum(self.blink_history) / len(self.blink_history) * 60 if self.blink_history else 0
        avg_hand_movement = np.mean(self.hand_movement_history) if self.hand_movement_history else 0
        avg_head_movement = np.mean(self.head_movement_history) if self.head_movement_history else 0
        
        # Calculate nervousness score (0-1)
        nervousness_factors = []
        
        if blink_rate > 0:
            # Normal blink rate is 12-20 per minute
            blink_nervousness = min(1.0, max(0.0, (blink_rate - 12) / 20))
            nervousness_factors.append(blink_nervousness)
        
        if avg_hand_movement > 0:
            # Normalize hand movement (threshold based on experience)
            hand_nervousness = min(1.0, avg_hand_movement * 10)
            nervousness_factors.append(hand_nervousness)
        
        nervousness_score = np.mean(nervousness_factors) if nervousness_factors else 0.0
        
        # Store current landmarks for next frame
        self.previous_landmarks = {
            'face': face_landmarks,
            'pose': pose_landmarks,
            'hands': hand_landmarks
        }
        
        return {
            'timestamp': current_time,
            'nervousness_score': float(nervousness_score),
            'blink_detected': blink_detected,
            'blink_stats': {
                'blink_rate': float(blink_rate),
                'ear_value': float(ear_value),
                'last_blink': self.last_blink_time
            },
            'hand_movement': float(hand_movement),
            'head_movement': float(head_movement),
            'hands_detected': len(hand_landmarks) if hand_landmarks else 0,
            'face_detected': 1 if face_landmarks else 0,
            'raw_metrics': {
                'avg_hand_movement': float(avg_hand_movement),
                'avg_head_movement': float(avg_head_movement),
                'blink_count': sum(self.blink_history),
                'frame_count': len(self.blink_history)
            }
        }


class MediaPipeProcessor:
    """Unified MediaPipe processing for pose, face, and hand detection"""
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_face = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize models
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.face_mesh = self.mp_face.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.feature_tracker = FeatureTracker()
    
    def process_frame(self, frame):
        """Process a single frame and extract all landmarks"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        pose_results = self.pose.process(rgb_frame)
        face_results = self.face_mesh.process(rgb_frame)
        hand_results = self.hands.process(rgb_frame)
        
        # Extract landmarks
        face_landmarks = face_results.multi_face_landmarks[0].landmark if face_results.multi_face_landmarks else None
        pose_landmarks = pose_results.pose_landmarks.landmark if pose_results.pose_landmarks else None
        hand_landmarks = []
        
        if hand_results.multi_hand_landmarks:
            for hand_landmark in hand_results.multi_hand_landmarks:
                hand_landmarks.extend(hand_landmark.landmark)
        
        # Extract metrics
        metrics = self.feature_tracker.extract_metrics(face_landmarks, pose_landmarks, hand_landmarks)
        
        # Convert pose landmarks to joints dict if available
        joints_dict = {}
        if pose_landmarks:
            joints_dict = self.landmarks_to_joints(pose_landmarks)
        
        return {
            'metrics': metrics,
            'joints': joints_dict,
            'pose_landmarks': pose_landmarks,
            'face_landmarks': face_landmarks,
            'hand_landmarks': hand_landmarks,
            'annotated_frame': self.draw_annotations(frame, pose_results, face_results, hand_results)
        }
    
    def landmarks_to_joints(self, landmarks) -> Dict[str, float]:
        """Convert MediaPipe pose landmarks to flat joints dictionary"""
        joints = {}
        
        for i, landmark in enumerate(landmarks):
            if i < len(LANDMARK_NAMES):
                name = LANDMARK_NAMES[i]
                joints[f"{name}_x"] = landmark.x
                joints[f"{name}_y"] = landmark.y
                joints[f"{name}_z"] = landmark.z
                joints[f"{name}_visibility"] = getattr(landmark, 'visibility', 1.0)
        
        return joints
    
    def draw_annotations(self, frame, pose_results, face_results, hand_results):
        """Draw MediaPipe annotations on frame"""
        annotated_frame = frame.copy()
        
        # Draw pose landmarks
        if pose_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                annotated_frame, 
                pose_results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS
            )
        
        # Draw face mesh
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    annotated_frame, 
                    face_landmarks, 
                    self.mp_face.FACEMESH_CONTOURS
                )
        
        # Draw hand landmarks
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    annotated_frame, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS
                )
        
        return annotated_frame
    
    def cleanup(self):
        """Cleanup MediaPipe resources"""
        if hasattr(self, 'pose'):
            self.pose.close()
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
        if hasattr(self, 'hands'):
            self.hands.close()


class AudioProcessor:
    """Audio processing for speech analysis"""
    
    def __init__(self, sample_rate=16000, chunk_size=1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio_buffer = []
        
    def process_audio_chunk(self, audio_data):
        """Process audio chunk for speech features"""
        # Add to buffer
        self.audio_buffer.append(audio_data)
        
        # Keep only last 5 seconds of audio
        max_chunks = (self.sample_rate * 5) // self.chunk_size
        if len(self.audio_buffer) > max_chunks:
            self.audio_buffer = self.audio_buffer[-max_chunks:]
        
        # Calculate basic audio features
        if len(audio_data) > 0:
            volume = np.sqrt(np.mean(audio_data**2))
            zero_crossings = np.sum(np.diff(np.sign(audio_data)) != 0)
            
            return {
                'volume': float(volume),
                'zero_crossings': int(zero_crossings),
                'energy': float(np.sum(audio_data**2)),
                'timestamp': time.time()
            }
        
        return None
    
    def get_audio_buffer(self):
        """Get current audio buffer as numpy array"""
        if self.audio_buffer:
            return np.concatenate(self.audio_buffer)
        return np.array([])


class PresentationAnalyzer:
    """High-level analyzer that combines all processing modules"""
    
    def __init__(self, api_base="http://localhost:8000"):
        self.api_base = api_base
        self.session_start = time.time()
        self.frame_count = 0
        
    def analyze_session_data(self, metrics_history, transcript_data):
        """Analyze complete session data"""
        if not metrics_history:
            return {"error": "No metrics data available"}
        
        # Calculate session statistics
        session_duration = time.time() - self.session_start
        total_frames = len(metrics_history)
        
        # Analyze nervousness patterns
        nervousness_scores = [m.get('nervousness_score', 0) for m in metrics_history]
        avg_nervousness = np.mean(nervousness_scores)
        max_nervousness = np.max(nervousness_scores)
        
        # Analyze blink patterns
        blink_rates = [m.get('blink_stats', {}).get('blink_rate', 0) for m in metrics_history]
        avg_blink_rate = np.mean(blink_rates)
        
        # Analyze movement patterns
        hand_movements = [m.get('raw_metrics', {}).get('avg_hand_movement', 0) for m in metrics_history]
        avg_hand_movement = np.mean(hand_movements)
        
        analysis_results = {
            'session_duration': session_duration,
            'total_frames': total_frames,
            'avg_nervousness': float(avg_nervousness),
            'max_nervousness': float(max_nervousness),
            'avg_blink_rate': float(avg_blink_rate),
            'avg_hand_movement': float(avg_hand_movement),
            'transcript_length': len(transcript_data.get('transcript', '')),
            'recommendations': self._generate_recommendations(
                avg_nervousness, avg_blink_rate, avg_hand_movement
            )
        }
        
        return analysis_results
    
    def _generate_recommendations(self, nervousness, blink_rate, hand_movement):
        """Generate recommendations based on metrics"""
        recommendations = []
        
        if nervousness > 0.7:
            recommendations.append("Alto nível de nervosismo detectado. Pratique técnicas de respiração.")
        elif nervousness > 0.5:
            recommendations.append("Nervosismo moderado. Tente relaxar os ombros e respirar profundamente.")
        
        if blink_rate > 25:
            recommendations.append("Taxa de piscadas elevada. Mantenha contato visual com a audiência.")
        elif blink_rate < 8:
            recommendations.append("Poucas piscadas detectadas. Lembre-se de piscar naturalmente.")
        
        if hand_movement > 0.1:
            recommendations.append("Movimento excessivo das mãos. Use gestos mais controlados.")
        elif hand_movement < 0.01:
            recommendations.append("Pouco movimento das mãos. Use gestos para enfatizar pontos importantes.")
        
        if not recommendations:
            recommendations.append("Boa performance geral! Continue praticando para melhorar ainda mais.")
        
        return recommendations
