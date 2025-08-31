import os
import tempfile
import numpy as np
import librosa
import torch

class SpeechAnalyzer:
    """Classe para análise de fala usando modelos de IA da Qualcomm"""
    
    def __init__(self, model_manager=None):
        """Inicializa o analisador de fala com modelos pré-treinados
        
        Args:
            model_manager: Instância do ModelManager para carregar modelos
        """
        # Carregar modelos do ModelManager se fornecido
        if model_manager:
            self.model = model_manager.get_model('whisper_model')
        else:
            # Importar aqui para evitar dependência circular
            from ..models.whisper_model import load_whisper_model
            self.model = load_whisper_model(model_size="tiny", use_qualcomm=True)
        
        # Palavras de preenchimento comuns em português
        self.filler_words = [
            "é", "tipo", "então", "sabe", "entende", "né", "tá", "assim", 
            "bom", "bem", "olha", "veja", "digamos", "digamos assim", "certo"
        ]
        
        # Configurações para análise de áudio
        self.sample_rate = 16000
    
    def analyze(self, audio_file):
        """Analisa um arquivo de áudio para extrair insights sobre a fala
        
        Args:
            audio_file: Arquivo de áudio da apresentação
            
        Returns:
            dict: Resultados da análise contendo métricas de fala
        """
        # Salvar o arquivo temporariamente
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            audio_file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Carregar e processar o áudio
            audio_data, _ = librosa.load(temp_path, sr=self.sample_rate, mono=True)
            
            # Transcrever o áudio
            transcription = self._transcribe_audio(audio_data)
            
            # Analisar características da fala
            speech_metrics = self._analyze_speech_metrics(audio_data, transcription)
            
            # Adicionar a transcrição aos resultados
            speech_metrics["transcription"] = transcription
            
            return speech_metrics
            
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def _transcribe_audio(self, audio_data):
        """Transcreve o áudio usando o modelo Whisper"""
        # Usar diretamente o modelo whisper para transcrição
        # O modelo whisper aceita diretamente o array de áudio
        result = self.model.transcribe(audio_data)
        
        # O resultado já contém o texto transcrito
        transcription = result["text"]
        
        return transcription
    
    def _analyze_speech_metrics(self, audio_data, transcription):
        """Analisa métricas de fala a partir do áudio e da transcrição"""
        # Inicializar resultados
        results = {}
        
        # Calcular clareza da fala (baseado em energia e contraste espectral)
        spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=self.sample_rate)
        results["clarity"] = float(np.mean(spectral_contrast) / 20 + 0.5)  # Normalizar para 0-1
        
        # Calcular ritmo da fala
        words = transcription.split()
        duration = len(audio_data) / self.sample_rate
        words_per_minute = len(words) / (duration / 60)
        
        # Normalizar palavras por minuto para uma escala de 0-1
        # Considerando 120-160 WPM como ideal (0.7-0.9 na escala)
        if words_per_minute < 80:
            results["pace"] = max(0.0, words_per_minute / 120)
        elif words_per_minute > 200:
            results["pace"] = max(0.0, 2 - (words_per_minute / 200))
        else:
            # Escala ideal entre 120-160 WPM
            results["pace"] = 0.7 + ((min(words_per_minute, 160) - 120) / 40) * 0.2
        
        results["words_per_minute"] = float(words_per_minute)
        
        # Detectar palavras de preenchimento
        filler_count = 0
        for word in words:
            if word.lower() in self.filler_words:
                filler_count += 1
        
        results["filler_words_count"] = filler_count
        results["filler_words_frequency"] = float(filler_count / max(1, len(words)))
        
        # Detectar pausas e sua distribuição
        # Usando envelope de energia para detectar silêncios
        energy = librosa.feature.rms(y=audio_data)[0]
        silence_threshold = np.mean(energy) * 0.5
        silence_frames = energy < silence_threshold
        
        # Converter frames para segundos
        frame_length = 2048
        hop_length = 512
        silence_indices = np.where(silence_frames)[0] * hop_length / self.sample_rate
        
        # Identificar pausas (silêncios maiores que 0.5 segundos)
        pauses = []
        if len(silence_indices) > 0:
            # Agrupar índices consecutivos
            pause_start = silence_indices[0]
            for i in range(1, len(silence_indices)):
                if silence_indices[i] - silence_indices[i-1] > 0.1:  # Nova pausa
                    pause_duration = silence_indices[i-1] - pause_start
                    if pause_duration > 0.5:  # Apenas pausas significativas
                        pauses.append(pause_duration)
                    pause_start = silence_indices[i]
            
            # Última pausa
            pause_duration = silence_indices[-1] - pause_start
            if pause_duration > 0.5:
                pauses.append(pause_duration)
        
        results["pauses_count"] = len(pauses)
        results["pauses_avg_duration"] = float(np.mean(pauses)) if pauses else 0.0
        results["pauses_frequency"] = float(len(pauses) / (duration / 60))  # Pausas por minuto
        
        # Variação de tom (pitch)
        pitches, magnitudes = librosa.piptrack(y=audio_data, sr=self.sample_rate)
        pitch_values = []
        for i in range(pitches.shape[1]):
            index = magnitudes[:, i].argmax()
            pitch = pitches[index, i]
            if pitch > 0:  # Filtrar valores zero
                pitch_values.append(pitch)
        
        if pitch_values:
            pitch_std = np.std(pitch_values)
            pitch_range = np.max(pitch_values) - np.min(pitch_values)
            
            # Normalizar variação de tom para 0-1
            # Uma boa variação está entre 30-80 Hz
            results["pitch_variation"] = min(1.0, pitch_std / 50)
        else:
            results["pitch_variation"] = 0.0
        
        # Calcular pontuação geral de engajamento
        # Baseado em uma combinação ponderada das métricas
        engagement_score = (
            results["clarity"] * 0.3 +
            results["pace"] * 0.2 +
            (1 - results["filler_words_frequency"]) * 0.2 +
            min(1.0, results["pauses_frequency"] / 10) * 0.1 +
            results["pitch_variation"] * 0.2
        )
        
        results["engagement_score"] = float(engagement_score)
        
        return results