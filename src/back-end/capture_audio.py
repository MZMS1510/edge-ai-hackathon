import sounddevice as sd
import soundfile as sf
import numpy as np
import time
import requests
from faster_whisper import WhisperModel
import threading
import queue
import os

# Configurações
SAMPLE_RATE = 16000
CHANNELS = 1
API_URL = "http://localhost:8000"
CHUNK_DURATION = 10  # segundos por chunk
AUDIO_FILE = "session.wav"

class AudioProcessor:
    def __init__(self):
        print("🎤 Carregando modelo Whisper...")
        self.whisper_model = WhisperModel("small", device="cpu")
        print("✅ Whisper carregado!")
        
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.audio_data = []
        
    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"⚠️ Status do áudio: {status}")
        
        # Debug rápido para ver se o microfone está enviando dados
        print(f"Áudio recebido: {indata.shape}, primeira amostra: {indata[0][0]}")
        
        # Adicionar audio na queue
        self.audio_queue.put(indata.copy())
        
        # Armazenar para arquivo completo
        self.audio_data.extend(indata.flatten())



        
        # Adicionar audio na queue
        self.audio_queue.put(indata.copy())
        
        # Armazenar para arquivo completo
        self.audio_data.extend(indata.flatten())
    
    def process_audio_chunk(self, audio_chunk):
        """Processa chunk de áudio e envia transcrição"""
        try:
            # Salvar chunk temporário
            temp_file = f"temp_chunk_{int(time.time())}.wav"
            sf.write(temp_file, audio_chunk, SAMPLE_RATE)
            
            # Transcrever com Whisper
            segments, info = self.whisper_model.transcribe(
                temp_file, 
                language="pt",
                word_timestamps=False
            )
            
            # Juntar segmentos
            text = " ".join([segment.text.strip() for segment in segments])
            
            if text.strip():
                print(f"📝 Transcrição: {text[:100]}...")
                
                # Enviar para API
                payload = {
                    "transcript": text,
                    "timestamp": time.time(),
                    "duration": len(audio_chunk) / SAMPLE_RATE
                }
                
                response = requests.post(
                    f"{API_URL}/transcript", 
                    json=payload,
                    timeout=5
                )
                
                if response.status_code == 200:
                    print("✅ Transcrição enviada para servidor")
                else:
                    print(f"❌ Erro ao enviar transcrição: {response.status_code}")
            
            # Limpar arquivo temporário
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except Exception as e:
            print(f"❌ Erro ao processar áudio: {e}")
    
    def audio_processor_thread(self):
        """Thread para processar áudio em chunks"""
        chunk_data = []
        chunk_start = time.time()
        
        while self.is_recording:
            try:
                # Pegar dados da queue com timeout
                audio_frame = self.audio_queue.get(timeout=1.0)
                chunk_data.extend(audio_frame.flatten())
                
                # Processar chunk quando atingir duração desejada
                if time.time() - chunk_start >= CHUNK_DURATION:
                    if len(chunk_data) > 0:
                        chunk_array = np.array(chunk_data)
                        
                        # Processar em thread separada para não bloquear
                        threading.Thread(
                            target=self.process_audio_chunk, 
                            args=(chunk_array,),
                            daemon=True
                        ).start()
                    
                    # Reset chunk
                    chunk_data = []
                    chunk_start = time.time()
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Erro no processamento: {e}")
    
    def start_recording(self):
        """Inicia gravação de áudio"""
        print(f"🎤 Iniciando gravação...")
        print(f"📊 Taxa de amostragem: {SAMPLE_RATE}Hz")
        print(f"⏱️  Chunks de {CHUNK_DURATION}s")
        print("Pressione Ctrl+C para parar\n")
        
        self.is_recording = True
        self.audio_data = []
        
        # Iniciar thread de processamento
        processor_thread = threading.Thread(
            target=self.audio_processor_thread, 
            daemon=True
        )
        processor_thread.start()
        
        try:
            with sd.InputStream(
                callback=self.audio_callback,
                channels=CHANNELS,
                samplerate=SAMPLE_RATE,
                dtype=np.float32
            ):
                while self.is_recording:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Parando gravação...")
            
        finally:
            self.stop_recording()
    
    def stop_recording(self):
        """Para gravação e salva arquivo final"""
        self.is_recording = False
        
        if self.audio_data:
            # Salvar sessão completa
            audio_array = np.array(self.audio_data)
            sf.write(AUDIO_FILE, audio_array, SAMPLE_RATE)
            print(f"💾 Áudio salvo em: {AUDIO_FILE}")
            print(f"📏 Duração: {len(audio_array) / SAMPLE_RATE:.1f}s")
            
            # Transcrição final completa
            print("🔄 Processando transcrição final...")
            self.process_final_transcription()
    
    def process_final_transcription(self):
        """Processa transcrição da sessão completa"""
        try:
            segments, info = self.whisper_model.transcribe(
                AUDIO_FILE, 
                language="pt",
                word_timestamps=True
            )
            
            full_text = ""
            segments_data = []
            
            for segment in segments:
                full_text += segment.text + " "
                segments_data.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                })
            
            # Enviar transcrição final
            payload = {
                "transcript": full_text.strip(),
                "segments": segments_data,
                "is_final": True,
                "duration": info.duration,
                "language": info.language
            }
            
            response = requests.post(
                f"{API_URL}/transcript", 
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Transcrição final enviada!")
                print(f"📝 Texto completo ({len(full_text)} chars)")
            
        except Exception as e:
            print(f"❌ Erro na transcrição final: {e}")

def main():
    processor = AudioProcessor()
    
    try:
        processor.start_recording()
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()