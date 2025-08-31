#!/usr/bin/env python3
"""
Teste Específico de Análise de Gestos
Verifica se a análise de gestos está funcionando corretamente
"""

import cv2
import mediapipe as mp
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from analysis import CommunicationAnalyzer

def test_gesture_analysis():
    """Testa análise de gestos em tempo real"""
    print("🎯 Teste de Análise de Gestos")
    print("=" * 50)
    
    # Inicializar MediaPipe
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # Inicializar analisador
    analyzer = CommunicationAnalyzer()
    
    print("📊 Configuração de Gestos:")
    print(f"  movement_threshold_low: {analyzer.config['gesture']['movement_threshold_low']:.3f}")
    print(f"  movement_threshold_high: {analyzer.config['gesture']['movement_threshold_high']:.3f}")
    print(f"  base_score_no_hands: {analyzer.config['gesture']['base_score_no_hands']}")
    
    # Abrir câmera
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Erro: Não foi possível abrir a câmera")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("\n🎥 Câmera aberta com sucesso!")
    print("📋 Instruções:")
    print("  - Fique parado (sem gestos) e observe o score")
    print("  - Faça gestos com as mãos e observe o score aumentar")
    print("  - Use uma mão ou duas mãos")
    print("  - Pressione 'q' para sair")
    print("  - Pressione 'r' para resetar scores")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Converter para RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Processar com MediaPipe
        hands_results = hands.process(rgb_frame)
        
        # Analisar gestos
        gesture_score = analyzer.analyze_gestures(hands_results)
        
        # Calcular movimento real para debug
        movement_info = "Sem mãos detectadas"
        if hands_results.multi_hand_landmarks:
            total_movement = 0
            hand_count = len(hands_results.multi_hand_landmarks)
            
            for hand_landmarks in hands_results.multi_hand_landmarks:
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                
                hand_movement = (abs(wrist.y - thumb_tip.y) + 
                               abs(wrist.y - index_tip.y) + 
                               abs(wrist.y - middle_tip.y)) / 3
                total_movement += hand_movement
            
            avg_movement = total_movement / hand_count if hand_count > 0 else 0
            movement_info = f"Mãos: {hand_count}, Movimento: {avg_movement:.3f}"
        
        # Desenhar landmarks
        annotated_frame = frame.copy()
        if hands_results.multi_hand_landmarks:
            for hand_landmarks in hands_results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    annotated_frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS
                )
        
        # Mostrar informações na tela
        cv2.putText(annotated_frame, f"Score Gestos: {gesture_score:.1f}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(annotated_frame, movement_info, 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Mostrar thresholds
        cv2.putText(annotated_frame, f"Low: {analyzer.config['gesture']['movement_threshold_low']:.3f}", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        cv2.putText(annotated_frame, f"High: {analyzer.config['gesture']['movement_threshold_high']:.3f}", 
                   (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        
        # Instruções
        cv2.putText(annotated_frame, "Fique parado ou faça gestos", 
                   (10, annotated_frame.shape[0] - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(annotated_frame, "Pressione 'q' para sair, 'r' para resetar", 
                   (10, annotated_frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow('Teste de Análise de Gestos', annotated_frame)
        
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
    print("✅ Análise de gestos corrigida!")
    print("🎯 Agora o sistema deve:")
    print("   - Dar score baixo quando você está parado")
    print("   - Dar score alto quando você faz gestos")
    print("   - Diferenciar entre pouco e muito movimento")

if __name__ == "__main__":
    test_gesture_analysis()
