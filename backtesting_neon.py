"""
Backtesting com Dados Reais do Neon PostgreSQL
Valida precisão do modelo com dados históricos
"""

import subprocess
import json
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import poisson

PROJECT_ID = "restless-glitter-71170845"
DATABASE_NAME = "neondb"

print("=" * 80)
print("BACKTESTING COM DADOS REAIS DO NEON")
print("=" * 80)

def run_sql(sql):
    """Executar SQL no Neon"""
    input_data = {
        "projectId": PROJECT_ID,
        "databaseName": DATABASE_NAME,
        "sql": sql
    }
    
    cmd = [
        "manus-mcp-cli", "tool", "call", "run_sql",
        "--server", "neon",
        "--input", json.dumps(input_data)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        try:
            # Parse JSON from stdout
            data = json.loads(result.stdout)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'rows' in data:
                return data['rows']
            else:
                return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Erro ao parsear resposta: {e}")
            print(f"Stdout: {result.stdout[:200]}")
            return []
    return []

# 1. Buscar todos os jogos
print("\n📊 Buscando jogos do Neon...")

sql_matches = """
SELECT 
    m.id,
    m.date,
    m.home_team_id,
    m.away_team_id,
    m.home_goals,
    m.away_goals,
    ht.name as home_team,
    at.name as away_team
FROM matches m
JOIN teams ht ON m.home_team_id = ht.id
JOIN teams at ON m.away_team_id = at.id
ORDER BY m.date
"""

matches = run_sql(sql_matches)
print(f"✅ {len(matches)} jogos encontrados")

if len(matches) < 50:
    print("\n⚠️  Poucos jogos disponíveis. Aguardando importação completa...")
    print("Execute novamente após a importação terminar.")
    exit(0)

# Converter para DataFrame
df = pd.DataFrame(matches)
df['date'] = pd.to_datetime(df['date'])
df['home_goals'] = df['home_goals'].astype(int)
df['away_goals'] = df['away_goals'].astype(int)

print(f"\n📅 Período: {df['date'].min().date()} até {df['date'].max().date()}")

# 2. Dividir em treino e teste (70% treino, 30% teste)
split_index = int(len(df) * 0.7)
train_df = df.iloc[:split_index].copy()
test_df = df.iloc[split_index:].copy()

print(f"\n📊 Divisão dos dados:")
print(f"  - Treino: {len(train_df)} jogos ({df['date'].min().date()} até {train_df['date'].max().date()})")
print(f"  - Teste: {len(test_df)} jogos ({test_df['date'].min().date()} até {df['date'].max().date()})")

# 3. Calcular estatísticas por time (apenas dados de treino)
print("\n📈 Calculando estatísticas dos times (dados de treino)...")

team_stats = {}

for team_id in set(train_df['home_team_id'].unique()) | set(train_df['away_team_id'].unique()):
    home_matches = train_df[train_df['home_team_id'] == team_id]
    away_matches = train_df[train_df['away_team_id'] == team_id]
    
    all_matches = len(home_matches) + len(away_matches)
    
    if all_matches == 0:
        continue
    
    # Gols marcados
    goals_for = home_matches['home_goals'].sum() + away_matches['away_goals'].sum()
    goals_against = home_matches['away_goals'].sum() + away_matches['home_goals'].sum()
    
    # Vitórias
    home_wins = (home_matches['home_goals'] > home_matches['away_goals']).sum()
    away_wins = (away_matches['away_goals'] > away_matches['home_goals']).sum()
    wins = home_wins + away_wins
    
    # Empates
    home_draws = (home_matches['home_goals'] == home_matches['away_goals']).sum()
    away_draws = (away_matches['away_goals'] == away_matches['home_goals']).sum()
    draws = home_draws + away_draws
    
    team_stats[team_id] = {
        'matches': all_matches,
        'wins': wins,
        'draws': draws,
        'losses': all_matches - wins - draws,
        'goals_for': goals_for,
        'goals_against': goals_against,
        'avg_goals_for': goals_for / all_matches if all_matches > 0 else 1.5,
        'avg_goals_against': goals_against / all_matches if all_matches > 0 else 1.5,
        'win_rate': wins / all_matches if all_matches > 0 else 0.33
    }

print(f"✅ Estatísticas calculadas para {len(team_stats)} times")

# 4. Função de previsão
def predict_match(home_id, away_id, stats):
    """Prever placar de um jogo"""
    
    # Estatísticas padrão se time não tiver dados
    default_stats = {
        'avg_goals_for': 1.5,
        'avg_goals_against': 1.5,
        'win_rate': 0.33
    }
    
    home_stats = stats.get(home_id, default_stats)
    away_stats = stats.get(away_id, default_stats)
    
    # Calcular gols esperados
    home_expected = (home_stats['avg_goals_for'] + away_stats['avg_goals_against']) / 2
    away_expected = (away_stats['avg_goals_for'] + home_stats['avg_goals_against']) / 2
    
    # Vantagem de casa
    home_expected += 0.3
    
    # Limitar valores extremos
    home_expected = max(0.5, min(4.0, home_expected))
    away_expected = max(0.5, min(4.0, away_expected))
    
    # Prever placar (valor mais provável da distribuição de Poisson)
    home_goals = int(round(home_expected))
    away_goals = int(round(away_expected))
    
    # Calcular probabilidades
    max_goals = 6
    prob_matrix = np.zeros((max_goals, max_goals))
    
    for i in range(max_goals):
        for j in range(max_goals):
            prob_matrix[i, j] = poisson.pmf(i, home_expected) * poisson.pmf(j, away_expected)
    
    prob_home_win = prob_matrix[np.triu_indices_from(prob_matrix, k=1)].sum()
    prob_draw = np.trace(prob_matrix)
    prob_away_win = prob_matrix[np.tril_indices_from(prob_matrix, k=-1)].sum()
    
    return {
        'home_goals': home_goals,
        'away_goals': away_goals,
        'home_expected': home_expected,
        'away_expected': away_expected,
        'prob_home_win': prob_home_win,
        'prob_draw': prob_draw,
        'prob_away_win': prob_away_win
    }

# 5. Executar backtesting
print("\n🔍 Executando backtesting...")

results = []

for idx, row in test_df.iterrows():
    pred = predict_match(row['home_team_id'], row['away_team_id'], team_stats)
    
    # Resultado real
    real_home = row['home_goals']
    real_away = row['away_goals']
    real_result = 'home' if real_home > real_away else ('away' if real_away > real_home else 'draw')
    
    # Resultado previsto
    pred_home = pred['home_goals']
    pred_away = pred['away_goals']
    pred_result = 'home' if pred_home > pred_away else ('away' if pred_away > pred_home else 'draw')
    
    # Acertos
    exact_score = (pred_home == real_home and pred_away == real_away)
    correct_result = (pred_result == real_result)
    correct_home_goals = (pred_home == real_home)
    correct_away_goals = (pred_away == real_away)
    
    # Pontuação (sistema do Bolão)
    points = 0
    if exact_score:
        points = 20
    elif correct_result:
        points = 10
        if correct_home_goals or correct_away_goals:
            points = 15
    
    results.append({
        'match': f"{row['home_team']} vs {row['away_team']}",
        'real': f"{real_home}x{real_away}",
        'predicted': f"{pred_home}x{pred_away}",
        'exact_score': exact_score,
        'correct_result': correct_result,
        'correct_home_goals': correct_home_goals,
        'correct_away_goals': correct_away_goals,
        'points': points
    })

# 6. Calcular métricas
results_df = pd.DataFrame(results)

print("\n" + "=" * 80)
print("RESULTADOS DO BACKTESTING")
print("=" * 80)

total_matches = len(results_df)
exact_score_rate = (results_df['exact_score'].sum() / total_matches) * 100
correct_result_rate = (results_df['correct_result'].sum() / total_matches) * 100
correct_home_goals_rate = (results_df['correct_home_goals'].sum() / total_matches) * 100
correct_away_goals_rate = (results_df['correct_away_goals'].sum() / total_matches) * 100
avg_points = results_df['points'].mean()

print(f"\n📊 Métricas de Precisão:")
print(f"  - Jogos testados: {total_matches}")
print(f"  - Placar exato: {exact_score_rate:.1f}% ({results_df['exact_score'].sum()} acertos)")
print(f"  - Resultado correto: {correct_result_rate:.1f}% ({results_df['correct_result'].sum()} acertos)")
print(f"  - Gols mandante corretos: {correct_home_goals_rate:.1f}%")
print(f"  - Gols visitante corretos: {correct_away_goals_rate:.1f}%")
print(f"  - Pontos médios: {avg_points:.1f} pts/jogo")

# Benchmarks
print(f"\n🎯 Comparação com Benchmarks:")
print(f"  - Placar exato: {exact_score_rate:.1f}% (benchmark: 10-15%)")
print(f"  - Resultado correto: {correct_result_rate:.1f}% (benchmark: 50-60%)")
print(f"  - Pontos médios: {avg_points:.1f} pts (benchmark: 10-12 pts)")

# Exemplos
print(f"\n📋 Exemplos de Previsões:")
sample = results_df.sample(min(10, len(results_df)))
for idx, row in sample.iterrows():
    status = "✅" if row['exact_score'] else ("🟡" if row['correct_result'] else "❌")
    print(f"  {status} {row['match']:40s} Real {row['real']:5s} Previsto {row['predicted']:5s} ({row['points']} pts)")

# Salvar resultados
results_df.to_csv('backtesting_neon_results.csv', index=False)
print(f"\n💾 Resultados salvos em: backtesting_neon_results.csv")

print("\n" + "=" * 80)
print("CONCLUSÃO")
print("=" * 80)

if correct_result_rate >= 50:
    print("\n✅ MODELO COM BOA PRECISÃO!")
    print("O modelo está prevendo resultados com taxa aceitável.")
elif correct_result_rate >= 40:
    print("\n🟡 MODELO COM PRECISÃO MODERADA")
    print("O modelo precisa de mais dados ou ajustes nos parâmetros.")
else:
    print("\n⚠️  MODELO COM BAIXA PRECISÃO")
    print("Aguarde importação completa de dados para melhorar precisão.")

print(f"""
💡 Recomendações:
  - Modelo atual baseado em {len(train_df)} jogos de treino
  - Precisão melhorará com mais dados históricos
  - Execute novamente após importação completa
  - Durante a Copa, modelo se adaptará aos resultados reais
""")

print("=" * 80)
