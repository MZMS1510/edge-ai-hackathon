from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import time
from collections import deque
import threading
from .ollama_client import get_coaching_feedback, quick_text_analysis


# Modelos de dados
class MetricsData(BaseModel):
    timestamp: float
    nervousness_score: float
    blink_detected: bool
    blink_stats: Dict
    hand_movement: float
    head_movement: float
    hands_detected: int
    face_detected: int
    raw_metrics: Dict

class TranscriptData(BaseModel):
    transcript: str
    timestamp: Optional[float] = None
    duration: Optional[float] = None
    segments: Optional[List[Dict]] = None
    is_final: Optional[bool] = False
    language: Optional[str] = "pt"

# Storage em memória
class DataStore:
    def __init__(self, max_size=1000):
        self.metrics_history = deque(maxlen=max_size)
        self.transcripts = []
        self.current_session = {
            'start_time': time.time(),
            'last_update': time.time(),
            'total_frames': 0,
            'analysis_cache': {}
        }
        self.lock = threading.RLock()
    
    def add_metrics(self, metrics: MetricsData):
        with self.lock:
            self.metrics_history.append(metrics.dict())
            self.current_session['last_update'] = time.time()
            self.current_session['total_frames'] += 1
    
    def add_transcript(self, transcript: TranscriptData):
        with self.lock:
            transcript_dict = transcript.dict()
            transcript_dict['received_at'] = time.time()
            self.transcripts.append(transcript_dict)
            
            # Trigger análise se for final
            if transcript.is_final:
                self.trigger_final_analysis(transcript.transcript)
    
    def get_latest_metrics(self, count=50):
        with self.lock:
            return list(self.metrics_history)[-count:]
    
    def get_current_stats(self):
        with self.lock:
            if not self.metrics_history:
                return {}
            
            recent_metrics = list(self.metrics_history)[-30:]  # últimos 30 frames
            
            nervousness_scores = [m['nervousness_score'] for m in recent_metrics]
            blink_rates = [m['blink_stats']['blink_rate'] for m in recent_metrics]
            hand_movements = [m['raw_metrics']['avg_hand_movement'] for m in recent_metrics]
            
            return {
                'current_nervousness': nervousness_scores[-1] if nervousness_scores else 0,
                'avg_nervousness': sum(nervousness_scores) / len(nervousness_scores) if nervousness_scores else 0,
                'avg_blink_rate': sum(blink_rates) / len(blink_rates) if blink_rates else 0,
                'avg_hand_movement': sum(hand_movements) / len(hand_movements) if hand_movements else 0,
                'total_frames': self.current_session['total_frames'],
                'session_duration': time.time() - self.current_session['start_time'],
                'last_update': self.current_session['last_update']
            }
    
    def get_full_transcript(self):
        with self.lock:
            return " ".join([t['transcript'] for t in self.transcripts if t.get('transcript')])
    
    def trigger_final_analysis(self, transcript):
        """Trigger análise com DeepSeek em thread separada"""
        def analyze():
            try:
                recent_metrics = self.get_latest_metrics(100)
                latest_metrics = recent_metrics[-1] if recent_metrics else None
                
                analysis = get_coaching_feedback(transcript, latest_metrics)
                
                with self.lock:
                    self.current_session['analysis_cache']['full_analysis'] = {
                        'analysis': analysis,
                        'timestamp': time.time(),
                        'transcript_length': len(transcript)
                    }
                
                print(f"✅ Análise DeepSeek concluída: {len(analysis)} chars")
                
            except Exception as e:
                print(f"❌ Erro na análise: {e}")
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def reset_session(self):
        with self.lock:
            self.metrics_history.clear()
            self.transcripts.clear()
            self.current_session = {
                'start_time': time.time(),
                'last_update': time.time(),
                'total_frames': 0,
                'analysis_cache': {}
            }

# Instância global
data_store = DataStore()

# FastAPI App
app = FastAPI(title="Edge Coach API", version="1.0.0")

# CORS para Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Edge Coach API", 
        "status": "running",
        "endpoints": ["/metrics", "/transcript", "/stats", "/analysis"]
    }

@app.post("/metrics")
async def receive_metrics(metrics: MetricsData):
    """Recebe métricas de vídeo"""
    try:
        data_store.add_metrics(metrics)
        return {"status": "success", "timestamp": metrics.timestamp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcript")
async def receive_transcript(transcript: TranscriptData):
    """Recebe transcrição de áudio"""
    try:
        data_store.add_transcript(transcript)
        return {"status": "success", "length": len(transcript.transcript)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Retorna estatísticas atuais"""
    try:
        stats = data_store.get_current_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics(count: int = 50):
    """Retorna histórico de métricas"""
    try:
        metrics = data_store.get_latest_metrics(count)
        return {"metrics": metrics, "count": len(metrics)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transcript")
async def get_transcript():
    """Retorna transcrição completa"""
    try:
        full_text = data_store.get_full_transcript()
        return {
            "transcript": full_text,
            "length": len(full_text),
            "segments": data_store.transcripts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis")
async def get_analysis():
    """Retorna análises disponíveis"""
    try:
        cache = data_store.current_session['analysis_cache']
        transcript = data_store.get_full_transcript()
        
        # Análise rápida se não houver cache
        quick_analysis = None
        if transcript and len(transcript) > 20:
            quick_analysis = quick_text_analysis(transcript[:500])
        
        return {
            "full_analysis": cache.get('full_analysis'),
            "quick_analysis": quick_analysis,
            "transcript_available": len(transcript) > 0,
            "transcript_length": len(transcript)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analysis/generate")
async def generate_analysis():
    """Force geração de nova análise"""
    try:
        transcript = data_store.get_full_transcript()
        
        if not transcript or len(transcript) < 20:
            raise HTTPException(status_code=400, detail="Transcrição insuficiente")
        
        # Análise com métricas mais recentes
        recent_metrics = data_store.get_latest_metrics(50)
        latest_metrics = recent_metrics[-1] if recent_metrics else None
        
        analysis = get_coaching_feedback(transcript, latest_metrics)
        
        # Salvar no cache
        with data_store.lock:
            data_store.current_session['analysis_cache']['manual_analysis'] = {
                'analysis': analysis,
                'timestamp': time.time(),
                'transcript_length': len(transcript)
            }
        
        return {"analysis": analysis, "status": "generated"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset_session():
    """Reset da sessão atual"""
    try:
        data_store.reset_session()
        return {"status": "session reset", "timestamp": time.time()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "metrics_count": len(data_store.metrics_history),
        "transcripts_count": len(data_store.transcripts)
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando Edge Coach API...")
    print("📊 Dashboard: http://localhost:8501")
    print("🔧 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)