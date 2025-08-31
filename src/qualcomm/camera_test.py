#!/usr/bin/env python3
"""
Teste de Câmera - Qualcomm Edge AI
"""

import cv2
import time

def test_camera():
    print("🔍 Testando câmeras disponíveis...")
    
    # Testar diferentes índices de câmera
    for i in range(5):
        print(f"�� Tentando câmera {i}...")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            print(f"✅ Câmera {i} funcionando!")
            
            # Tentar ler um frame
            ret, frame = cap.read()
            if ret:
                print(f"✅ Frame lido com sucesso: {frame.shape}")
                cap.release()
                return i
            else:
                print(f"❌ Câmera {i} aberta mas não consegue ler frames")
                cap.release()
        else:
            print(f"❌ Câmera {i} não disponível")
    
    return None

if __name__ == "__main__":
    camera_index = test_camera()
    if camera_index is not None:
        print(f"�� Use camera_index = {camera_index}")
    else:
        print("❌ Nenhuma câmera funcionando")
