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
    """Conecta ao Neon PostgreSQL usando secrets com configurações otimizadas"""
    try:
        # Tentar usar secrets do Streamlit Cloud
        if hasattr(st, 'secrets') and 'neon' in st.secrets:
            conn_string = st.secrets['neon']['connection_string']
        else:
            # Fallback para desenvolvimento local
            st.warning("⚠️ Usando configuração local. Configure secrets no Streamlit Cloud.")
            return None
        
        # Conectar com timeout e autocommit
        conn = psycopg2.connect(
            conn_string,
            connect_timeout=10,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5
        )
        conn.autocommit = True
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
        ["🏠 Home", "🏆 Jogos da Copa", "🎯 Previsões", "📊 Classificação & Pódio", "📊 Estatísticas", "ℹ️ Sobre"]
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

# Página Jogos da Copa
elif page == "🏆 Jogos da Copa":
    st.header("🏆 Todos os Jogos da Copa 2026")
    
    from copa_2026_structure import GRUPOS_COPA_2026, get_all_group_matches
    from tournament_simulator import simulate_group_stage, get_default_stats
    
    st.info("📊 **104 jogos** | 72 da fase de grupos + 32 do mata-mata")
    
    # Criar dicionário de estatísticas
    team_stats = {}
    teams_df = get_teams()
    
    # Buscar estatísticas reais do banco
    if len(teams_df) > 0:
        for _, row in teams_df.iterrows():
            team_name = row['name']
            team_id = row['id']
            stats = get_team_stats(team_id)
            if stats:
                team_stats[team_name] = stats
    
    # Completar com estatísticas padrão para times sem dados
    for grupo, teams in GRUPOS_COPA_2026.items():
        for team in teams:
            if team not in team_stats:
                team_stats[team] = get_default_stats()
    
    # Simular fase de grupos
    with st.spinner('🔄 Simulando fase de grupos...'):
        group_results = simulate_group_stage(team_stats)
    
    # Mostrar jogos por grupo
    st.subheader("🏆 Fase de Grupos")
    
    for grupo in sorted(GRUPOS_COPA_2026.keys()):
        with st.expander(f"Grupo {grupo}", expanded=False):
            teams = GRUPOS_COPA_2026[grupo]
            
            # Mostrar times do grupo
            st.markdown(f"**Times:** {', '.join(teams)}")
            st.markdown("---")
            
            # Gerar e mostrar jogos
            st.markdown("**Jogos:**")
            
            for i in range(len(teams)):
                for j in range(i + 1, len(teams)):
                    home = teams[i]
                    away = teams[j]
                    
                    # Obter estatísticas
                    home_stats = team_stats.get(home, get_default_stats())
                    away_stats = team_stats.get(away, get_default_stats())
                    
                    # Prever placar
                    from model_optimized import predict_match_optimized
                    prediction = predict_match_optimized(home_stats, away_stats)
                    
                    # Exibir previsão
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        st.markdown(f"**{home}**")
                    with col2:
                        st.markdown(f"<center><b>{prediction['home_goals']} x {prediction['away_goals']}</b></center>", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"**{away}**")
            
            # Mostrar classificação prevista
            st.markdown("---")
            st.markdown("**Classificação Prevista:**")
            standings = group_results[grupo]['standings']
            for idx, (team, stats) in enumerate(standings, 1):
                emoji = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "⚪"
                st.markdown(f"{emoji} **{idx}º {team}** - {stats['points']} pts | SG: {stats['gd']:+d} | {stats['gf']} gols")
    
    st.markdown("---")
    st.info("ℹ️ **Mata-mata será adicionado em breve** com base nos classificados da fase de grupos")

