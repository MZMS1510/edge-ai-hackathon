#!/usr/bin/env python3
"""
Sistema de Coleta de Dados para Treinamento de Análise de Postura - Versão Corrigida
Coleta landmarks de diferentes poses para melhorar a precisão do modelo
"""

import cv2
import mediapipe as mp
import numpy as np
import json
import os
from datetime import datetime
import time

class PostureDataCollectorFixed:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=True,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3
        )
        
        self.data_dir = "training_data"
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        """Cria diretório para dados de treinamento"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            os.makedirs(os.path.join(self.data_dir, "good_posture"))
            os.makedirs(os.path.join(self.data_dir, "bad_posture"))
            os.makedirs(os.path.join(self.data_dir, "neutral_posture"))
    
    def open_camera_with_fallback(self):
        """Tenta abrir a câmera com diferentes configurações"""
        print("🔧 Tentando abrir câmera com diferentes configurações...")
        
        # Tentar diferentes backends
        backends = [
            cv2.CAP_DSHOW,  # DirectShow (Windows)
            cv2.CAP_MSMF,   # Media Foundation (Windows)
            cv2.CAP_ANY,    # Qualquer backend disponível
        ]
        
        for backend in backends:
            print(f"  Tentando backend {backend}...")
            
            # Tentar diferentes índices de câmera
            for camera_index in [0, 1]:
                try:
                    cap = cv2.VideoCapture(camera_index, backend)
                    
                    if cap.isOpened():
                        print(f"    ✅ Câmera {camera_index} aberta com backend {backend}")
                        
                        # Tentar ler um frame
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            print(f"    ✅ Frame lido com sucesso!")
                            print(f"    📐 Dimensões: {frame.shape}")
                            
                            # Configurar propriedades
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                            cap.set(cv2.CAP_PROP_FPS, 30)
                            
                            return cap
                        else:
                            print(f"    ❌ Erro ao ler frame")
                            cap.release()
                    else:
                        print(f"    ❌ Não foi possível abrir câmera {camera_index}")
                        
                except Exception as e:
                    print(f"    ❌ Erro: {e}")
                    continue
        
        print("❌ Nenhuma configuração funcionou!")
        return None
    
    def collect_posture_data(self, posture_type, duration_seconds=10, sample_rate=0.5):
        """
        Coleta dados de uma pose específica
        """
        print(f"🎯 Iniciando coleta de {posture_type}...")
        
        # Tentar abrir câmera com fallback
        cap = self.open_camera_with_fallback()
        
        if cap is None:
            print("❌ Não foi possível abrir a câmera")
            print("💡 Soluções:")
            print("   1. Verifique permissões de câmera no Windows")
            print("   2. Feche outros programas que usam câmera")
            print("   3. Reinicie o computador")
            print("   4. Verifique se a câmera está conectada")
            return
        
        print(f"✅ Câmera aberta com sucesso!")
        print(f"⏱️ Duração: {duration_seconds} segundos")
        print(f"📊 Taxa de amostragem: {sample_rate} segundos")
        print("📋 Instruções:")
        
        if posture_type == "good_posture":
            print("  - Mantenha uma postura ereta e alinhada")
            print("  - Ombros nivelados")
            print("  - Coluna reta")
            print("  - Fique a 1-2 metros da câmera")
        elif posture_type == "bad_posture":
            print("  - Simule uma postura ruim")
            print("  - Ombros desalinhados")
            print("  - Coluna curvada")
            print("  - Fique a 1-2 metros da câmera")
        else:
            print("  - Mantenha uma postura neutra/regular")
            print("  - Fique a 1-2 metros da câmera")
        
        print("\n🔄 Pressione 'q' para sair ou aguarde o tempo definido")
        print("💡 Certifique-se de que há boa iluminação")
        
        samples = []
        start_time = time.time()
        last_sample_time = 0
        detection_count = 0
        total_frames = 0
        detection_rate = 0.0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    print("⚠️ Erro ao ler frame, tentando continuar...")
                    time.sleep(0.1)
                    continue
                
                total_frames += 1
                
                # Converter para RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(rgb_frame)
                
                # Desenhar landmarks
                annotated_frame = frame.copy()
                if results.pose_landmarks:
                    detection_count += 1
                    self.mp_drawing.draw_landmarks(
                        annotated_frame, 
                        results.pose_landmarks, 
                        self.mp_pose.POSE_CONNECTIONS
                    )
                    
                    # Desenhar pontos importantes
                    for landmark in [self.mp_pose.PoseLandmark.LEFT_SHOULDER, 
                                   self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
                                   self.mp_pose.PoseLandmark.LEFT_HIP,
                                   self.mp_pose.PoseLandmark.RIGHT_HIP]:
                        landmark_point = results.pose_landmarks.landmark[landmark]
                        h, w, _ = frame.shape
                        x, y = int(landmark_point.x * w), int(landmark_point.y * h)
                        cv2.circle(annotated_frame, (x, y), 5, (0, 255, 0), -1)
                else:
                    # Mostrar aviso quando não detecta pose
                    cv2.putText(annotated_frame, "POSE NAO DETECTADA", 
                               (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.putText(annotated_frame, "Aproxime-se da camera", 
                               (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Mostrar informações na tela
                elapsed_time = time.time() - start_time
                remaining_time = max(0, duration_seconds - elapsed_time)
                
                # Informações de debug
                detection_rate = (detection_count / total_frames * 100) if total_frames > 0 else 0
                
                cv2.putText(annotated_frame, f"Tempo: {remaining_time:.1f}s", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"Tipo: {posture_type}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"Amostras: {len(samples)}", 
                           (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"Detecção: {detection_rate:.1f}%", 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Instruções na tela
                cv2.putText(annotated_frame, "Pressione 'q' para sair", 
                           (10, annotated_frame.shape[0] - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(annotated_frame, "Certifique-se de estar visivel na camera", 
                           (10, annotated_frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.imshow('Coleta de Dados de Postura', annotated_frame)
                
                # Coletar amostra se passou tempo suficiente
                current_time = time.time()
                if current_time - last_sample_time >= sample_rate:
                    if results.pose_landmarks:
                        # Verificar se os landmarks necessários estão visíveis
                        landmarks = results.pose_landmarks.landmark
                        required_landmarks = [
                            self.mp_pose.PoseLandmark.LEFT_SHOULDER,
                            self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
                            self.mp_pose.PoseLandmark.LEFT_HIP,
                            self.mp_pose.PoseLandmark.RIGHT_HIP
                        ]
                        
                        # Verificar visibilidade dos landmarks
                        all_visible = True
                        for landmark_idx in required_landmarks:
                            if landmarks[landmark_idx].visibility < 0.5:
                                all_visible = False
                                break
                        
                        if all_visible:
                            sample = self.extract_landmarks(results.pose_landmarks)
                            samples.append(sample)
                            last_sample_time = current_time
                            print(f"✅ Amostra coletada! Total: {len(samples)}")
                        else:
                            print("⚠️ Landmarks não suficientemente visíveis")
                    else:
                        print("⚠️ Pose não detectada")
                
                # Verificar se terminou o tempo ou pressionou 'q'
                if remaining_time <= 0 or cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except Exception as e:
            print(f"❌ Erro durante a coleta: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()
        
        # Salvar dados coletados
        if samples:
            self.save_samples(posture_type, samples)
            print(f"✅ Coletadas {len(samples)} amostras de {posture_type}")
            print(f"📊 Taxa de detecção: {detection_rate:.1f}%")
        else:
            print("❌ Nenhuma amostra foi coletada")
            print("💡 Possíveis soluções:")
            print("   - Certifique-se de estar a 1-2 metros da câmera")
            print("   - Verifique se há boa iluminação")
            print("   - Certifique-se de que seu corpo inteiro está visível")
            print(f"   - Taxa de detecção foi: {detection_rate:.1f}%")
    
    def extract_landmarks(self, pose_landmarks):
        """Extrai landmarks relevantes para análise de postura"""
        landmarks = pose_landmarks.landmark
        
        # Pontos de interesse para postura
        key_points = {
            'left_shoulder': landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER],
            'right_shoulder': landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER],
            'left_hip': landmarks[self.mp_pose.PoseLandmark.LEFT_HIP],
            'right_hip': landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP],
            'left_ear': landmarks[self.mp_pose.PoseLandmark.LEFT_EAR],
            'right_ear': landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR],
            'nose': landmarks[self.mp_pose.PoseLandmark.NOSE],
        }
        
        # Extrair coordenadas
        sample = {
            'timestamp': datetime.now().isoformat(),
            'landmarks': {}
        }
        
        for name, landmark in key_points.items():
            sample['landmarks'][name] = {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            }
        
        # Calcular métricas derivadas
        sample['metrics'] = self.calculate_posture_metrics(key_points)
        
        return sample
    
    def calculate_posture_metrics(self, key_points):
        """Calcula métricas de postura"""
        left_shoulder = key_points['left_shoulder']
        right_shoulder = key_points['right_shoulder']
        left_hip = key_points['left_hip']
        right_hip = key_points['right_hip']
        
        metrics = {
            'shoulder_angle': abs(left_shoulder.y - right_shoulder.y),
            'hip_angle': abs(left_hip.y - right_hip.y),
            'spine_alignment': abs((left_shoulder.y + right_shoulder.y) / 2 - 
                                 (left_hip.y + right_hip.y) / 2),
            'shoulder_width': abs(left_shoulder.x - right_shoulder.x),
            'hip_width': abs(left_hip.x - right_hip.x),
        }
        
        return metrics
    
    def save_samples(self, posture_type, samples):
        """Salva as amostras coletadas"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{posture_type}_{timestamp}.json"
        filepath = os.path.join(self.data_dir, posture_type, filename)
        
        data = {
            'posture_type': posture_type,
            'collection_time': datetime.now().isoformat(),
            'sample_count': len(samples),
            'samples': samples
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Dados salvos em: {filepath}")
    
    def interactive_collection(self):
        """Interface interativa para coleta de dados"""
        print("🎯 Sistema de Coleta de Dados de Postura - Versão Corrigida")
        print("=" * 60)
        
        while True:
            print("\n📋 Opções:")
            print("1. Coletar postura boa")
            print("2. Coletar postura ruim")
            print("3. Coletar postura neutra")
            print("4. Ver estatísticas")
            print("5. Sair")
            
            choice = input("\nEscolha uma opção (1-5): ").strip()
            
            if choice == "1":
                self.collect_posture_data("good_posture")
            elif choice == "2":
                self.collect_posture_data("bad_posture")
            elif choice == "3":
                self.collect_posture_data("neutral_posture")
            elif choice == "4":
                self.show_statistics()
            elif choice == "5":
                print("👋 Saindo do sistema de coleta")
                break
            else:
                print("❌ Opção inválida")
    
    def show_statistics(self):
        """Mostra estatísticas dos dados coletados"""
        print("\n📊 Estatísticas dos Dados Coletados")
        print("=" * 40)
        
        for posture_type in ["good_posture", "bad_posture", "neutral_posture"]:
            folder_path = os.path.join(self.data_dir, posture_type)
            if os.path.exists(folder_path):
                files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
                total_samples = 0
                
                for file in files:
                    filepath = os.path.join(folder_path, file)
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            total_samples += data['sample_count']
                    except:
                        pass
                
                print(f"{posture_type}: {len(files)} arquivos, {total_samples} amostras")
            else:
                print(f"{posture_type}: 0 arquivos, 0 amostras")

if __name__ == "__main__":
    collector = PostureDataCollectorFixed()
    collector.interactive_collection()
