import cv2
import mediapipe as mp
import numpy as np
import time
import requests
from features import extract_features

# Configuração MediaPipe
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# URL do servidor local
API_URL = "http://localhost:8000"

def main():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Não foi possível abrir a câmera. Verifique se está conectada e liberada por outro programa.")
        input("Pressione Enter para sair...")
        return
    
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh, mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:
        
        print("🎥 Iniciando captura de vídeo...")
        print("Pressione 'q' para sair a qualquer momento")
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️  Falha ao capturar frame. Tentando novamente...")
                time.sleep(0.1)
                continue
            
            frame_count += 1
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Processar com MediaPipe
            face_results = face_mesh.process(rgb_frame)
            hand_results = hands.process(rgb_frame)
            
            # Extrair features
            features = extract_features(face_results, hand_results, frame)
            
            # Enviar dados a cada 30 frames (~1 segundo)
            if frame_count % 30 == 0:
                try:
                    response = requests.post(f"{API_URL}/metrics", json=features, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ Métricas enviadas - Frame {frame_count}")
                    else:
                        print(f"❌ Erro API: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"⚠️  Servidor offline ou indisponível: {e}")
            
            # Desenhar landmarks
            if face_results.multi_face_landmarks:
                for face_landmarks in face_results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS,
                        None, mp_drawing.DrawingSpec(color=(0,255,0), thickness=1, circle_radius=1)
                    )
            
            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Mostrar FPS
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time if elapsed_time > 0 else 0
            
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Nervosismo: {features.get('nervousness_score', 0):.2f}", 
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, "Pressione 'q' para sair", (10, frame.shape[0] - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('Edge Coach - Análise em Tempo Real', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("🛑 Saindo por comando do usuário...")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print(f"📊 Captura finalizada. Total de frames: {frame_count}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
