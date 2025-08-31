/**
 * History Manager - Gerenciador de Histórico de Análises
 * Componente JavaScript para gerenciar histórico de relatórios
 */

class HistoryManager {
    constructor() {
        this.currentReport = null;
        this.historyData = [];
        this.init();
    }
    
    async init() {
        await this.loadHistory();
        this.setupEventListeners();
        this.renderHistory();
    }
    
    async loadHistory() {
        try {
            const response = await fetch('/api/history');
            const data = await response.json();
            this.historyData = data.analyses || [];
            this.renderStatistics(data.statistics);
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
        }
    }
    
    setupEventListeners() {
        // Botão para mostrar/ocultar histórico
        const historyToggle = document.getElementById('history-toggle');
        if (historyToggle) {
            historyToggle.addEventListener('click', () => {
                this.toggleHistoryPanel();
            });
        }
        
        // Botão para fechar histórico
        const historyClose = document.getElementById('history-close');
        if (historyClose) {
            historyClose.addEventListener('click', () => {
                this.closeHistoryPanel();
            });
        }
        
        // Botão para exportar histórico
        const exportBtn = document.getElementById('export-history');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportHistory();
            });
        }
        
        // Fechar histórico ao clicar fora do painel
        const historyPanel = document.getElementById('history-panel');
        if (historyPanel) {
            historyPanel.addEventListener('click', (e) => {
                if (e.target === historyPanel) {
                    this.closeHistoryPanel();
                }
            });
        }
        
        // Fechar histórico com tecla ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeHistoryPanel();
            }
        });
    }
    
    renderStatistics(stats) {
        const statsContainer = document.getElementById('history-statistics');
        if (!statsContainer) return;
        
        statsContainer.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${stats.total_analyses}</div>
                    <div class="stat-label">Total de Análises</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.average_score}</div>
                    <div class="stat-label">Score Médio</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.best_score}</div>
                    <div class="stat-label">Melhor Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.total_duration}min</div>
                    <div class="stat-label">Tempo Total</div>
                </div>
            </div>
            <div class="performance-distribution">
                <h4>Distribuição de Performance</h4>
                <div class="distribution-bars">
                    ${this.renderPerformanceBars(stats.performance_distribution)}
                </div>
            </div>
        `;
    }
    
    renderPerformanceBars(distribution) {
        const total = Object.values(distribution).reduce((a, b) => a + b, 0);
        if (total === 0) return '<p>Nenhuma análise realizada</p>';
        
        return Object.entries(distribution).map(([level, count]) => {
            const percentage = ((count / total) * 100).toFixed(1);
            const color = this.getPerformanceColor(level);
            
            return `
                <div class="distribution-item">
                    <div class="level-label">${level}</div>
                    <div class="level-bar">
                        <div class="level-fill" style="width: ${percentage}%; background: ${color}"></div>
                    </div>
                    <div class="level-count">${count} (${percentage}%)</div>
                </div>
            `;
        }).join('');
    }
    
    getPerformanceColor(level) {
        const colors = {
            'Excelente': '#28a745',
            'Bom': '#17a2b8',
            'Regular': '#ffc107',
            'Precisa Melhorar': '#dc3545'
        };
        return colors[level] || '#6c757d';
    }
    
    renderHistory() {
        const historyContainer = document.getElementById('history-list');
        if (!historyContainer) return;
        
        if (this.historyData.length === 0) {
            historyContainer.innerHTML = `
                <div class="empty-history">
                    <div class="empty-icon">📊</div>
                    <h3>Nenhuma análise realizada</h3>
                    <p>Realize sua primeira análise para ver o histórico aqui</p>
                </div>
            `;
            return;
        }
        
        historyContainer.innerHTML = this.historyData.map(analysis => `
            <div class="history-item" data-id="${analysis.id}">
                <div class="history-header">
                    <div class="history-date">
                        <div class="date">${analysis.date}</div>
                        <div class="time">${analysis.time}</div>
                    </div>
                    <div class="history-score">
                        <div class="score-value ${this.getScoreClass(analysis.overall_score)}">
                            ${analysis.overall_score}
                        </div>
                        <div class="score-label">Score Geral</div>
                    </div>
                    <div class="history-level">
                        <span class="level-badge ${this.getLevelClass(analysis.performance_level)}">
                            ${analysis.performance_level}
                        </span>
                    </div>
                </div>
                <div class="history-details">
                    <div class="detail-item">
                        <span class="detail-label">Duração:</span>
                        <span class="detail-value">${analysis.duration_minutes} min</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Frames:</span>
                        <span class="detail-value">${analysis.total_frames}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Pontos Fortes:</span>
                        <span class="detail-value">${analysis.strengths_count}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Melhorias:</span>
                        <span class="detail-value">${analysis.weaknesses_count}</span>
                    </div>
                </div>
                <div class="history-actions">
                    <button class="btn-view" onclick="historyManager.viewReport('${analysis.id}')">
                        👁️ Ver Detalhes
                    </button>
                    <button class="btn-delete" onclick="historyManager.deleteReport('${analysis.id}')">
                        🗑️ Deletar
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    getScoreClass(score) {
        if (score >= 85) return 'excellent';
        if (score >= 70) return 'good';
        if (score >= 55) return 'regular';
        return 'needs-improvement';
    }
    
    getLevelClass(level) {
        return level.toLowerCase().replace(' ', '-');
    }
    
    async viewReport(reportId) {
        try {
            const response = await fetch(`/api/report/${reportId}`);
            const report = await response.json();
            
            if (report.error) {
                this.showError(report.error);
                return;
            }
            
            this.showReportModal(report);
        } catch (error) {
            console.error('Erro ao carregar relatório:', error);
            this.showError('Erro ao carregar relatório');
        }
    }
    
    showReportModal(report) {
        const modal = document.createElement('div');
        modal.className = 'report-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>📊 Relatório de Análise</h2>
                    <button class="modal-close" onclick="this.closest('.report-modal').remove()">×</button>
                </div>
                <div class="modal-body">
                    ${this.renderReportContent(report)}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Fechar modal ao clicar fora
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }
    
    renderReportContent(report) {
        return `
            <div class="report-summary">
                <div class="summary-metrics">
                    <div class="metric">
                        <div class="metric-value">${report.average_scores.overall}</div>
                        <div class="metric-label">Score Geral</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${report.average_scores.posture}</div>
                        <div class="metric-label">Postura</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${report.average_scores.gesture}</div>
                        <div class="metric-label">Gestos</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${report.average_scores.eye_contact}</div>
                        <div class="metric-label">Contato Visual</div>
                    </div>
                </div>
            </div>
            
            <div class="report-sections">
                <div class="section">
                    <h3>✅ Pontos Fortes</h3>
                    <ul>
                        ${report.strengths.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="section">
                    <h3>⚠️ Áreas de Melhoria</h3>
                    <ul>
                        ${report.weaknesses.map(w => `<li>${w}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="section">
                    <h3>💡 Recomendações</h3>
                    <ul>
                        ${report.recommendations.map(r => `<li>${r}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }
    
    async deleteReport(reportId) {
        if (!confirm('Tem certeza que deseja deletar este relatório?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/report/${reportId}`, {
                method: 'DELETE'
            });
            const result = await response.json();
            
            if (result.success) {
                await this.loadHistory();
                this.renderHistory();
                this.showSuccess('Relatório deletado com sucesso');
            } else {
                this.showError(result.error || 'Erro ao deletar relatório');
            }
        } catch (error) {
            console.error('Erro ao deletar relatório:', error);
            this.showError('Erro ao deletar relatório');
        }
    }
    
    async exportHistory() {
        try {
            const response = await fetch('/api/export-history');
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('Histórico exportado com sucesso');
            } else {
                this.showError(result.error || 'Erro ao exportar histórico');
            }
        } catch (error) {
            console.error('Erro ao exportar histórico:', error);
            this.showError('Erro ao exportar histórico');
        }
    }
    
    toggleHistoryPanel() {
        const panel = document.getElementById('history-panel');
        const floatButton = document.getElementById('history-close-float');
        if (panel) {
            panel.classList.add('active');
            if (floatButton) {
                floatButton.classList.add('active');
            }
        }
    }
    
    closeHistoryPanel() {
        const panel = document.getElementById('history-panel');
        const floatButton = document.getElementById('history-close-float');
        if (panel) {
            panel.classList.remove('active');
            if (floatButton) {
                floatButton.classList.remove('active');
            }
        }
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.historyManager = new HistoryManager();
});
