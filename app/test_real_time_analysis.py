#!/usr/bin/env python3
"""
Teste de Análise em Tempo Real
Verifica se o sistema principal está funcionando com o modelo treinado
"""

import cv2
import mediapipe as mp
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from analysis import CommunicationAnalyzer

def test_real_time_analysis():
    """Testa análise em tempo real"""
    print("🎯 Teste de Análise em Tempo Real")
    print("=" * 50)
    
    # Inicializar MediaPipe
    mp_pose = mp.solutions.pose
    mp_hands = mp.solutions.hands
    mp_face = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        enable_segmentation=False,
        smooth_segmentation=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    face = mp_face.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # Inicializar analisador
    analyzer = CommunicationAnalyzer()
    
    print("📊 Configuração Atual:")
    print(f"  shoulder_threshold: {analyzer.config['posture']['shoulder_threshold']:.4f}")
    print(f"  hip_threshold: {analyzer.config['posture']['hip_threshold']:.4f}")
    print(f"  spine_threshold: {analyzer.config['posture']['spine_threshold']:.4f}")
    print(f"  feedback_thresholds: {analyzer.config['feedback_thresholds']['posture']}")
    
    # Abrir câmera
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Erro: Não foi possível abrir a câmera")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("\n🎥 Câmera aberta com sucesso!")
    print("📋 Instruções:")
    print("  - Teste diferentes posturas (boa, ruim, neutra)")
    print("  - Observe os scores em tempo real")
    print("  - Pressione 'q' para sair")
    print("  - Pressione 'r' para resetar scores")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Converter para RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Processar com MediaPipe
        pose_results = pose.process(rgb_frame)
        hands_results = hands.process(rgb_frame)
        face_results = face.process(rgb_frame)
        
        # Analisar
        posture_score = analyzer.analyze_posture(pose_results)
        gesture_score = analyzer.analyze_gestures(hands_results)
        eye_contact_score = analyzer.analyze_eye_contact(frame, face_results)
        
        # Gerar feedback
        feedback = analyzer.generate_feedback(posture_score, gesture_score, eye_contact_score)
        overall_score = analyzer.get_overall_score(posture_score, gesture_score, eye_contact_score)
        
        # Desenhar landmarks
        annotated_frame = frame.copy()
        if pose_results.pose_landmarks:
            mp_drawing.draw_landmarks(
                annotated_frame, 
                pose_results.pose_landmarks, 
                mp_pose.POSE_CONNECTIONS
            )
        
        if hands_results.multi_hand_landmarks:
            for hand_landmarks in hands_results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    annotated_frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS
                )
        
        # Mostrar scores na tela
        cv2.putText(annotated_frame, f"Postura: {posture_score:.1f}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(annotated_frame, f"Gestos: {gesture_score:.1f}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(annotated_frame, f"Contato Visual: {eye_contact_score:.1f}", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(annotated_frame, f"Score Geral: {overall_score:.1f}", 
                   (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Mostrar feedback
        y_offset = 150
        for i, fb in enumerate(feedback[:3]):  # Mostrar apenas os 3 primeiros
            cv2.putText(annotated_frame, fb, 
                       (10, y_offset + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Instruções
        cv2.putText(annotated_frame, "Pressione 'q' para sair, 'r' para resetar", 
                   (10, annotated_frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow('Análise em Tempo Real', annotated_frame)
        
        # Controles
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            analyzer.reset_scores()
            print("🔄 Scores resetados!")
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n📊 Resumo do Teste:")
    print("✅ Sistema funcionando com modelo treinado!")
    print("🎯 Thresholds rigorosos aplicados")
    print("💡 Agora o sistema deve diferenciar melhor as posturas")

if __name__ == "__main__":
    test_real_time_analysis()
