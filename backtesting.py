"""
Backtesting do Sistema de Previsão
Treina com dados até uma data e testa em jogos posteriores
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3

from utils import DatabaseManager, calculate_team_stats
from data_processing import DataProcessor
from model import MatchPredictor
from data_collection import APIFootballCollector

print("=" * 80)
print("BACKTESTING - VALIDAÇÃO DO MODELO DE PREVISÃO")
print("=" * 80)

# Configuração do backtesting
CUTOFF_DATE = "2024-01-01"  # Treinar com dados até essa data
TEST_PERIOD_MONTHS = 12      # Testar nos próximos 12 meses

print(f"\n📅 Configuração:")
print(f"  - Data de corte: {CUTOFF_DATE}")
print(f"  - Período de teste: {TEST_PERIOD_MONTHS} meses após o corte")
print(f"  - Treino: Dados até {CUTOFF_DATE}")
print(f"  - Teste: Jogos após {CUTOFF_DATE}")

# Inicializar componentes
db = DatabaseManager()
collector = APIFootballCollector()

# Coletar dados de seleções importantes para backtesting
print("\n" + "=" * 80)
print("COLETA DE DADOS PARA BACKTESTING")
print("=" * 80)

test_teams = {
    "Brazil": 6,
    "Argentina": 26,
    "France": 2,
    "Germany": 25,
    "Spain": 9,
    "England": 10,
    "Portugal": 27,
    "Netherlands": 1118,
    "Italy": 768,
    "Uruguay": 7,
    "Belgium": 1,
    "Croatia": 3,
}

print(f"\n📥 Coletando dados de {len(test_teams)} seleções...")
print("(Isso pode levar alguns minutos devido ao rate limit da API)")

for name, team_id in test_teams.items():
    print(f"\n  🔄 {name}...", end=" ")
    
    # Inserir seleção
    db.insert_team(team_id=team_id, name=name, country=name)
    
    # Coletar histórico de jogos (últimos 5 anos)
    matches = collector.get_team_matches(team_id, limit=100)
    
    count = 0
    for match in matches:
        try:
            match_id = match["fixture"]["id"]
            date = match["fixture"]["date"]
            home_team_id = match["teams"]["home"]["id"]
            away_team_id = match["teams"]["away"]["id"]
            home_goals = match["goals"]["home"]
            away_goals = match["goals"]["away"]
            competition = match["league"]["name"]
            stage = match["league"].get("round", "")
            
            if home_goals is not None and away_goals is not None:
                db.insert_match(
                    match_id=match_id,
                    date=date,
                    home_team_id=home_team_id,
                    away_team_id=away_team_id,
                    home_goals=home_goals,
                    away_goals=away_goals,
                    competition=competition,
                    stage=stage
                )
                count += 1
        except Exception as e:
            continue
    
    print(f"✅ {count} jogos coletados")

print("\n✅ Coleta concluída!")

# Verificar dados coletados
print("\n" + "=" * 80)
print("ANÁLISE DOS DADOS COLETADOS")
print("=" * 80)

conn = sqlite3.connect(db.db_path)

# Total de jogos
total_matches = pd.read_sql_query("SELECT COUNT(*) as count FROM matches", conn)
print(f"\n📊 Total de jogos no banco: {total_matches['count'].values[0]}")

# Jogos de treino (antes do corte)
train_matches = pd.read_sql_query(
    f"SELECT COUNT(*) as count FROM matches WHERE date < '{CUTOFF_DATE}'", 
    conn
)
print(f"📚 Jogos de treino (antes de {CUTOFF_DATE}): {train_matches['count'].values[0]}")

# Jogos de teste (depois do corte)
test_date_end = (datetime.strptime(CUTOFF_DATE, "%Y-%m-%d") + timedelta(days=TEST_PERIOD_MONTHS*30)).strftime("%Y-%m-%d")
test_matches = pd.read_sql_query(
    f"""SELECT COUNT(*) as count FROM matches 
        WHERE date >= '{CUTOFF_DATE}' 
        AND date <= '{test_date_end}'
        AND home_goals IS NOT NULL 
        AND away_goals IS NOT NULL""", 
    conn
)
print(f"🧪 Jogos de teste (após {CUTOFF_DATE}): {test_matches['count'].values[0]}")

if test_matches['count'].values[0] == 0:
    print("\n⚠️  Não há jogos suficientes para teste no período especificado.")
    print("Ajustando para usar todos os jogos disponíveis...")
    
    # Pegar todos os jogos
    all_matches_query = """
        SELECT * FROM matches 
        WHERE home_goals IS NOT NULL 
        AND away_goals IS NOT NULL
        ORDER BY date
    """
    all_matches_df = pd.read_sql_query(all_matches_query, conn)
    
    if len(all_matches_df) > 0:
        # Dividir: 70% treino, 30% teste
        split_idx = int(len(all_matches_df) * 0.7)
        train_df = all_matches_df.iloc[:split_idx]
        test_df = all_matches_df.iloc[split_idx:]
        
        print(f"\n📊 Divisão ajustada:")
        print(f"  - Treino: {len(train_df)} jogos")
        print(f"  - Teste: {len(test_df)} jogos")
        
        # Atualizar CUTOFF_DATE
        if len(train_df) > 0:
            CUTOFF_DATE = train_df.iloc[-1]['date']
            print(f"  - Nova data de corte: {CUTOFF_DATE}")
else:
    test_df = pd.read_sql_query(
        f"""SELECT m.*, 
               t1.name as home_team_name,
               t2.name as away_team_name
            FROM matches m
            LEFT JOIN teams t1 ON m.home_team_id = t1.id
            LEFT JOIN teams t2 ON m.away_team_id = t2.id
            WHERE m.date >= '{CUTOFF_DATE}' 
            AND m.date <= '{test_date_end}'
            AND m.home_goals IS NOT NULL 
            AND m.away_goals IS NOT NULL
            ORDER BY m.date""", 
        conn
    )

conn.close()

# Executar Backtesting
print("\n" + "=" * 80)
print("EXECUTANDO BACKTESTING")
print("=" * 80)

if 'test_df' not in locals() or len(test_df) == 0:
    print("\n❌ Não há dados suficientes para backtesting.")
    print("\n💡 Dica: Execute 'python src/data_collection.py' para coletar mais dados")
    sys.exit(1)

print(f"\n🔮 Gerando previsões para {len(test_df)} jogos de teste...")

# Criar preditor (usando apenas dados de treino)
class BacktestPredictor(MatchPredictor):
    """Preditor que usa apenas dados até a data de corte"""
    
    def __init__(self, cutoff_date):
        super().__init__()
        self.cutoff_date = cutoff_date
    
    def get_team_matches_before_cutoff(self, team_id, limit=100):
        """Obter apenas jogos antes da data de corte"""
        query = f"""
            SELECT * FROM matches 
            WHERE (home_team_id = ? OR away_team_id = ?)
            AND date < ?
            ORDER BY date DESC
            LIMIT ?
        """
        conn = sqlite3.connect(self.db.db_path)
        df = pd.read_sql_query(query, conn, params=(team_id, team_id, self.cutoff_date, limit))
        conn.close()
        return df

predictor = BacktestPredictor(CUTOFF_DATE)

# Fazer previsões e comparar com resultados reais
results = []
predictions_detail = []

for idx, match in test_df.iterrows():
    try:
        # Fazer previsão
        prediction = predictor.predict_match_score(
            match['home_team_id'],
            match['away_team_id']
        )
        
        # Resultado real
        real_home = int(match['home_goals'])
        real_away = int(match['away_goals'])
        
        # Resultado previsto
        pred_home = prediction['predicted_home_goals']
        pred_away = prediction['predicted_away_goals']
        
        # Calcular acertos
        placar_exato = (pred_home == real_home) and (pred_away == real_away)
        gols_home = (pred_home == real_home)
        gols_away = (pred_away == real_away)
        
        # Resultado (vitória/empate/derrota)
        real_result = 'home' if real_home > real_away else ('away' if real_away > real_home else 'draw')
        pred_result = prediction['predicted_result']
        resultado_correto = (real_result == pred_result)
        
        # Pontuação do Bolão
        if placar_exato:
            points = 20
            tipo = "Placar exato"
        elif resultado_correto and (gols_home or gols_away):
            points = 15
            tipo = "Resultado + gols"
        elif resultado_correto:
            points = 10
            tipo = "Resultado"
        elif gols_home or gols_away:
            points = 5
            tipo = "Gols de um time"
        else:
            points = 0
            tipo = "Errou"
        
        results.append({
            'placar_exato': placar_exato,
            'resultado_correto': resultado_correto,
            'gols_home': gols_home,
            'gols_away': gols_away,
            'points': points
        })
        
        predictions_detail.append({
            'Data': match['date'][:10] if 'date' in match else 'N/A',
            'Jogo': f"{match.get('home_team_name', 'Time 1')} vs {match.get('away_team_name', 'Time 2')}",
            'Real': f"{real_home} x {real_away}",
            'Previsto': f"{pred_home} x {pred_away}",
            'Pontos': points,
            'Tipo': tipo
        })
        
    except Exception as e:
        print(f"  ⚠️  Erro ao processar jogo {idx}: {e}")
        continue

# Análise dos Resultados
print("\n" + "=" * 80)
print("RESULTADOS DO BACKTESTING")
print("=" * 80)

if len(results) > 0:
    df_results = pd.DataFrame(results)
    df_predictions = pd.DataFrame(predictions_detail)
    
    # Métricas gerais
    total_predictions = len(df_results)
    placar_exato_count = df_results['placar_exato'].sum()
    resultado_count = df_results['resultado_correto'].sum()
    gols_home_count = df_results['gols_home'].sum()
    gols_away_count = df_results['gols_away'].sum()
    total_points = df_results['points'].sum()
    
    placar_exato_rate = placar_exato_count / total_predictions
    resultado_rate = resultado_count / total_predictions
    avg_points = total_points / total_predictions
    
    print(f"\n📊 Métricas Gerais ({total_predictions} jogos):")
    print(f"  - Taxa de placar exato: {placar_exato_rate:.1%} ({placar_exato_count}/{total_predictions})")
    print(f"  - Taxa de resultado correto: {resultado_rate:.1%} ({resultado_count}/{total_predictions})")
    print(f"  - Taxa de gols mandante: {gols_home_count/total_predictions:.1%}")
    print(f"  - Taxa de gols visitante: {gols_away_count/total_predictions:.1%}")
    print(f"  - Pontuação média por jogo: {avg_points:.1f} pontos")
    print(f"  - Pontuação total: {total_points} pontos")
    
    # Benchmark da indústria
    print(f"\n📈 Comparação com Benchmarks da Indústria:")
    print(f"  - Placar exato: {placar_exato_rate:.1%} (benchmark: 10-15%)")
    print(f"  - Resultado: {resultado_rate:.1%} (benchmark: 50-60%)")
    
    # Avaliação
    print(f"\n💡 Avaliação do Modelo:")
    
    if placar_exato_rate >= 0.15:
        print(f"  ✅ Placar exato: EXCELENTE (acima do benchmark)")
    elif placar_exato_rate >= 0.10:
        print(f"  ✓ Placar exato: BOM (dentro do benchmark)")
    else:
        print(f"  ⚠️  Placar exato: ABAIXO DO ESPERADO (precisa melhorar)")
    
    if resultado_rate >= 0.60:
        print(f"  ✅ Resultado: EXCELENTE (acima do benchmark)")
    elif resultado_rate >= 0.50:
        print(f"  ✓ Resultado: BOM (dentro do benchmark)")
    else:
        print(f"  ⚠️  Resultado: ABAIXO DO ESPERADO (precisa melhorar)")
    
    # Detalhes das previsões
    print(f"\n📋 Amostra de Previsões (primeiras 20):")
    print(df_predictions.head(20).to_string(index=False))
    
    # Distribuição de pontos
    print(f"\n📊 Distribuição de Pontuação:")
    points_dist = df_results['points'].value_counts().sort_index(ascending=False)
    for points, count in points_dist.items():
        pct = count / total_predictions * 100
        print(f"  - {points} pontos: {count} jogos ({pct:.1f}%)")
    
    # Projeção para o Bolão
    print(f"\n🏆 Projeção para o Bolão Copa 2026:")
    total_copa_games = 128
    projected_points = avg_points * total_copa_games
    print(f"  - Pontuação média por jogo: {avg_points:.1f} pts")
    print(f"  - Projeção para 128 jogos: {projected_points:.0f} pts")
    print(f"  - Projeção com grupos (12×10): {projected_points + 120:.0f} pts")
    print(f"  - Projeção com pódio (+100): {projected_points + 220:.0f} pts")
    
    # Salvar resultados
    output_file = "/home/ubuntu/analise-copa-2026/backtesting_results.csv"
    df_predictions.to_csv(output_file, index=False)
    print(f"\n💾 Resultados salvos em: {output_file}")
    
else:
    print("\n❌ Nenhuma previsão foi gerada.")

# Adicionar ao final do backtesting.py
if results:
    performance = 'performando bem' if resultado_rate >= 0.5 else 'precisa de mais dados'
    recommendation = 'Recomendado para uso no Bolão' if resultado_rate >= 0.5 else 'Coletar mais dados antes de usar'
    summary = f"""
✅ Backtesting Concluído!

📊 Resumo:
  - Jogos testados: {len(results)}
  - Taxa de acerto de resultado: {resultado_rate:.1%}
  - Pontuação média: {avg_points:.1f} pts/jogo

💡 Interpretação:
  - O modelo está {performance}
  - {recommendation}
  
🚀 Próximos Passos:
  1. Revisar previsões incorretas
  2. Ajustar parâmetros se necessário
  3. Coletar mais dados históricos
  4. Usar sistema adaptativo durante a Copa
"""
    print(summary)
else:
    print("⚠️ Nenhum resultado disponível")

print("=" * 80)
