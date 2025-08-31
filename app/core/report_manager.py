#!/usr/bin/env python3
"""
Report Manager - Gerenciador de Relatórios de Análise
Gerencia histórico de análises e relatórios finais
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path

class ReportManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.output_dir = self.base_dir / "OUTPUT"
        self.reports_dir = self.output_dir / "reports"
        self.history_file = self.output_dir / "analysis_history.json"
        
        # Criar estrutura de pastas
        self.setup_directories()
        
        self.history = self.load_history()
    
    def setup_directories(self):
        """Cria estrutura de pastas para organização"""
        try:
            # Criar pasta OUTPUT
            self.output_dir.mkdir(exist_ok=True)
            
            # Criar subpastas
            self.reports_dir.mkdir(exist_ok=True)
            
            # Criar arquivo README
            readme_file = self.output_dir / "README.md"
            if not readme_file.exists():
                with open(readme_file, 'w', encoding='utf-8') as f:
                    f.write("""# OUTPUT - Relatórios de Análise

Esta pasta contém todos os relatórios e dados gerados pelo Communication Coach.

## Estrutura:
- `reports/` - Relatórios individuais de cada análise
- `analysis_history.json` - Histórico completo de todas as análises
- `README.md` - Este arquivo

## Formato dos Relatórios:
- `analysis_report_YYYYMMDD_HHMMSS.json` - Relatório detalhado de cada sessão
- Contém métricas, feedback, recomendações e progresso