# Página Classificação & Pódio
elif page == "📊 Classificação & Pódio":
    st.header("📊 Classificação dos Grupos & Pódio")
    
    from copa_2026_structure import GRUPOS_COPA_2026
    from tournament_simulator import simulate_group_stage, simulate_knockout_stage, simulate_full_tournament, get_default_stats
    
    st.info("🎯 **Palpites necessários para o Bolão:** Classificação de cada grupo (1º e 2º) + Pódio (1º, 2º, 3º lugar)")
    
    # Criar dicionário de estatísticas
    team_stats = {}
    teams_df = get_teams()
    
    # Buscar estatísticas reais do banco
    if len(teams_df) > 0:
        for _, row in teams_df.iterrows():
            team_name = row['name']
            team_id = row['id']
            stats = get_team_stats(team_id)
            if stats:
                team_stats[team_name] = stats
    
    # Completar com estatísticas padrão para times sem dados
    for grupo, teams in GRUPOS_COPA_2026.items():
        for team in teams:
            if team not in team_stats:
                team_stats[team] = get_default_stats()
    
    # Simular fase de grupos
    with st.spinner('🔄 Simulando torneio completo...'):
        group_results = simulate_group_stage(team_stats)
    
    # Mostrar classificação dos grupos
    st.subheader("🏆 Classificação dos Grupos")
    st.caption("📊 Baseado em simulação com dados históricos de 7.623 jogos")
    
    # Criar tabela resumida
    classificacao_data = []
    for grupo in sorted(GRUPOS_COPA_2026.keys()):
        standings = group_results[grupo]['standings']
        primeiro = standings[0][0]
        segundo = standings[1][0]
        
        classificacao_data.append({
            'Grupo': grupo,
            '1º Lugar': f"🥇 {primeiro}",
            '2º Lugar': f"🥈 {segundo}",
            'Pts 1º': standings[0][1]['points'],
            'Pts 2º': standings[1][1]['points']
        })
    
    import pandas as pd
    df_class = pd.DataFrame(classificacao_data)
    st.dataframe(df_class, use_container_width=True, hide_index=True)
    
    # Detalhes por grupo
    st.markdown("---")
    st.subheader("🔍 Detalhes por Grupo")
    
    cols = st.columns(3)
    for idx, grupo in enumerate(sorted(GRUPOS_COPA_2026.keys())):
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"### Grupo {grupo}")
                standings = group_results[grupo]['standings']
                for pos, (team, stats) in enumerate(standings, 1):
                    emoji = "🥇" if pos == 1 else "🥈" if pos == 2 else "🥉" if pos == 3 else "⚪"
                    color = "green" if pos <= 2 else "orange" if pos == 3 else "red"
                    st.markdown(f":{color}[{emoji} **{pos}º** {team}]")
                    st.caption(f"{stats['points']} pts | SG {stats['gd']:+d} | {stats['gf']} gols")
    
    # Simular torneio completo para pódio
    st.markdown("---")
    st.subheader("🏆 Pódio Previsto")
    
    with st.spinner('🔄 Simulando mata-mata (1000x)...'):
        tournament_results = simulate_full_tournament(team_stats, n_simulations=1000)
    
    # Mostrar top 3 candidatos ao título
    st.markdown("### 🥇 Candidatos ao Título")
    champion_probs = tournament_results['champion_probabilities']
    top_champions = list(champion_probs.items())[:5]
    
    for idx, (team, prob) in enumerate(top_champions, 1):
        emoji = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "🎯"
        st.markdown(f"{emoji} **{team}** - {prob*100:.1f}% de chance")
        st.progress(prob)
    
    # Mostrar top 10 candidatos ao pódio
    st.markdown("---")
    st.markdown("### 🏆 Candidatos ao Pódio (Top 3)")
    podium_probs = tournament_results['podium_probabilities']
    top_podium = list(podium_probs.items())[:10]
    
    cols = st.columns(2)
    for idx, (team, prob) in enumerate(top_podium):
        with cols[idx % 2]:
            st.metric(team, f"{prob*100:.1f}%", delta="Pódio")
    
    # Simular mata-mata uma vez para mostrar pódio previsto
    st.markdown("---")
    st.markdown("### 🏆 Pódio Mais Provável")
    
    knockout_results = simulate_knockout_stage(group_results, team_stats)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🥇 Campeão")
        if knockout_results['champion']:
            st.success(f"**{knockout_results['champion']}**")
        else:
            st.info("A definir")
    
    with col2:
        st.markdown("### 🥈 Vice")
        if knockout_results['runner_up']:
            st.info(f"**{knockout_results['runner_up']}**")
        else:
            st.info("A definir")
    
    with col3:
        st.markdown("### 🥉 3º Lugar")
        if knockout_results['third_place']:
            st.warning(f"**{knockout_results['third_place']}**")
        else:
            st.info("A definir")
    
    st.markdown("---")
    st.caption("ℹ️ Previsões baseadas em 1000 simulações Monte Carlo com dados históricos")

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
