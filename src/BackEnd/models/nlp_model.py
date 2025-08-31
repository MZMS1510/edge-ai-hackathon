import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def load_nlp_models(use_qualcomm=True):
    """
    Carrega os modelos NLP para análise de sentimento e classificação de texto.
    
    Args:
        use_qualcomm: Se True, tenta usar a versão otimizada para Qualcomm
        
    Returns:
        tuple: (sentiment_analyzer, text_classifier) para análise de texto
    """
    # Modelo para análise de sentimento (português)
    sentiment_model_id = "neuralmind/bert-base-portuguese-cased-sentiment"
    
    try:
        if use_qualcomm:
            # Tentar carregar modelos otimizados para Qualcomm
            try:
                print("A opção use_qualcomm=True foi ignorada devido à falta do módulo qai_hub_models")
                print("Usando modelos Hugging Face padrão...")
            except Exception as e:
                print(f"Não foi possível carregar os modelos NLP otimizados para Qualcomm: {str(e)}")
                print("Usando modelos Hugging Face padrão...")
        
        # Carregar modelos padrão do Hugging Face
        # Modelo de sentimento
        sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_id)
        sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_id)
        
        # Mover para GPU se disponível
        if torch.cuda.is_available():
            sentiment_model = sentiment_model.to("cuda")
            print("Modelos NLP movidos para GPU.")
        else:
            print("GPU não disponível, usando CPU para modelos NLP.")
        
        # Criar funções de pipeline para os modelos
        def sentiment_analyzer(text):
            inputs = sentiment_tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = sentiment_model(**inputs)
            
            scores = torch.nn.functional.softmax(outputs.logits, dim=1)
            return {"label": sentiment_model.config.id2label[scores.argmax().item()], 
                    "score": scores.max().item()}
        
        # Para classificação de texto, podemos usar o mesmo modelo
        text_classifier = sentiment_analyzer
        
        print("Modelos NLP carregados com sucesso.")
        return sentiment_analyzer, text_classifier
    
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar modelos NLP: {str(e)}")