import re
import nltk
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

class NLPAnalyzer:
    """Classe para análise de conteúdo textual de apresentações usando NLP"""
    
    def __init__(self, model_manager=None):
        """Inicializa o analisador de NLP com modelos pré-treinados
        
        Args:
            model_manager: Instância do ModelManager para carregar modelos
        """
        # Carregar modelos do ModelManager se fornecido
        if model_manager:
            self.sentiment_analyzer = model_manager.get_model('sentiment_analyzer')
            self.text_classifier = model_manager.get_model('text_classifier')
        else:
            # Importar aqui para evitar dependência circular
            from ..models.nlp_model import load_nlp_models
            self.sentiment_analyzer, self.text_classifier = load_nlp_models(use_qualcomm=True)
            
        # Garantir que os recursos NLTK estejam disponíveis
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        # Stopwords em português
        self.stopwords = set(stopwords.words('portuguese'))
        
        # Palavras técnicas comuns por área
        self.technical_jargon = {
            "tecnologia": [
                "algoritmo", "api", "backend", "frontend", "framework", "deploy",
                "cloud", "servidor", "interface", "dados", "processamento", "rede",
                "protocolo", "sistema", "software", "hardware", "código", "programação",
                "desenvolvimento", "implementação", "arquitetura", "infraestrutura"
            ],
            "negócios": [
                "roi", "kpi", "métricas", "conversão", "pipeline", "funil",
                "monetização", "escalabilidade", "pivot", "disrupção", "inovação",
                "mercado", "segmento", "target", "público-alvo", "estratégia",
                "tático", "operacional", "benchmark", "concorrência", "diferencial"
            ],
            "ciência": [
                "hipótese", "teoria", "experimento", "metodologia", "análise",
                "síntese", "correlação", "causalidade", "variável", "constante",
                "amostra", "população", "significância", "estatística", "probabilidade",
                "distribuição", "desvio", "média", "mediana", "quartil", "percentil"
            ]
        }
        
        # Conectores lógicos para análise de estrutura
        self.logical_connectors = [
            "portanto", "assim", "logo", "então", "por isso", "dessa forma",
            "consequentemente", "por conseguinte", "em vista disso", "diante disso",
            "em primeiro lugar", "em segundo lugar", "por um lado", "por outro lado",
            "além disso", "ademais", "outrossim", "também", "inclusive", "até mesmo",
            "não apenas", "mas também", "tanto", "quanto", "não só", "como também",
            "em contrapartida", "em contraste", "todavia", "contudo", "entretanto",
            "no entanto", "porém", "mas", "apesar de", "embora", "ainda que",
            "mesmo que", "posto que", "conquanto", "se", "caso", "desde que",
            "contanto que", "a menos que", "a não ser que", "salvo se", "exceto se",
            "porque", "visto que", "já que", "uma vez que", "dado que", "considerando que",
            "pois", "porquanto", "como", "na medida em que", "tendo em vista que",
            "para", "a fim de", "com o intuito de", "com o objetivo de", "com a finalidade de",
            "com o propósito de", "de modo a", "de maneira a", "de forma a", "de sorte a",
            "ou", "ou seja", "isto é", "em outras palavras", "a saber", "por exemplo",
            "como por exemplo", "tal como", "assim como", "bem como", "tal qual",
            "em suma", "em síntese", "em resumo", "resumindo", "concluindo",
            "para concluir", "em conclusão", "por fim", "finalmente", "por último"
        ]
    
    def analyze(self, text):
        """Analisa o texto da apresentação para extrair insights sobre o conteúdo
        
        Args:
            text: Texto da apresentação
            
        Returns:
            dict: Resultados da análise contendo métricas de conteúdo
        """
        # Verificar se o texto é válido
        if not text or len(text.strip()) == 0:
            raise ValueError("Texto vazio fornecido para análise")
        
        # Inicializar resultados
        results = {}
        
        # Tokenizar o texto
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())
        
        # Remover stopwords e pontuação
        filtered_words = [word for word in words if word.isalnum() and word not in self.stopwords]
        
        # Calcular estatísticas básicas
        results["word_count"] = len(words)
        results["sentence_count"] = len(sentences)
        results["avg_words_per_sentence"] = float(len(words) / max(1, len(sentences)))
        
        # Analisar complexidade do vocabulário
        unique_words = set(filtered_words)
        results["vocabulary_diversity"] = float(len(unique_words) / max(1, len(filtered_words)))
        
        # Analisar estrutura do texto
        results["structure"] = self._analyze_structure(sentences)
        
        # Analisar clareza
        results["clarity"] = self._analyze_clarity(sentences, filtered_words)
        
        # Analisar uso de jargão técnico
        results["technical_jargon"] = self._analyze_technical_jargon(filtered_words)
        
        # Analisar sentimento
        results["sentiment"] = self._analyze_sentiment(text, sentences)
        
        # Analisar relevância e coerência
        results["relevance"] = self._analyze_relevance(sentences)
        results["coherence"] = self._analyze_coherence(sentences)
        
        # Calcular pontuação geral de conteúdo
        content_score = (
            results["structure"] * 0.25 +
            results["clarity"] * 0.25 +
            (1 - results["technical_jargon"]) * 0.1 +  # Menos jargão é melhor
            results["relevance"] * 0.2 +
            results["coherence"] * 0.2
        )
        
        results["content_score"] = float(content_score)
        
        return results
    
    def _analyze_structure(self, sentences):
        """Analisa a estrutura do texto (introdução, desenvolvimento, conclusão)"""
        if len(sentences) < 3:
            return 0.3  # Texto muito curto para ter boa estrutura
        
        # Verificar presença de conectores lógicos que indicam boa estrutura
        intro_connectors = ["em primeiro lugar", "inicialmente", "primeiramente", "para começar"]
        development_connectors = ["além disso", "ademais", "por um lado", "por outro lado", "em segundo lugar"]
        conclusion_connectors = ["portanto", "assim", "logo", "em conclusão", "finalmente", "por fim"]
        
        # Verificar introdução (primeiras 25% das sentenças)
        intro_section = sentences[:max(1, int(len(sentences) * 0.25))]
        intro_score = 0
        for sentence in intro_section:
            for connector in intro_connectors:
                if connector in sentence.lower():
                    intro_score = 1
                    break
            if intro_score > 0:
                break
        
        # Verificar desenvolvimento (meio 50% das sentenças)
        dev_start = max(1, int(len(sentences) * 0.25))
        dev_end = min(len(sentences) - 1, int(len(sentences) * 0.75))
        dev_section = sentences[dev_start:dev_end]
        dev_score = 0
        for sentence in dev_section:
            for connector in development_connectors:
                if connector in sentence.lower():
                    dev_score = 1
                    break
            if dev_score > 0:
                break
        
        # Verificar conclusão (últimas 25% das sentenças)
        conclusion_section = sentences[max(1, int(len(sentences) * 0.75)):]
        conclusion_score = 0
        for sentence in conclusion_section:
            for connector in conclusion_connectors:
                if connector in sentence.lower():
                    conclusion_score = 1
                    break
            if conclusion_score > 0:
                break
        
        # Calcular pontuação de estrutura
        structure_score = (intro_score * 0.3 + dev_score * 0.4 + conclusion_score * 0.3)
        
        # Ajustar com base no número de parágrafos (estimado por quebras de linha)
        text = " ".join(sentences)
        paragraphs = len(re.findall(r'\n\s*\n', text)) + 1
        paragraph_factor = min(1.0, paragraphs / 3)  # Pelo menos 3 parágrafos para pontuação máxima
        
        return float(structure_score * 0.7 + paragraph_factor * 0.3)
    
    def _analyze_clarity(self, sentences, filtered_words):
        """Analisa a clareza do texto"""
        # Verificar comprimento médio das sentenças (sentenças muito longas reduzem clareza)
        avg_sentence_length = np.mean([len(word_tokenize(s)) for s in sentences])
        sentence_length_score = 1.0 if 10 <= avg_sentence_length <= 20 else max(0.0, 1.0 - abs(avg_sentence_length - 15) / 15)
        
        # Verificar uso de palavras complexas (mais de 3 sílabas)
        complex_words = [w for w in filtered_words if self._count_syllables(w) > 3]
        complex_word_ratio = len(complex_words) / max(1, len(filtered_words))
        complex_word_score = 1.0 - min(1.0, complex_word_ratio * 2)  # Penalizar muitas palavras complexas
        
        # Verificar repetição excessiva de palavras
        word_freq = {}
        for word in filtered_words:
            if len(word) > 3:  # Ignorar palavras muito curtas
                word_freq[word] = word_freq.get(word, 0) + 1
        
        repetition_score = 1.0
        if filtered_words:
            max_freq = max(word_freq.values()) if word_freq else 0
            if max_freq > 5:  # Se alguma palavra aparece mais de 5 vezes
                repetition_score = max(0.0, 1.0 - (max_freq - 5) / 10)
        
        # Combinar pontuações
        clarity_score = (
            sentence_length_score * 0.4 +
            complex_word_score * 0.4 +
            repetition_score * 0.2
        )
        
        return float(clarity_score)
    
    def _analyze_technical_jargon(self, filtered_words):
        """Analisa o uso de jargão técnico no texto"""
        # Contar palavras de jargão técnico
        jargon_count = 0
        all_jargon = []
        for category, terms in self.technical_jargon.items():
            all_jargon.extend(terms)
        
        for word in filtered_words:
            if word.lower() in all_jargon:
                jargon_count += 1
        
        # Calcular proporção de jargão
        jargon_ratio = jargon_count / max(1, len(filtered_words))
        
        return float(jargon_ratio)
    
    def _analyze_sentiment(self, text, sentences):
        """Analisa o sentimento do texto"""
        # Dividir o texto em chunks para análise de sentimento
        # (modelos geralmente têm limite de tokens)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < 500:
                current_chunk += " " + sentence
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Analisar sentimento de cada chunk
        positive_score = 0
        negative_score = 0
        
        for chunk in chunks:
            if not chunk:
                continue
                
            result = self.sentiment_analyzer(chunk)[0]
            if result["label"] == "POSITIVE":
                positive_score += result["score"]
            else:
                negative_score += result["score"]
        
        # Normalizar pontuações
        total_chunks = len(chunks) if chunks else 1
        avg_positive = positive_score / total_chunks
        avg_negative = negative_score / total_chunks
        
        # Calcular pontuação de sentimento (0-1, onde 1 é mais positivo)
        sentiment_score = avg_positive / (avg_positive + avg_negative) if (avg_positive + avg_negative) > 0 else 0.5
        
        return float(sentiment_score)
    
    def _analyze_relevance(self, sentences):
        """Analisa a relevância do conteúdo"""
        # Simplificação: assumir que textos mais longos e com boa estrutura são mais relevantes
        # Em uma implementação real, isso seria feito com um modelo treinado para o domínio específico
        
        # Verificar comprimento do texto
        length_factor = min(1.0, len(sentences) / 20)  # Pelo menos 20 sentenças para pontuação máxima
        
        # Verificar presença de exemplos e dados concretos
        example_indicators = ["por exemplo", "como", "tal como", "ilustrando", "demonstrando"]
        data_indicators = ["dados", "estatísticas", "pesquisa", "estudo", "análise", "percentual", "%"]
        
        example_score = 0
        data_score = 0
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Verificar exemplos
            for indicator in example_indicators:
                if indicator in sentence_lower:
                    example_score = 1
                    break
            
            # Verificar dados
            for indicator in data_indicators:
                if indicator in sentence_lower:
                    data_score = 1
                    break
            
            if example_score and data_score:
                break
        
        # Combinar pontuações
        relevance_score = (
            length_factor * 0.4 +
            example_score * 0.3 +
            data_score * 0.3
        )
        
        return float(relevance_score)
    
    def _analyze_coherence(self, sentences):
        """Analisa a coerência do texto"""
        if len(sentences) < 2:
            return 0.5  # Texto muito curto para avaliar coerência
        
        # Verificar uso de conectores lógicos entre sentenças
        connector_count = 0
        for sentence in sentences:
            for connector in self.logical_connectors:
                if connector in sentence.lower():
                    connector_count += 1
                    break
        
        # Calcular proporção de sentenças com conectores
        connector_ratio = connector_count / len(sentences)
        
        # Verificar progressão temática (simplificação)
        # Em uma implementação real, isso seria feito com análise de tópicos mais sofisticada
        progression_score = 0.7  # Valor padrão razoável
        
        # Combinar pontuações
        coherence_score = connector_ratio * 0.6 + progression_score * 0.4
        
        return float(coherence_score)
    
    def _count_syllables(self, word):
        """Conta o número aproximado de sílabas em uma palavra (para português)"""
        # Simplificação para estimar sílabas em português
        word = word.lower()
        
        # Remover pontuação final se existir
        if not word[-1].isalnum():
            word = word[:-1]
        
        # Contar vogais
        vowels = "aeiouyáàâãéèêíìîóòôõúùû"
        count = 0
        prev_is_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            
            # Contar nova sílaba se for vogal e a anterior não for
            if is_vowel and not prev_is_vowel:
                count += 1
            
            prev_is_vowel = is_vowel
        
        # Ajustar para casos especiais
        if count == 0:
            count = 1  # Garantir pelo menos uma sílaba
        
        return count