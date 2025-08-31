import os
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar serviços e gerenciador de modelos
from models.model_manager import ModelManager
from services.speech_analyzer import SpeechAnalyzer
from services.visual_analyzer import VisualAnalyzer
from services.nlp_analyzer import NLPAnalyzer

app = Flask(__name__)
CORS(app)

# Inicializar gerenciador de modelos
print("Inicializando ModelManager e carregando modelos de IA...")
model_manager = ModelManager(use_qualcomm=True)
model_manager.download_nltk_resources()
models = model_manager.load_models()

# Inicializar analisadores com os modelos carregados
print("Inicializando analisadores...")
speech_analyzer = SpeechAnalyzer(model_manager=model_manager)
visual_analyzer = VisualAnalyzer(model_manager=model_manager)
nlp_analyzer = NLPAnalyzer(model_manager=model_manager)
print("Sistema inicializado e pronto para análise de apresentações.")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "PitchPerfect AI API está funcionando!"})

@app.route('/api/analyze/speech', methods=['POST'])
def analyze_speech():
    """Endpoint para análise de fala"""
    if 'audio' not in request.files:
        return jsonify({"error": "Arquivo de áudio não fornecido"}), 400
    
    audio_file = request.files['audio']
    
    try:
        results = speech_analyzer.analyze(audio_file)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze/visual', methods=['POST'])
def analyze_visual():
    """Endpoint para análise visual"""
    if 'video' not in request.files:
        return jsonify({"error": "Arquivo de vídeo não fornecido"}), 400
    
    video_file = request.files['video']
    
    try:
        results = visual_analyzer.analyze(video_file)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """Endpoint para análise de texto/conteúdo"""
    data = request.json
    
    if not data or 'text' not in data:
        return jsonify({"error": "Texto não fornecido"}), 400
    
    try:
        results = nlp_analyzer.analyze(data['text'])
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze/presentation', methods=['POST'])
def analyze_presentation():
    """Endpoint para análise completa da apresentação"""
    if not request.files:
        return jsonify({"error": "Nenhum arquivo fornecido"}), 400
    
    results = {}
    
    # Análise de áudio se disponível
    if 'audio' in request.files:
        try:
            results['speech'] = speech_analyzer.analyze(request.files['audio'])
        except Exception as e:
            results['speech'] = {"error": str(e)}
    
    # Análise de vídeo se disponível
    if 'video' in request.files:
        try:
            results['visual'] = visual_analyzer.analyze(request.files['video'])
        except Exception as e:
            results['visual'] = {"error": str(e)}
    
    # Análise de texto se disponível
    if request.form and 'text' in request.form:
        try:
            results['content'] = nlp_analyzer.analyze(request.form['text'])
        except Exception as e:
            results['content'] = {"error": str(e)}
    
    # Gerar insights combinados
    if results:
        results['insights'] = generate_combined_insights(results)
    
    return jsonify(results)

def generate_combined_insights(analysis_results):
    """Gera insights combinados a partir dos resultados de análise individuais"""
    insights = {
        "summary": "Análise de apresentação completa",
        "strengths": [],
        "areas_for_improvement": [],
        "recommendations": []
    }
    
    # Processar resultados de fala
    if 'speech' in analysis_results and 'error' not in analysis_results['speech']:
        speech_data = analysis_results['speech']
        
        # Adicionar pontos fortes baseados na fala
        if speech_data.get('clarity', 0) > 0.7:
            insights['strengths'].append("Boa clareza de fala")
        if speech_data.get('pace', 0) > 0.6 and speech_data.get('pace', 0) < 0.8:
            insights['strengths'].append("Ritmo de fala adequado")
        
        # Adicionar áreas para melhoria baseadas na fala
        if speech_data.get('clarity', 0) < 0.5:
            insights['areas_for_improvement'].append("Melhorar a clareza da fala")
            insights['recommendations'].append("Pratique a articulação e reduza a velocidade em partes complexas")
        if speech_data.get('filler_words_frequency', 0) > 0.1:
            insights['areas_for_improvement'].append("Reduzir o uso de palavras de preenchimento")
            insights['recommendations'].append("Esteja consciente de palavras como 'hum', 'é', 'tipo' e faça pausas silenciosas em vez disso")
    
    # Processar resultados visuais
    if 'visual' in analysis_results and 'error' not in analysis_results['visual']:
        visual_data = analysis_results['visual']
        
        # Adicionar pontos fortes baseados no visual
        if visual_data.get('eye_contact', 0) > 0.7:
            insights['strengths'].append("Bom contato visual")
        if visual_data.get('posture', 0) > 0.7:
            insights['strengths'].append("Boa postura corporal")
        
        # Adicionar áreas para melhoria baseadas no visual
        if visual_data.get('eye_contact', 0) < 0.5:
            insights['areas_for_improvement'].append("Melhorar o contato visual com a audiência")
            insights['recommendations'].append("Olhe para diferentes partes da sala e mantenha contato visual por 3-5 segundos")
        if visual_data.get('gestures', 0) < 0.4:
            insights['areas_for_improvement'].append("Usar mais gestos para enfatizar pontos")
            insights['recommendations'].append("Incorpore gestos naturais que complementem suas palavras")
    
    # Processar resultados de conteúdo
    if 'content' in analysis_results and 'error' not in analysis_results['content']:
        content_data = analysis_results['content']
        
        # Adicionar pontos fortes baseados no conteúdo
        if content_data.get('structure', 0) > 0.7:
            insights['strengths'].append("Boa estrutura de conteúdo")
        if content_data.get('relevance', 0) > 0.8:
            insights['strengths'].append("Conteúdo altamente relevante")
        
        # Adicionar áreas para melhoria baseadas no conteúdo
        if content_data.get('structure', 0) < 0.5:
            insights['areas_for_improvement'].append("Melhorar a estrutura e organização do conteúdo")
            insights['recommendations'].append("Use uma estrutura clara com introdução, pontos principais e conclusão")
        if content_data.get('technical_jargon', 0) > 0.7:
            insights['areas_for_improvement'].append("Reduzir o uso de jargão técnico")
            insights['recommendations'].append("Explique termos técnicos ou substitua por linguagem mais acessível")
    
    # Adicionar recomendações gerais se não houver específicas
    if not insights['recommendations']:
        insights['recommendations'] = [
            "Continue praticando suas apresentações",
            "Grave-se para auto-avaliação",
            "Peça feedback de colegas confiáveis"
        ]
    
    return insights

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)