#!/usr/bin/env python3
"""
Sistema de Análise e Treinamento de Dados de Postura
Analisa dados coletados e ajusta thresholds para melhor precisão
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
from datetime import datetime

class PostureAnalyzerTrainer:
    def __init__(self):
        self.data_dir = "training_data"
        self.model_dir = "trained_models"
        self.ensure_directories()
        
    def ensure_directories(self):
        """Cria diretórios necessários"""
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
    
    def load_training_data(self):
        """Carrega todos os dados de treinamento"""
        all_data = []
        
        for posture_type in ["good_posture", "bad_posture", "neutral_posture"]:
            folder_path = os.path.join(self.data_dir, posture_type)
            if not os.path.exists(folder_path):
                continue
                
            files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
            
            for file in files:
                filepath = os.path.join(folder_path, file)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        
                        for sample in data['samples']:
                            sample_data = {
                                'posture_type': posture_type,
                                'metrics': sample['metrics'],
                                'landmarks': sample['landmarks']
                            }
                            all_data.append(sample_data)
                            
                except Exception as e:
                    print(f"Erro ao carregar {filepath}: {e}")
        
        return all_data
    
    def prepare_features(self, data):
        """Prepara features para treinamento"""
        features = []
        labels = []
        
        for sample in data:
            metrics = sample['metrics']
            
            # Features baseadas nas métricas
            feature_vector = [
                metrics['shoulder_angle'],
                metrics['hip_angle'],
                metrics['spine_alignment'],
                metrics['shoulder_width'],
                metrics['hip_width'],
            ]
            
            features.append(feature_vector)
            
            # Labels numéricos
            if sample['posture_type'] == 'good_posture':
                labels.append(2)  # Boa
            elif sample['posture_type'] == 'neutral_posture':
                labels.append(1)  # Neutra
            else:
                labels.append(0)  # Ruim
        
        return np.array(features), np.array(labels)
    
    def train_model(self, features, labels):
        """Treina um modelo de classificação"""
        # Dividir dados em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Treinar modelo Random Forest
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Avaliar modelo
        y_pred = model.predict(X_test)
        
        # Gerar relatório
        report = classification_report(y_test, y_pred, 
                                     target_names=['Ruim', 'Neutra', 'Boa'])
        
        return model, X_test, y_test, y_pred, report
    
    def analyze_thresholds(self, data):
        """Analisa dados para sugerir thresholds otimizados"""
        print("🔍 Analisando dados para otimizar thresholds...")
        
        # Separar dados por tipo
        good_data = [s for s in data if s['posture_type'] == 'good_posture']
        bad_data = [s for s in data if s['posture_type'] == 'bad_posture']
        neutral_data = [s for s in data if s['posture_type'] == 'neutral_posture']
        
        if not good_data or not bad_data:
            print("❌ Dados insuficientes para análise")
            return None
        
        # Calcular estatísticas
        metrics = ['shoulder_angle', 'hip_angle', 'spine_alignment']
        threshold_suggestions = {}
        
        for metric in metrics:
            good_values = [s['metrics'][metric] for s in good_data]
            bad_values = [s['metrics'][metric] for s in bad_data]
            neutral_values = [s['metrics'][metric] for s in neutral_data]
            
            # Calcular percentis
            good_p95 = np.percentile(good_values, 95)
            bad_p5 = np.percentile(bad_values, 5)
            neutral_p50 = np.percentile(neutral_values, 50) if neutral_values else (good_p95 + bad_p5) / 2
            
            # Sugerir threshold baseado na separação entre boas e ruins
            suggested_threshold = (good_p95 + bad_p5) / 2
            
            threshold_suggestions[metric] = {
                'suggested_threshold': suggested_threshold,
                'good_p95': good_p95,
                'bad_p5': bad_p5,
                'neutral_p50': neutral_p50,
                'good_mean': np.mean(good_values),
                'bad_mean': np.mean(bad_values),
                'good_std': np.std(good_values),
                'bad_std': np.std(bad_values)
            }
        
        return threshold_suggestions
    
    def generate_visualizations(self, data, model_results=None):
        """Gera visualizações dos dados"""
        print("📊 Gerando visualizações...")
        
        # Preparar dados para visualização
        good_data = [s for s in data if s['posture_type'] == 'good_posture']
        bad_data = [s for s in data if s['posture_type'] == 'bad_posture']
        neutral_data = [s for s in data if s['posture_type'] == 'neutral_posture']
        
        metrics = ['shoulder_angle', 'hip_angle', 'spine_alignment']
        
        # Criar subplots
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Distribuição de Métricas por Tipo de Postura', fontsize=16)
        
        for i, metric in enumerate(metrics):
            ax = axes[i]
            
            # Extrair valores
            good_values = [s['metrics'][metric] for s in good_data]
            bad_values = [s['metrics'][metric] for s in bad_data]
            neutral_values = [s['metrics'][metric] for s in neutral_data]
            
            # Criar histogramas
            if good_values:
                ax.hist(good_values, alpha=0.7, label='Boa', bins=20, color='green')
            if bad_values:
                ax.hist(bad_values, alpha=0.7, label='Ruim', bins=20, color='red')
            if neutral_values:
                ax.hist(neutral_values, alpha=0.7, label='Neutra', bins=20, color='orange')
            
            ax.set_xlabel(metric.replace('_', ' ').title())
            ax.set_ylabel('Frequência')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Salvar visualização
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_path = os.path.join(self.model_dir, f"posture_analysis_{timestamp}.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Visualização salva em: {plot_path}")
        
        # Gerar matriz de correlação se houver dados suficientes
        if len(data) > 10:
            self.generate_correlation_matrix(data)
    
    def generate_correlation_matrix(self, data):
        """Gera matriz de correlação entre métricas"""
        metrics = ['shoulder_angle', 'hip_angle', 'spine_alignment', 'shoulder_width', 'hip_width']
        
        # Preparar dados
        feature_data = []
        for sample in data:
            row = [sample['metrics'][metric] for metric in metrics]
            feature_data.append(row)
        
        feature_array = np.array(feature_data)
        
        # Calcular correlação
        corr_matrix = np.corrcoef(feature_array.T)
        
        # Criar heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, 
                   annot=True, 
                   cmap='coolwarm', 
                   xticklabels=metrics,
                   yticklabels=metrics,
                   center=0)
        plt.title('Matriz de Correlação entre Métricas de Postura')
        plt.tight_layout()
        
        # Salvar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        corr_path = os.path.join(self.model_dir, f"correlation_matrix_{timestamp}.png")
        plt.savefig(corr_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Matriz de correlação salva em: {corr_path}")
    
    def save_optimized_config(self, threshold_suggestions):
        """Salva configuração otimizada"""
        if not threshold_suggestions:
            return
        
        # Converter para formato do analysis_config.json
        optimized_config = {
            "posture": {
                "shoulder_threshold": threshold_suggestions['shoulder_angle']['suggested_threshold'],
                "hip_threshold": threshold_suggestions['hip_angle']['suggested_threshold'],
                "spine_threshold": threshold_suggestions['spine_alignment']['suggested_threshold'],
                "variation_factor": 1.0,
                "min_score": 15,
                "max_score": 95
            },
            "gesture": {
                "movement_threshold_low": 0.015,
                "movement_threshold_high": 0.035,
                "base_score_no_hands": 35,
                "variation_factor": 1.0,
                "min_score": 20,
                "max_score": 90
            },
            "eye_contact": {
                "center_tolerance": 0.25,
                "movement_factor": 1.5,
                "variation_factor": 1.0,
                "min_score": 25,
                "max_score": 90
            },
            "feedback_thresholds": {
                "posture": {
                    "poor": 45,
                    "good": 75
                },
                "gesture": {
                    "poor": 30,
                    "good": 60
                },
                "eye_contact": {
                    "poor": 40,
                    "good": 70
                }
            },
            "smoothing": {
                "factor": 0.6,
                "history_size": 15
            },
            "weights": {
                "posture": 0.35,
                "gesture": 0.3,
                "eye_contact": 0.35
            }
        }
        
        # Salvar configuração otimizada
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_path = os.path.join(self.model_dir, f"optimized_config_{timestamp}.json")
        
        with open(config_path, 'w') as f:
            json.dump(optimized_config, f, indent=2)
        
        print(f"💾 Configuração otimizada salva em: {config_path}")
        
        # Salvar relatório detalhado
        report_path = os.path.join(self.model_dir, f"threshold_analysis_{timestamp}.json")
        with open(report_path, 'w') as f:
            json.dump(threshold_suggestions, f, indent=2)
        
        print(f"📋 Relatório detalhado salvo em: {report_path}")
    
    def run_full_analysis(self):
        """Executa análise completa dos dados"""
        print("🚀 Iniciando análise completa dos dados de treinamento...")
        
        # Carregar dados
        data = self.load_training_data()
        
        if not data:
            print("❌ Nenhum dado de treinamento encontrado")
            print("💡 Execute primeiro o coletor de dados: python training_data_collector.py")
            return
        
        print(f"✅ Carregados {len(data)} amostras")
        
        # Preparar features
        features, labels = self.prepare_features(data)
        print(f"📊 Features preparadas: {features.shape}")
        
        # Treinar modelo
        print("🤖 Treinando modelo de classificação...")
        model, X_test, y_test, y_pred, report = self.train_model(features, labels)
        
        print("\n📈 Relatório de Classificação:")
        print(report)
        
        # Analisar thresholds
        print("\n🔍 Analisando thresholds...")
        threshold_suggestions = self.analyze_thresholds(data)
        
        if threshold_suggestions:
            print("\n💡 Sugestões de Thresholds Otimizados:")
            for metric, info in threshold_suggestions.items():
                print(f"  {metric}: {info['suggested_threshold']:.4f}")
                print(f"    Boa (p95): {info['good_p95']:.4f}")
                print(f"    Ruim (p5): {info['bad_p5']:.4f}")
                print()
        
        # Gerar visualizações
        self.generate_visualizations(data, model_results=(X_test, y_test, y_pred))
        
        # Salvar configuração otimizada
        self.save_optimized_config(threshold_suggestions)
        
        print("\n🎉 Análise completa finalizada!")
        print("📁 Verifique os arquivos gerados na pasta 'trained_models'")

if __name__ == "__main__":
    trainer = PostureAnalyzerTrainer()
    trainer.run_full_analysis()
