import requests
import json
import time
from typing import Dict, Any, Optional

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="deepseek-r1:8b"):
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/generate"
    
    def test_connection(self):
        """Testa conexão com Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7):
        """Gera resposta usando DeepSeek-R1"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(
                self.api_url, 
                json=payload, 
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Erro na resposta")
            else:
                return f"Erro HTTP: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "❌ Timeout - DeepSeek demorou muito para responder"
        except requests.exceptions.ConnectionError:
            return "❌ Conexão falhou - Verifique se Ollama está rodando"
        except Exception as e:
            return f"❌ Erro: {str(e)}"
    
    def analyze_presentation(self, transcript: str, metrics: Optional[Dict] = None):
        """Análise específica para apresentações usando DeepSeek-R1"""
        
        # Preparar contexto com métricas se disponível
        metrics_context = ""
        if metrics:
            nervousness = metrics.get('nervousness_score', 0)
            blink_rate = metrics.get('blink_stats', {}).get('blink_rate', 0)
            hand_movement = metrics.get('raw_metrics', {}).get('avg_hand_movement', 0)
            
            metrics_context = f"""
Métricas de nervosismo detectadas:
- Score de nervosismo: {nervousness:.2f}/1.0
- Taxa de piscadas: {blink_rate:.2f}
- Movimento das mãos: {hand_movement:.3f}
"""
        
        prompt = f"""Você é um coach especialista em apresentações. Analise esta apresentação e forneça feedback construtivo.

TRANSCRIÇÃO DA APRESENTAÇÃO:
"{transcript}"

{metrics_context}

INSTRUÇÕES:
1. Analise o conteúdo, linguagem e estrutura da apresentação
2. Se houver métricas de nervosismo, considere-as na análise
3. Dê exatamente 3 dicas práticas e específicas de melhoria
4. Seja direto, construtivo e motivador
5. Responda em português brasileiro

FORMATO DA RESPOSTA:
🎯 **DICA 1**: [título]
[explicação prática de 1-2 linhas]

🎯 **DICA 2**: [título]  
[explicação prática de 1-2 linhas]

🎯 **DICA 3**: [título]
[explicação prática de 1-2 linhas]

💡 **PONTO POSITIVO**: [algo que está funcionando bem]
"""

        return self.generate_response(prompt, max_tokens=400, temperature=0.8)
    
    def analyze_transcript_only(self, transcript: str):
        """Análise rápida apenas do texto"""
        if not transcript or len(transcript.strip()) < 10:
            return "❌ Transcrição muito curta para análise. Fale mais sobre o tema!"
        
        prompt = f"""Analise esta fala de apresentação e dê 3 dicas rápidas:

TEXTO: "{transcript}"

Responda em formato simples:
1. [dica sobre conteúdo]
2. [dica sobre linguagem] 
3. [dica sobre estrutura]

Seja direto e prático."""

        return self.generate_response(prompt, max_tokens=200, temperature=0.7)
    
    def get_topic_suggestions(self, transcript: str):
        """Sugere tópicos baseado na transcrição"""
        prompt = f"""Com base nesta fala: "{transcript}"

Sugira 3 tópicos relacionados que a pessoa poderia abordar para enriquecer a apresentação:

1. [tópico 1]
2. [tópico 2] 
3. [tópico 3]

Seja específico e relevante ao contexto."""

        return self.generate_response(prompt, max_tokens=150)

# Instância global
ollama_client = OllamaClient()

def get_coaching_feedback(transcript: str, metrics: Optional[Dict] = None):
    """Função de conveniência para análise completa"""
    if not ollama_client.test_connection():
        return "❌ Ollama não está rodando. Execute: ollama serve"
    
    return ollama_client.analyze_presentation(transcript, metrics)

def quick_text_analysis(transcript: str):
    """Análise rápida apenas do texto"""
    if not ollama_client.test_connection():
        return "❌ Ollama offline"
    
    return ollama_client.analyze_transcript_only(transcript)