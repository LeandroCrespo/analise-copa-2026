"""
Dashboard Streamlit - Sistema de Análise Copa 2026
Versão otimizada para Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
import sys
import os

# Adicionar diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importar modelo otimizado
try:
    sys.path.append(os.path.dirname(__file__))
    from model_optimized import predict_match_optimized, get_best_conservative_scores
except:
    st.error("Erro ao importar modelo. Verifique se model_optimized.py está no diretório.")

# Configuração da página
st.set_page_config(
    page_title="Análise Copa 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título
st.title("⚽ Sistema de Análise - Copa do Mundo 2026")
st.markdown("---")

# Função para conectar ao Neon
@st.cache_resource
def get_connection():
    """Conecta ao Neon PostgreSQL usando secrets"""
    try:
        # Tentar usar secrets do Streamlit Cloud
        if hasattr(st, 'secrets') and 'neon' in st.secrets:
            conn_string = st.secrets['neon']['connection_string']
        else:
            # Fallback para desenvolvimento local
            st.warning("⚠️ Usando configuração local. Configure secrets no Streamlit Cloud.")
            return None
        
        conn = psycopg2.connect(conn_string)
        return conn
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao banco: {e}")
        return None

# Função para buscar dados
@st.cache_data(ttl=3600)
def get_teams():
    """Busca lista de times"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        df = pd.read_sql("SELECT id, name FROM teams ORDER BY name", conn)
        return df
    except Exception as e:
        st.error(f"Erro ao buscar times: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_team_stats(team_id):
    """Busca estatísticas de um time"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        # Buscar jogos do time
        query = f"""
        SELECT 
            date,
            CASE 
                WHEN home_team_id = {team_id} THEN home_goals
                ELSE away_goals
            END as goals_scored,
            CASE 
                WHEN home_team_id = {team_id} THEN away_goals
                ELSE home_goals
            END as goals_conceded,
            CASE 
                WHEN (home_team_id = {team_id} AND home_goals > away_goals) OR
                     (away_team_id = {team_id} AND away_goals > home_goals) THEN 'W'
                WHEN home_goals = away_goals THEN 'D'
                ELSE 'L'
            END as result
        FROM matches
        WHERE home_team_id = {team_id} OR away_team_id = {team_id}
        ORDER BY date DESC
        LIMIT 50
        """
        
        df = pd.read_sql(query, conn)
        
        if len(df) == 0:
            return None
        
        # Calcular estatísticas
        stats = {
            'avg_goals_scored': df['goals_scored'].mean(),
            'avg_goals_conceded': df['goals_conceded'].mean(),
            'win_rate': (df['result'] == 'W').sum() / len(df),
            'strength': 50 + (df['goals_scored'].mean() - df['goals_conceded'].mean()) * 10,
            'recent_form': (df.head(10)['result'] == 'W').sum() / 10,
            'total_games': len(df)
        }
        
        return stats
    
    except Exception as e:
        st.error(f"Erro ao buscar estatísticas: {e}")
        return None

# Sidebar
with st.sidebar:
    st.header("📊 Navegação")
    page = st.radio(
        "Escolha uma página:",
        ["🏠 Home", "🎯 Previsões", "📊 Estatísticas", "ℹ️ Sobre"]
    )

# Página Home
if page == "🏠 Home":
    st.header("🏠 Bem-vindo!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Jogos no Banco", "7.623")
        st.caption("Dados de 2015-2026")
    
    with col2:
        st.metric("🎯 Precisão", "57.6%")
        st.caption("Resultado correto")
    
    with col3:
        st.metric("⚽ Seleções", "223")
        st.caption("Todas as principais")
    
    st.markdown("---")
    
    st.subheader("🎯 Estratégia de Placares")
    st.info("""
    **Placares Conservadores (65.1% dos jogos):**
    - 1x0, 1x1, 0x0, 2x0, 0x1
    - 2x1, 1x2, 0x2, 2x2
    
    **Por quê?**
    - Maximiza chance de pontuar
    - Reduz risco de errar completamente
    - Baseado em análise de 7.623 jogos reais
    """)
    
    st.subheader("🔄 Atualização Automática")
    st.success("""
    ✅ Sistema atualiza automaticamente todos os dias às 03:00
    
    - Jogos de março (amistosos) serão capturados
    - Eliminatórias atualizadas
    - Durante a Copa, resultados diários
    """)

# Página Previsões
elif page == "🎯 Previsões":
    st.header("🎯 Gerar Previsões")
    
    teams_df = get_teams()
    
    if len(teams_df) == 0:
        st.error("❌ Não foi possível carregar times. Verifique a conexão com o banco.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            home_team = st.selectbox(
                "🏠 Time Mandante",
                options=teams_df['name'].tolist(),
                key="home"
            )
        
        with col2:
            away_team = st.selectbox(
                "✈️ Time Visitante",
                options=teams_df['name'].tolist(),
                key="away"
            )
        
        if st.button("🎯 Gerar Previsão", type="primary"):
            if home_team == away_team:
                st.error("⚠️ Selecione times diferentes!")
            else:
                with st.spinner("Calculando previsão..."):
                    # Buscar IDs
                    home_id = teams_df[teams_df['name'] == home_team]['id'].values[0]
                    away_id = teams_df[teams_df['name'] == away_team]['id'].values[0]
                    
                    # Buscar estatísticas
                    home_stats = get_team_stats(home_id)
                    away_stats = get_team_stats(away_id)
                    
                    if home_stats and away_stats:
                        # Gerar previsão
                        prediction = predict_match_optimized(home_stats, away_stats)
                        
                        st.success("✅ Previsão Gerada!")
                        
                        # Placar previsto
                        st.markdown("### 🎯 Placar Previsto")
                        col1, col2, col3 = st.columns([2, 1, 2])
                        
                        with col1:
                            st.markdown(f"### {home_team}")
                        
                        with col2:
                            st.markdown(f"## {prediction['home_goals']} x {prediction['away_goals']}")
                        
                        with col3:
                            st.markdown(f"### {away_team}")
                        
                        # Probabilidades
                        st.markdown("### 📊 Probabilidades")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("🏠 Vitória Mandante", f"{prediction['prob_home_win']:.1%}")
                        
                        with col2:
                            st.metric("🤝 Empate", f"{prediction['prob_draw']:.1%}")
                        
                        with col3:
                            st.metric("✈️ Vitória Visitante", f"{prediction['prob_away_win']:.1%}")
                        
                        # Detalhes
                        with st.expander("📈 Detalhes da Previsão"):
                            st.write(f"**Probabilidade do placar exato:** {prediction['prob_exact']:.1%}")
                            st.write(f"**Pontuação esperada:** {prediction['expected_points']:.2f} pts")
                            st.write(f"**Estratégia:** {prediction['strategy']}")
                            
                            st.markdown("**Estatísticas dos times:**")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**{home_team}:**")
                                st.write(f"- Gols por jogo: {home_stats['avg_goals_scored']:.2f}")
                                st.write(f"- Força: {home_stats['strength']:.1f}/100")
                                st.write(f"- Jogos analisados: {home_stats['total_games']}")
                            
                            with col2:
                                st.write(f"**{away_team}:**")
                                st.write(f"- Gols por jogo: {away_stats['avg_goals_scored']:.2f}")
                                st.write(f"- Força: {away_stats['strength']:.1f}/100")
                                st.write(f"- Jogos analisados: {away_stats['total_games']}")
                    else:
                        st.error("❌ Não há dados suficientes para gerar previsão.")

# Página Estatísticas
elif page == "📊 Estatísticas":
    st.header("📊 Estatísticas das Seleções")
    
    teams_df = get_teams()
    
    if len(teams_df) > 0:
        selected_team = st.selectbox(
            "Selecione uma seleção:",
            options=teams_df['name'].tolist()
        )
        
        if selected_team:
            team_id = teams_df[teams_df['name'] == selected_team]['id'].values[0]
            stats = get_team_stats(team_id)
            
            if stats:
                st.subheader(f"📊 {selected_team}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("⚽ Gols/Jogo", f"{stats['avg_goals_scored']:.2f}")
                
                with col2:
                    st.metric("🛡️ Gols Sofridos", f"{stats['avg_goals_conceded']:.2f}")
                
                with col3:
                    st.metric("💪 Força", f"{stats['strength']:.1f}/100")
                
                with col4:
                    st.metric("🏆 Taxa Vitória", f"{stats['win_rate']:.1%}")
                
                st.info(f"📊 Análise baseada em {stats['total_games']} jogos")
            else:
                st.warning("⚠️ Não há dados suficientes para esta seleção.")

# Página Sobre
elif page == "ℹ️ Sobre":
    st.header("ℹ️ Sobre o Sistema")
    
    st.markdown("""
    ## 🏆 Sistema de Análise Copa 2026
    
    ### 📊 Dados
    - **7.623 jogos reais** (2015-2026)
    - **223 seleções** cadastradas
    - **11 anos** de histórico
    
    ### 🎯 Precisão Validada
    - **57.6%** de acerto em resultado
    - **8.4%** de acerto em placar exato
    - Testado com **2.287 jogos**
    
    ### 🔄 Atualização Automática
    - Roda diariamente às 03:00
    - Captura jogos novos automaticamente
    - Zero trabalho manual
    
    ### 📈 Metodologia
    - Distribuição de Poisson
    - Regressão à média
    - Simulação de Monte Carlo
    - Placares conservadores (65.1% dos jogos)
    
    ### 🔗 Links
    - [GitHub](https://github.com/LeandroCrespo/analise-copa-2026)
    - [Neon PostgreSQL](https://neon.tech)
    
    ---
    
    **Desenvolvido com metodologia científica para maximizar sua pontuação no Bolão! 🏆⚽📊**
    """)

# Footer
st.markdown("---")
st.caption("Sistema de Análise Copa 2026 | Dados atualizados automaticamente")
