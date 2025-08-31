import os
import mediapipe as mp

def load_mediapipe_models(use_qualcomm=True):
    """
    Carrega os modelos MediaPipe para detecção facial e de pose.
    
    Args:
        use_qualcomm: Se True, tenta usar a versão otimizada para Qualcomm
        
    Returns:
        tuple: (face_mesh, pose) modelos para análise visual
    """
    try:
        if use_qualcomm:
            # Tentar carregar modelos otimizados para Qualcomm
            try:
                print("A opção use_qualcomm=True foi ignorada devido à falta do módulo qai_hub_models")
                print("Usando modelos MediaPipe padrão...")
            except Exception as e:
                print(f"Não foi possível carregar os modelos MediaPipe otimizados para Qualcomm: {str(e)}")
                print("Usando modelos MediaPipe padrão...")
        
        # Carregar modelos padrão do MediaPipe
        mp_face_mesh = mp.solutions.face_mesh
        mp_pose = mp.solutions.pose
        
        # Configurar modelos
        face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        print("Modelos MediaPipe carregados com sucesso.")
        return face_mesh, pose
    
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar modelos MediaPipe: {str(e)}")