import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# Configuração da página
st.set_page_config(
    page_title="Edge Coach Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URLs da API
API_BASE = "http://localhost:8000"

def get_api_data(endpoint, default=None):
    """Helper para chamar API com tratamento de erro"""
    try:
        response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro API {endpoint}: {response.status_code}")
            return default
    except requests.exceptions.RequestException as e:
        st.error(f"API offline: {e}")
        return default

def post_api_data(endpoint, data=None):
    """Helper para POST na API"""
    try:
        response = requests.post(f"{API_BASE}{endpoint}", json=data, timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def format_nervousness_level(score):
    """Formatar nível de nervosismo"""
    if score < 0.3:
        return "🟢 Calmo", "#00ff00"
    elif score < 0.6:
        return "🟡 Moderado", "#ffff00"
    else:
        return "🔴 Nervoso", "#ff0000"

def create_metrics_chart(metrics_data):
    """Criar gráfico de métricas"""
    if not metrics_data:
        return None
    
    df = pd.DataFrame(metrics_data)
    
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Score de Nervosismo', 'Taxa de Piscadas', 'Movimento das Mãos'),
        vertical_spacing=0.1,
        shared_xaxes=True
    )
    
    # Nervosismo
    fig.add_trace(
        go.Scatter(
            y=df['nervousness_score'],
            mode='lines+markers',
            name='Nervosismo',
            line=dict(color='red', width=2)
        ),
        row=1, col=1
    )
    
    # Piscadas
    blink_rates = [m['blink_stats']['blink_rate'] for m in metrics_data]
    fig.add_trace(
        go.Scatter(
            y=blink_rates,
            mode='lines+markers',
            name='Taxa Piscadas',
            line=dict(color='blue', width=2)
        ),
        row=2, col=1
    )
    
    # Movimento das mãos
    hand_movements = [m['raw_metrics']['avg_hand_movement'] for m in metrics_data]
    fig.add_trace(
        go.Scatter(
            y=hand_movements,
            mode='lines+markers',
            name='Movimento Mãos',
            line=dict(color='green', width=2)
        ),
        row=3, col=1
    )
    
    fig.update_layout(height=600, showlegend=False)
    fig.update_yaxes(range=[0, 1], row=1, col=1)
    fig.update_yaxes(range=[0, 1], row=2, col=1)
    
    return fig

# Interface principal
def main():
    st.title("🎯 Edge Coach Dashboard")
    st.markdown("### Análise de Apresentação em Tempo Real")
    
    # Sidebar
    st.sidebar.header("⚙️ Controles")
    
    # Auto-refresh
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=True)
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    # Botões de controle
    if st.sidebar.button("🔄 Atualizar Dados"):
        st.rerun()
    
    if st.sidebar.button("🗑️ Reset Sessão"):
        result = post_api_data("/reset")
        if result:
            st.sidebar.success("Sessão resetada!")
            st.rerun()
    
    # Status da API
    st.sidebar.subheader("📡 Status do Sistema")
    health = get_api_data("/health", {})
    
    if health:
        st.sidebar.success("✅ API Online")
        st.sidebar.metric("Métricas", health.get('metrics_count', 0))
        st.sidebar.metric("Transcrições", health.get('transcripts_count', 0))
    else:
        st.sidebar.error("❌ API Offline")
        st.sidebar.info("Inicie o servidor: `uvicorn src.server:app --reload`")
    
    # Layout principal
    col1, col2 = st.columns([2, 1])
    
    # === COLUNA PRINCIPAL === 
    with col1:
        st.header("📊 Métricas em Tempo Real")
        
        # Obter estatísticas atuais
        stats = get_api_data("/stats", {})
        
        if stats:
            # Métricas principais
            col1a, col1b, col1c = st.columns(3)
            
            with col1a:
                nervousness = stats.get('current_nervousness', 0)
                level, color = format_nervousness_level(nervousness)
                st.metric(
                    "Nervosismo Atual",
                    f"{nervousness:.2f}",
                    delta=level
                )
            
            with col1b:
                st.metric(
                    "Taxa de Piscadas",
                    f"{stats.get('avg_blink_rate', 0):.2f}",
                    delta="Normal" if stats.get('avg_blink_rate', 0) < 0.3 else "Alto"
                )
            
            with col1c:
                st.metric(
                    "Frames Processados",
                    stats.get('total_frames', 0),
                    delta=f"{stats.get('session_duration', 0):.0f}s sessão"
                )
            
            # Gráfico de tendências
            st.subheader("📈 Tendências")
            metrics_data = get_api_data("/metrics?count=100", {}).get('metrics', [])
            
            if metrics_data:
                chart = create_metrics_chart(metrics_data)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("Aguardando dados de vídeo...")
                st.markdown("▶️ Execute: `python src/capture_video.py`")
    
    # === SIDEBAR DIREITA ===
    with col2:
        st.header("🎤 Transcrição")

        transcript_list = get_api_data("/transcript", [])

        if transcript_list:
            # Pega a última transcrição
            last_transcript = transcript_list[-1]
            transcript_text = last_transcript.get('transcript', '')

            st.text_area(
                "Texto capturado:",
                transcript_text,
                height=200,
                disabled=True
            )

            st.metric("Caracteres", len(transcript_text))

            # Obter análise
            analysis_data = get_api_data("/analysis", {})

            if analysis_data:
                if analysis_data.get('quick_analysis'):
                    st.subheader("⚡ Análise Rápida")
                    st.write(analysis_data['quick_analysis'])

                full_analysis = analysis_data.get('full_analysis')
                if full_analysis:
                    st.subheader("🧠 Análise DeepSeek-R1")
                    st.write(full_analysis['analysis'])
                    st.caption(f"Gerada há {time.time() - full_analysis['timestamp']:.0f}s")
                else:
                    st.info("Aguardando áudio...")
                    st.markdown("▶️ Execute: `python src/capture_audio.py`")


            
            # Análise disponível
            analysis_data = get_api_data("/analysis", {})
            
            if analysis_data:
                # Análise rápida
                if analysis_data.get('quick_analysis'):
                    st.subheader("⚡ Análise Rápida")
                    st.write(analysis_data['quick_analysis'])
                
                # Análise completa (DeepSeek)
                full_analysis = analysis_data.get('full_analysis')
                if full_analysis:
                    st.subheader("🧠 Análise DeepSeek-R1")
                    st.write(full_analysis['analysis'])
                    st.caption(f"Gerada há {time.time() - full_analysis['timestamp']:.0f}s")
                
                # Botão para gerar nova análise
                if st.button("🔍 Gerar Nova Análise"):
                    with st.spinner("DeepSeek analisando..."):
                        result = post_api_data("/analysis/generate")
                        if result:
                            st.success("Análise gerada!")
                            st.rerun()
                        else:
                            st.error("Erro ao gerar análise")
        
        else:
            st.info("Aguardando áudio...")
            st.markdown("▶️ Execute: `python src/capture_audio.py`")
    
    # === SEÇÃO INFERIOR ===
    st.header("🎯 Dicas Rule-Based")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📋 Checklist")
        if stats:
            nervousness = stats.get('current_nervousness', 0)
            blink_rate = stats.get('avg_blink_rate', 0)
            
            checks = [
                ("✅" if nervousness < 0.4 else "❌", f"Nervosismo controlado ({nervousness:.2f})"),
                ("✅" if blink_rate < 0.3 else "❌", f"Taxa de piscadas normal ({blink_rate:.2f})"),
                ("✅" if stats.get('total_frames', 0) > 0 else "❌", "Captura de vídeo ativa"),
                ("✅" if transcript_data and len(transcript_data.get('transcript', '')) > 50 else "❌", "Áudio sendo capturado")
            ]
            
            for check, desc in checks:
                st.write(f"{check} {desc}")
    
    with col4:
        st.subheader("💡 Dicas Automáticas")
        
        tips = []
        if stats:
            if stats.get('current_nervousness', 0) > 0.6:
                tips.append("🫁 Respire fundo e fale mais devagar")
            if stats.get('avg_blink_rate', 0) > 0.4:
                tips.append("👁️ Mantenha contato visual, pisque menos")
            if stats.get('avg_hand_movement', 0) > 0.1:
                tips.append("🤲 Controle os gestos das mãos")
            
            if not tips:
                tips.append("🎉 Você está indo bem! Continue assim.")
        
        for tip in tips:
            st.info(tip)
    
    # Footer
    st.markdown("---")
    st.markdown("🤖 **Edge Coach** | Powered by DeepSeek-R1 + MediaPipe + Whisper")

if __name__ == "__main__":
    main()