## Backup:
- Faça backup desta pasta regularmente
- Os relatórios são únicos e não podem ser regenerados
""")
            
            print(f"✅ Estrutura de pastas criada: {self.output_dir}")
            
        except Exception as e:
            print(f"❌ Erro ao criar estrutura de pastas: {e}")
    
    def load_history(self):
        """Carrega histórico de análises"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Erro ao carregar histórico: {e}")
        
        return {
            'analyses': [],
            'total_analyses': 0,
            'last_updated': None,
            'created_date': datetime.now().isoformat()
        }
    
    def save_history(self):
        """Salva histórico de análises"""
        try:
            self.history['last_updated'] = datetime.now().isoformat()
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erro ao salvar histórico: {e}")
    
    def add_report(self, report_data):
        """Adiciona novo relatório ao histórico"""
        try:
            # Criar entrada do relatório
            analysis_entry = {
                'id': f"analysis_{len(self.history['analyses']) + 1}",
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().strftime("%d/%m/%Y"),
                'time': datetime.now().strftime("%H:%M"),
                'duration_minutes': report_data.get('session_info', {}).get('duration_minutes', 0),
                'overall_score': report_data.get('average_scores', {}).get('overall', 0),
                'performance_level': report_data.get('performance_level', 'N/A'),
                'total_frames': report_data.get('session_info', {}).get('total_frames', 0),
                'report_file': f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                'summary': {
                    'posture': report_data.get('average_scores', {}).get('posture', 0),
                    'gesture': report_data.get('average_scores', {}).get('gesture', 0),
                    'eye_contact': report_data.get('average_scores', {}).get('eye_contact', 0)
                },
                'strengths_count': len(report_data.get('strengths', [])),
                'weaknesses_count': len(report_data.get('weaknesses', [])),
                'recommendations_count': len(report_data.get('recommendations', []))
            }
            
            # Adicionar ao histórico
            self.history['analyses'].append(analysis_entry)
            self.history['total_analyses'] = len(self.history['analyses'])
            
            # Salvar histórico
            self.save_history()
            
            # Salvar relatório completo
            report_file_path = self.reports_dir / analysis_entry['report_file']
            with open(report_file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Relatório salvo: {report_file_path}")
            return analysis_entry
            
        except Exception as e:
            print(f"❌ Erro ao adicionar relatório: {e}")
            return None
    
    def get_all_reports(self):
        """Retorna todos os relatórios do histórico"""
        return self.history.get('analyses', [])
    
    def get_report_by_id(self, report_id):
        """Retorna relatório específico por ID"""
        for analysis in self.history['analyses']:
            if analysis['id'] == report_id:
                report_file = self.reports_dir / analysis['report_file']
                if report_file.exists():
                    try:
                        with open(report_file, 'r', encoding='utf-8') as f:
                            return json.load(f)
                    except Exception as e:
                        print(f"❌ Erro ao carregar relatório: {e}")
                break
        return None
    
    def get_latest_report(self):
        """Retorna o relatório mais recente"""
        if self.history['analyses']:
            latest = self.history['analyses'][-1]
            return self.get_report_by_id(latest['id'])
        return None
    
    def get_statistics(self):
        """Retorna estatísticas gerais"""
        if not self.history['analyses']:
            return {
                'total_analyses': 0,
                'average_score': 0,
                'best_score': 0,
                'total_duration': 0,
                'performance_distribution': {}
            }
        
        scores = [analysis['overall_score'] for analysis in self.history['analyses']]
        durations = [analysis['duration_minutes'] for analysis in self.history['analyses']]
        performance_levels = [analysis['performance_level'] for analysis in self.history['analyses']]
        
        # Contar distribuição de performance
        performance_dist = {}
        for level in performance_levels:
            performance_dist[level] = performance_dist.get(level, 0) + 1
        
        return {
            'total_analyses': len(self.history['analyses']),
            'average_score': round(sum(scores) / len(scores), 1),
            'best_score': max(scores),
            'total_duration': round(sum(durations), 1),
            'performance_distribution': performance_dist,
            'last_analysis': self.history['analyses'][-1]['date'] if self.history['analyses'] else None
        }
    
    def delete_report(self, report_id):
        """Deleta relatório específico"""
        for i, analysis in enumerate(self.history['analyses']):
            if analysis['id'] == report_id:
                # Deletar arquivo do relatório
                report_file = self.reports_dir / analysis['report_file']
                if report_file.exists():
                    report_file.unlink()
                
                # Remover do histórico
                self.history['analyses'].pop(i)
                self.history['total_analyses'] = len(self.history['analyses'])
                self.save_history()
                
                print(f"✅ Relatório {report_id} deletado")
                return True
        
        return False
    
    def export_history(self, format='json'):
        """Exporta histórico completo"""
        if format == 'json':
            export_file = self.output_dir / f"history_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            return str(export_file)
        return None
    
    def cleanup_old_reports(self, days=30):
        """Remove relatórios antigos (mais de X dias)"""
        try:
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            removed_count = 0
            
            for analysis in self.history['analyses'][:]:  # Cópia para não modificar durante iteração
                analysis_timestamp = datetime.fromisoformat(analysis['timestamp']).timestamp()
                if analysis_timestamp < cutoff_date:
                    # Deletar arquivo
                    report_file = self.reports_dir / analysis['report_file']
                    if report_file.exists():
                        report_file.unlink()
                    
                    # Remover do histórico
                    self.history['analyses'].remove(analysis)
                    removed_count += 1
            
            if removed_count > 0:
                self.history['total_analyses'] = len(self.history['analyses'])
                self.save_history()
                print(f"🧹 {removed_count} relatórios antigos removidos")
            
            return removed_count
            
        except Exception as e:
            print(f"❌ Erro ao limpar relatórios antigos: {e}")
            return 0
    
    def get_storage_info(self):
        """Retorna informações sobre uso de armazenamento"""
        try:
            total_size = 0
            report_count = 0
            
            for report_file in self.reports_dir.glob("*.json"):
                total_size += report_file.stat().st_size
                report_count += 1
            
            history_size = self.history_file.stat().st_size if self.history_file.exists() else 0
            
            return {
                'total_reports': report_count,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'history_size_kb': round(history_size / 1024, 2),
                'output_dir': str(self.output_dir)
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter informações de armazenamento: {e}")
            return {}

# Instância global
report_manager = ReportManager()
