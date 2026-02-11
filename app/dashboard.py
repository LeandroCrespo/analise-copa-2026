"""
Dashboard Streamlit para Sistema de Análise Copa 2026
"""

import sys
sys.path.append('../src')

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from utils import DatabaseManager
from data_processing import DataProcessor
from adaptive_model import AdaptiveMatchPredictor, AdaptiveGroupPredictor, AdaptivePodiumPredictor
from live_updater import LiveUpdater

# Configuração da página
st.set_page_config(
    page_title="Análise Copa 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar componentes
@st.cache_resource
def init_components():
    """Inicializar componentes do sistema"""
    db = DatabaseManager()
    processor = DataProcessor()
    match_predictor = AdaptiveMatchPredictor()
    group_predictor = AdaptiveGroupPredictor()
    podium_predictor = AdaptivePodiumPredictor()
    updater = LiveUpdater()
    
    return db, processor, match_predictor, group_predictor, podium_predictor, updater

db, processor, match_predictor, group_predictor, podium_predictor, updater = init_components()

# Sidebar
st.sidebar.title("⚽ Análise Copa 2026")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Menu Principal",
    ["🏠 Home", "📊 Análise de Seleções", "🎯 Previsão de Jogos", 
     "🏆 Classificação dos Grupos", "🥇 Previsão de Pódio", 
     "🔄 Atualizar Dados", "📈 Estatísticas"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Sistema Adaptativo**\n\n"
    "As previsões são atualizadas automaticamente conforme "
    "os jogos acontecem, considerando os resultados reais."
)

# ==================== HOME ====================
if menu == "🏠 Home":
    st.title("⚽ Sistema de Análise e Previsão - Copa 2026")
    
    st.markdown("""
    ## Bem-vindo ao Sistema Inteligente de Palpites!
    
    Este sistema utiliza **modelos estatísticos adaptativos** para gerar palpites otimizados 
    para o Bolão Copa do Mundo 2026.
    
    ### 🎯 Funcionalidades
    
    - **Previsão de Placares**: Palpites de placar exato para todos os 128 jogos
    - **Classificação dos Grupos**: Previsão de 1º e 2º colocados de cada grupo
    - **Previsão de Pódio**: Campeão, Vice-Campeão e 3º Lugar
    - **Atualização Automática**: Sistema se adapta conforme jogos acontecem
    - **Análise Detalhada**: Estatísticas completas de cada seleção
    
    ### 🔄 Sistema Adaptativo
    
    O grande diferencial deste sistema é sua **capacidade de adaptação**:
    
    - ✅ Monitora resultados reais da Copa 2026
    - ✅ Recalcula previsões baseado em performance atual
    - ✅ Pondera histórico geral (40%) + forma na Copa (60%)
    - ✅ Atualiza automaticamente o banco de dados
    
    ### 📊 Metodologia
    
    - **Regressão à Média**: Análise de tendências históricas
    - **Distribuição de Poisson**: Modelagem probabilística de gols
    - **Simulação de Monte Carlo**: Cálculo de probabilidades complexas
    - **Machine Learning**: Ajuste dinâmico de pesos
    """)
    
    # Status do sistema
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        teams_count = len(db.get_all_teams())
        st.metric("Seleções Cadastradas", teams_count)
    
    with col2:
        query = "SELECT COUNT(*) FROM matches"
        matches_count = db.execute_query(query)[0][0]
        st.metric("Jogos no Banco", matches_count)
    
    with col3:
        query = "SELECT COUNT(*) FROM matches WHERE home_goals IS NOT NULL"
        played_count = db.execute_query(query)[0][0]
        st.metric("Jogos Finalizados", played_count)
    
    # Próximos jogos
    st.markdown("---")
    st.subheader("📅 Próximos Jogos")
    
    upcoming = updater.get_upcoming_matches(days_ahead=7)
    
    if upcoming:
        df_upcoming = pd.DataFrame(upcoming)
        df_upcoming["date"] = pd.to_datetime(df_upcoming["date"]).dt.strftime("%d/%m/%Y %H:%M")
        st.dataframe(df_upcoming, use_container_width=True)
    else:
        st.info("Nenhum jogo agendado para os próximos 7 dias")

# ==================== ANÁLISE DE SELEÇÕES ====================
elif menu == "📊 Análise de Seleções":
    st.title("📊 Análise Detalhada de Seleções")
    
    teams_df = db.get_all_teams()
    
    if teams_df.empty:
        st.warning("Nenhuma seleção cadastrada. Execute a coleta de dados primeiro.")
    else:
        # Seletor de seleção
        team_names = teams_df["name"].tolist()
        selected_team_name = st.selectbox("Selecione uma seleção:", team_names)
        
        team_id = teams_df[teams_df["name"] == selected_team_name]["id"].values[0]
        
        # Obter estatísticas
        overall_stats = processor.get_team_overall_stats(team_id)
        recent_form = processor.get_team_recent_form(team_id)
        strength = processor.calculate_team_strength(team_id)
        
        # Métricas principais
        st.markdown("### 📈 Métricas Principais")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Força Geral", f"{strength:.1f}/100")
        
        with col2:
            st.metric("Taxa de Vitória", f"{overall_stats.get('overall_win_rate', 0):.1%}")
        
        with col3:
            st.metric("Média de Gols", f"{overall_stats.get('overall_avg_goals_for', 0):.2f}")
        
        with col4:
            st.metric("Saldo de Gols", overall_stats.get("overall_goal_difference", 0))
        
        # Estatísticas gerais vs. forma recente
        st.markdown("### 📊 Comparação: Histórico Geral vs. Forma Recente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Histórico Geral**")
            st.write(f"- Total de jogos: {overall_stats.get('total_matches', 0)}")
            st.write(f"- Vitórias: {overall_stats.get('overall_wins', 0)}")
            st.write(f"- Empates: {overall_stats.get('overall_draws', 0)}")
            st.write(f"- Derrotas: {overall_stats.get('overall_losses', 0)}")
            st.write(f"- Gols marcados: {overall_stats.get('overall_avg_goals_for', 0):.2f}/jogo")
            st.write(f"- Gols sofridos: {overall_stats.get('overall_avg_goals_against', 0):.2f}/jogo")
        
        with col2:
            st.markdown("**Forma Recente (últimos 10 jogos)**")
            st.write(f"- Jogos: {recent_form.get('recent_matches', 0)}")
            st.write(f"- Vitórias: {recent_form.get('recent_wins', 0)}")
            st.write(f"- Empates: {recent_form.get('recent_draws', 0)}")
            st.write(f"- Derrotas: {recent_form.get('recent_losses', 0)}")
            st.write(f"- Gols marcados: {recent_form.get('recent_avg_goals_for', 0):.2f}/jogo")
            st.write(f"- Gols sofridos: {recent_form.get('recent_avg_goals_against', 0):.2f}/jogo")
        
        # Histórico de jogos
        st.markdown("### 📜 Histórico de Jogos Recentes")
        
        matches_df = db.get_team_matches(team_id, limit=20)
        
        if not matches_df.empty:
            matches_display = matches_df[["date", "home_team_name", "home_goals", "away_goals", "away_team_name", "competition"]].copy()
            matches_display["date"] = pd.to_datetime(matches_display["date"]).dt.strftime("%d/%m/%Y")
            matches_display["placar"] = matches_display["home_goals"].astype(str) + " x " + matches_display["away_goals"].astype(str)
            
            st.dataframe(matches_display, use_container_width=True)
        else:
            st.info("Nenhum histórico de jogos disponível")

# ==================== PREVISÃO DE JOGOS ====================
elif menu == "🎯 Previsão de Jogos":
    st.title("🎯 Previsão de Placares")
    
    teams_df = db.get_all_teams()
    
    if teams_df.empty:
        st.warning("Nenhuma seleção cadastrada. Execute a coleta de dados primeiro.")
    else:
        st.markdown("### Selecione o Confronto")
        
        col1, col2 = st.columns(2)
        
        with col1:
            team_names = teams_df["name"].tolist()
            home_team_name = st.selectbox("Seleção Mandante:", team_names, key="home")
            home_team_id = teams_df[teams_df["name"] == home_team_name]["id"].values[0]
        
        with col2:
            away_team_name = st.selectbox("Seleção Visitante:", team_names, key="away")
            away_team_id = teams_df[teams_df["name"] == away_team_name]["id"].values[0]
        
        if st.button("🔮 Gerar Previsão", type="primary"):
            if home_team_id == away_team_id:
                st.error("Selecione duas seleções diferentes!")
            else:
                with st.spinner("Calculando previsão..."):
                    prediction = match_predictor.predict_match_score_adaptive(home_team_id, away_team_id)
                
                # Resultado previsto
                st.markdown("---")
                st.markdown("### 🎯 Resultado Previsto")
                
                col1, col2, col3 = st.columns([2, 1, 2])
                
                with col1:
                    st.markdown(f"#### {home_team_name}")
                    st.markdown(f"# {prediction['predicted_home_goals']}")
                
                with col2:
                    st.markdown("#### ")
                    st.markdown("# X")
                
                with col3:
                    st.markdown(f"#### {away_team_name}")
                    st.markdown(f"# {prediction['predicted_away_goals']}")
                
                # Probabilidades
                st.markdown("---")
                st.markdown("### 📊 Probabilidades")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        f"Vitória {home_team_name}", 
                        f"{prediction['prob_home_win']:.1%}",
                        delta=None
                    )
                
                with col2:
                    st.metric("Empate", f"{prediction['prob_draw']:.1%}")
                
                with col3:
                    st.metric(
                        f"Vitória {away_team_name}", 
                        f"{prediction['prob_away_win']:.1%}"
                    )
                
                # Gráfico de probabilidades
                fig = go.Figure(data=[
                    go.Bar(
                        x=[f"Vitória\n{home_team_name}", "Empate", f"Vitória\n{away_team_name}"],
                        y=[prediction['prob_home_win'], prediction['prob_draw'], prediction['prob_away_win']],
                        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c']
                    )
                ])
                fig.update_layout(
                    title="Distribuição de Probabilidades",
                    yaxis_title="Probabilidade",
                    yaxis_tickformat=".0%"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Detalhes adicionais
                st.markdown("---")
                st.markdown("### 📈 Detalhes da Previsão")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**{home_team_name}**")
                    st.write(f"- Gols esperados: {prediction['home_goals_expected']}")
                    st.write(f"- Intervalo de confiança: {prediction['home_goals_ci'][0]:.1f} - {prediction['home_goals_ci'][1]:.1f}")
                
                with col2:
                    st.write(f"**{away_team_name}**")
                    st.write(f"- Gols esperados: {prediction['away_goals_expected']}")
                    st.write(f"- Intervalo de confiança: {prediction['away_goals_ci'][0]:.1f} - {prediction['away_goals_ci'][1]:.1f}")
                
                # Informações de adaptação
                if prediction["adaptation_info"]["is_adapted"]:
                    st.info(
                        f"✅ **Previsão Adaptativa**: Esta previsão considera resultados reais da Copa 2026. "
                        f"{home_team_name}: {prediction['adaptation_info']['home_copa_matches']} jogos | "
                        f"{away_team_name}: {prediction['adaptation_info']['away_copa_matches']} jogos"
                    )

# ==================== CLASSIFICAÇÃO DOS GRUPOS ====================
elif menu == "🏆 Classificação dos Grupos":
    st.title("🏆 Previsão de Classificação dos Grupos")
    
    st.markdown("""
    ### Como funciona
    
    O sistema simula todos os jogos de cada grupo considerando:
    - Resultados reais já ocorridos
    - Previsões adaptativas para jogos futuros
    - Critérios de desempate da FIFA
    """)
    
    st.markdown("---")
    
    # Definir grupos (exemplo - ajustar conforme dados reais)
    st.info("⚠️ Configure os grupos da Copa 2026 no código para gerar previsões")
    
    # Exemplo de estrutura de grupos
    example_groups = {
        "A": [1, 2, 3, 4],  # IDs das seleções
        "B": [5, 6, 7, 8],
        # ... outros grupos
    }
    
    st.code("""
    # Exemplo de configuração de grupos:
    groups = {
        "A": [brasil_id, argentina_id, uruguai_id, colombia_id],
        "B": [franca_id, alemanha_id, espanha_id, italia_id],
        # ... outros grupos
    }
    
    predictions = group_predictor.predict_all_groups(groups)
    """)

# ==================== PREVISÃO DE PÓDIO ====================
elif menu == "🥇 Previsão de Pódio":
    st.title("🥇 Previsão de Pódio")
    
    st.markdown("""
    ### Simulação de Monte Carlo
    
    O sistema simula o torneio completo 1000+ vezes para calcular as probabilidades
    de cada seleção chegar ao pódio.
    """)
    
    st.markdown("---")
    
    st.info("⚠️ A previsão de pódio será gerada após a definição dos classificados para o mata-mata")
    
    st.markdown("""
    ### Metodologia
    
    1. **Fase de Grupos**: Considera resultados reais + previsões
    2. **Mata-Mata**: Simula todos os confrontos probabilisticamente
    3. **Monte Carlo**: 1000 simulações completas do torneio
    4. **Resultado**: Probabilidade de cada seleção ser campeã, vice ou 3ª
    """)

# ==================== ATUALIZAR DADOS ====================
elif menu == "🔄 Atualizar Dados":
    st.title("🔄 Atualização de Dados")
    
    st.markdown("""
    ### Gerenciamento de Dados
    
    Use esta seção para atualizar os dados do sistema.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Atualização Manual")
        
        if st.button("🔄 Atualizar Resultados de Hoje", type="primary"):
            with st.spinner("Atualizando resultados..."):
                count = updater.update_all_matches()
                st.success(f"✅ {count} jogos atualizados!")
        
        if st.button("📥 Sincronizar Todos os Jogos da Copa 2026"):
            with st.spinner("Sincronizando jogos..."):
                updater.sync_copa_2026_matches()
                st.success("✅ Sincronização concluída!")
    
    with col2:
        st.subheader("Jogos ao Vivo")
        
        if st.button("🔴 Verificar Jogos ao Vivo"):
            live_matches = updater.get_live_matches()
            
            if live_matches:
                st.success(f"🔴 {len(live_matches)} jogos ao vivo")
                for match in live_matches:
                    st.write(
                        f"**{match['home_team']}** {match['home_goals']} x "
                        f"{match['away_goals']} **{match['away_team']}** "
                        f"({match['elapsed']}')"
                    )
            else:
                st.info("Nenhum jogo ao vivo no momento")

# ==================== ESTATÍSTICAS ====================
elif menu == "📈 Estatísticas":
    st.title("📈 Estatísticas Gerais")
    
    teams_data = processor.get_all_teams_data()
    
    if teams_data.empty:
        st.warning("Nenhum dado disponível")
    else:
        # Ranking de força
        st.subheader("🏆 Ranking de Força das Seleções")
        
        ranking = teams_data[["team_name", "strength_score", "overall_overall_win_rate", 
                             "overall_overall_avg_goals_for"]].sort_values(
            "strength_score", ascending=False
        ).head(20)
        
        ranking.columns = ["Seleção", "Força", "Taxa de Vitória", "Média de Gols"]
        ranking["Força"] = ranking["Força"].round(1)
        ranking["Taxa de Vitória"] = (ranking["Taxa de Vitória"] * 100).round(1).astype(str) + "%"
        ranking["Média de Gols"] = ranking["Média de Gols"].round(2)
        
        st.dataframe(ranking, use_container_width=True)
        
        # Gráfico de força
        fig = px.bar(
            teams_data.sort_values("strength_score", ascending=False).head(15),
            x="team_name",
            y="strength_score",
            title="Top 15 Seleções por Força",
            labels={"team_name": "Seleção", "strength_score": "Score de Força"}
        )
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Sistema de Análise Copa 2026**\n\n"
    "Desenvolvido com ❤️ usando Streamlit"
)
