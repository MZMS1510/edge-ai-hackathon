import requests
import time
import json
from typing import Dict, List, Optional
from ollama_client import get_coaching_feedback, quick_text_analysis

class PresentationAnalyzer:
    def __init__(self, api_base="http://localhost:8000"):
        self.api_base = api_base
        
    def get_current_data(self):
        """Obtém dados atuais do servidor"""
        try:
            stats_response = requests.get(f"{self.api_base}/stats")
            transcript_response = requests.get(f"{self.api_base}/transcript")
            metrics_response = requests.get(f"{self.api_base}/metrics?count=100")
            
            return {
                'stats': stats_response.json() if stats_response.status_code == 200 else {},
                'transcript': transcript_response.json() if transcript_response.status_code == 200 else {},
                'metrics': metrics_response.json() if metrics_response.status_code == 200 else {}
            }
        except Exception as e:
            print(f"Erro ao obter dados: {e}")
            return None
    
    def analyze_nervousness_patterns(self, metrics_data: List[Dict]) -> Dict:
        """Analisa padrões de nervosismo"""
        if not metrics_data:
            return {}
        
        nervousness_scores = [m.get('nervousness_score', 0) for m in metrics_data]
        blink_rates = [m.get('blink_stats', {}).get('blink_rate', 0) for m in metrics_data]
        hand_movements = [m.get('raw_metrics', {}).get('avg_hand_movement', 0) for m in metrics_data]
        
        # Calcular tendências
        if len(nervousness_scores) > 1:
            recent_avg = sum(nervousness_scores[-10:]) / min(10, len(nervousness_scores))
            overall_avg = sum(nervousness_scores) / len(nervousness_scores)
            trend = "melhorando" if recent_avg < overall_avg else "piorando"
        else:
            recent_avg = nervousness_scores[0] if nervousness_scores else 0
            overall_avg = recent_avg
            trend = "estável"
        
        # Detectar picos
        peaks = [i for i, score in enumerate(nervousness_scores) if score > 0.7]
        
        return {
            'overall_average': overall_avg,
            'recent_average': recent_avg,
            'trend': trend,
            'peak_moments': peaks,
            'high_blink_periods': [i for i, rate in enumerate(blink_rates) if rate > 20],
            'excessive_movement_periods': [i for i, mov in enumerate(hand_movements) if mov > 0.5]
        }
    
    def analyze_speech_patterns(self, transcript_data: Dict) -> Dict:
        """Analisa padrões de fala"""
        if not transcript_data or 'text' not in transcript_data:
            return {'error': 'Nenhuma transcrição disponível'}
        
        text = transcript_data['text']
        words = text.split()
        
        if not words:
            return {'error': 'Texto vazio'}
        
        # Análise básica
        word_count = len(words)
        char_count = len(text)
        sentence_count = len([s for s in text.split('.') if s.strip()])
        
        # Detectar palavras de preenchimento
        filler_words = ['né', 'então', 'tipo', 'assim', 'bem', 'eh', 'ah', 'um', 'uma']
        filler_count = sum(1 for word in words if word.lower().strip('.,!?') in filler_words)
        filler_rate = filler_count / word_count if word_count > 0 else 0
        
        # Calcular velocidade de fala (estimativa)
        duration = transcript_data.get('duration', 60)  # fallback 60 segundos
        wpm = (word_count / duration) * 60 if duration > 0 else 0
        
        # Análise de repetição
        word_freq = {}
        for word in words:
            clean_word = word.lower().strip('.,!?')
            if len(clean_word) > 3:  # ignora palavras muito pequenas
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        repeated_words = {word: count for word, count in word_freq.items() if count > 2}
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'average_sentence_length': word_count / sentence_count if sentence_count > 0 else 0,
            'filler_word_count': filler_count,
            'filler_rate': filler_rate,
            'estimated_wpm': wpm,
            'repeated_words': repeated_words,
            'readability_score': self._calculate_readability(words, sentence_count)
        }
    
    def _calculate_readability(self, words: List[str], sentence_count: int) -> float:
        """Calcula um score simples de legibilidade"""
        if not words or sentence_count == 0:
            return 0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        avg_sentence_length = len(words) / sentence_count
        
        # Score simples: palavras menores e frases mais curtas = mais legível
        # Normalizado entre 0-100
        readability = max(0, min(100, 100 - (avg_word_length * 5) - (avg_sentence_length * 2)))
        return readability
    
    def generate_insights(self, data: Dict) -> Dict:
        """Gera insights combinados dos dados"""
        insights = {
            'overall_score': 0,
            'strengths': [],
            'areas_for_improvement': [],
            'specific_recommendations': [],
            'nervousness_analysis': {},
            'speech_analysis': {},
            'ai_feedback': ''
        }
        
        # Análise de nervosismo
        if 'metrics' in data and data['metrics']:
            nervousness_analysis = self.analyze_nervousness_patterns(data['metrics'])
            insights['nervousness_analysis'] = nervousness_analysis
            
            # Pontuação baseada no nervosismo
            nervousness_score = nervousness_analysis.get('recent_average', 0)
            if nervousness_score < 0.3:
                insights['strengths'].append("Aparenta estar calmo e confiante")
                insights['overall_score'] += 30
            elif nervousness_score < 0.6:
                insights['areas_for_improvement'].append("Nervosismo moderado detectado")
                insights['overall_score'] += 15
            else:
                insights['areas_for_improvement'].append("Alto nível de nervosismo")
                insights['specific_recommendations'].append("Pratique técnicas de respiração antes de apresentar")
        
        # Análise de fala
        if 'transcript' in data and data['transcript']:
            speech_analysis = self.analyze_speech_patterns(data['transcript'])
            insights['speech_analysis'] = speech_analysis
            
            if 'error' not in speech_analysis:
                # Pontuação baseada na fala
                filler_rate = speech_analysis.get('filler_rate', 0)
                wpm = speech_analysis.get('estimated_wpm', 120)
                
                if filler_rate < 0.05:
                    insights['strengths'].append("Discurso fluido com poucas palavras de preenchimento")
                    insights['overall_score'] += 20
                elif filler_rate > 0.15:
                    insights['areas_for_improvement'].append("Muitas palavras de preenchimento")
                    insights['specific_recommendations'].append("Pratique pausas silenciosas em vez de 'eh', 'né', etc.")
                
                if 140 <= wpm <= 180:
                    insights['strengths'].append("Ritmo de fala adequado")
                    insights['overall_score'] += 20
                elif wpm < 120:
                    insights['specific_recommendations'].append("Tente falar um pouco mais rápido")
                elif wpm > 200:
                    insights['specific_recommendations'].append("Diminua o ritmo da fala para melhor compreensão")
                
                readability = speech_analysis.get('readability_score', 50)
                if readability > 70:
                    insights['strengths'].append("Linguagem clara e acessível")
                    insights['overall_score'] += 15
        
        # Normalizar pontuação final (0-100)
        insights['overall_score'] = min(100, max(0, insights['overall_score']))
        
        # Obter feedback da IA (DeepSeek-R1)
        if 'transcript' in data and data['transcript'] and data['transcript'].get('text'):
            try:
                ai_feedback = get_coaching_feedback(
                    data['transcript']['text'], 
                    insights['nervousness_analysis']
                )
                insights['ai_feedback'] = ai_feedback
            except Exception as e:
                insights['ai_feedback'] = f"Erro ao obter feedback da IA: {e}"
        
        return insights
    
    def get_real_time_feedback(self) -> Dict:
        """Obtém feedback em tempo real"""
        data = self.get_current_data()
        if not data:
            return {'error': 'Não foi possível obter dados do servidor'}
        
        return self.generate_insights(data)
    
    def export_analysis_report(self, filename: Optional[str] = None) -> str:
        """Exporta relatório completo de análise"""
        if not filename:
            timestamp = int(time.time())
            filename = f"presentation_analysis_{timestamp}.json"
        
        data = self.get_current_data()
        if not data:
            return "Erro: Não foi possível obter dados"
        
        insights = self.generate_insights(data)
        
        report = {
            'timestamp': time.time(),
            'raw_data': data,
            'analysis': insights,
            'summary': {
                'overall_score': insights['overall_score'],
                'main_strengths': insights['strengths'][:3],
                'top_recommendations': insights['specific_recommendations'][:3]
            }
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            return f"Relatório salvo em: {filename}"
        except Exception as e:
            return f"Erro ao salvar relatório: {e}"

# Função utilitária para usar diretamente
def analyze_presentation():
    """Função principal para análise rápida"""
    analyzer = PresentationAnalyzer()
    feedback = analyzer.get_real_time_feedback()
    
    print("=== ANÁLISE DA APRESENTAÇÃO ===")
    print(f"Score Geral: {feedback.get('overall_score', 0)}/100")
    print("\nPontos Fortes:")
    for strength in feedback.get('strengths', []):
        print(f"✅ {strength}")
    
    print("\nÁreas de Melhoria:")
    for improvement in feedback.get('areas_for_improvement', []):
        print(f"⚠️ {improvement}")
    
    print("\nRecomendações:")
    for rec in feedback.get('specific_recommendations', []):
        print(f"💡 {rec}")
    
    if feedback.get('ai_feedback'):
        print(f"\nFeedback DeepSeek-R1:\n{feedback['ai_feedback']}")
    
    return feedback

if __name__ == "__main__":
    analyze_presentation()