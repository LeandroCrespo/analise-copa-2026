"""
Backtesting Rápido com Dados Reais
Versão otimizada para execução rápida
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
import sqlite3
from utils import DatabaseManager
from model import MatchPredictor

print("=" * 80)
print("BACKTESTING RÁPIDO COM DADOS REAIS")
print("=" * 80)

# Inicializar
db = DatabaseManager()

# Buscar jogos para teste (últimos 200 jogos)
print("\n📊 Carregando dados...")

conn = sqlite3.connect(db.db_path)

# Pegar jogos dos últimos 2 anos
query = """
    SELECT m.*, 
           t1.name as home_team_name,
           t2.name as away_team_name
    FROM matches m
    LEFT JOIN teams t1 ON m.home_team_id = t1.id
    LEFT JOIN teams t2 ON m.away_team_id = t2.id
    WHERE m.date >= '2023-01-01'
    ORDER BY m.date
"""

all_matches = pd.read_sql_query(query, conn)
conn.close()

print(f"✅ {len(all_matches)} jogos carregados (2023-2025)")

# Dividir: 70% treino, 30% teste
split_idx = int(len(all_matches) * 0.7)
train_df = all_matches.iloc[:split_idx]
test_df = all_matches.iloc[split_idx:]

cutoff_date = train_df.iloc[-1]['date'] if len(train_df) > 0 else "2024-01-01"

print(f"\n📊 Divisão:")
print(f"  - Treino: {len(train_df)} jogos")
print(f"  - Teste: {len(test_df)} jogos")
print(f"  - Data de corte: {cutoff_date}")

# Criar preditor
print("\n🔮 Gerando previsões...")

predictor = MatchPredictor()

results = []
sample_predictions = []

for idx, match in test_df.head(100).iterrows():  # Testar apenas 100 jogos para ser rápido
    try:
        prediction = predictor.predict_match_score(
            match['home_team_id'],
            match['away_team_id']
        )
        
        real_home = int(match['home_goals'])
        real_away = int(match['away_goals'])
        pred_home = prediction['predicted_home_goals']
        pred_away = prediction['predicted_away_goals']
        
        placar_exato = (pred_home == real_home) and (pred_away == real_away)
        gols_home = (pred_home == real_home)
        gols_away = (pred_away == real_away)
        
        real_result = 'home' if real_home > real_away else ('away' if real_away > real_home else 'draw')
        pred_result = prediction['predicted_result']
        resultado_correto = (real_result == pred_result)
        
        if placar_exato:
            points = 20
        elif resultado_correto and (gols_home or gols_away):
            points = 15
        elif resultado_correto:
            points = 10
        elif gols_home or gols_away:
            points = 5
        else:
            points = 0
        
        results.append({
            'placar_exato': placar_exato,
            'resultado_correto': resultado_correto,
            'points': points
        })
        
        if len(sample_predictions) < 10:
            sample_predictions.append({
                'Jogo': f"{match['home_team_name']} vs {match['away_team_name']}",
                'Real': f"{real_home} x {real_away}",
                'Previsto': f"{pred_home} x {pred_away}",
                'Pontos': points
            })
        
    except:
        continue

# Resultados
print("\n" + "=" * 80)
print("RESULTADOS DO BACKTESTING")
print("=" * 80)

if results:
    df_results = pd.DataFrame(results)
    
    total = len(df_results)
    placar_exato_count = df_results['placar_exato'].sum()
    resultado_count = df_results['resultado_correto'].sum()
    total_points = df_results['points'].sum()
    
    placar_exato_rate = placar_exato_count / total
    resultado_rate = resultado_count / total
    avg_points = total_points / total
    
    print(f"\n📊 Métricas ({total} jogos testados):")
    print(f"  - Placar exato: {placar_exato_rate:.1%} ({placar_exato_count}/{total})")
    print(f"  - Resultado correto: {resultado_rate:.1%} ({resultado_count}/{total})")
    print(f"  - Pontuação média: {avg_points:.1f} pts/jogo")
    print(f"  - Pontuação total: {total_points} pts")
    
    print(f"\n📈 Comparação com Benchmarks:")
    print(f"  - Placar exato: {placar_exato_rate:.1%} (benchmark: 10-15%)")
    print(f"  - Resultado: {resultado_rate:.1%} (benchmark: 50-60%)")
    
    print(f"\n📋 Amostra de Previsões:")
    df_sample = pd.DataFrame(sample_predictions)
    print(df_sample.to_string(index=False))
    
    print(f"\n🏆 PROJEÇÃO PARA O BOLÃO:")
    projected = avg_points * 128
    print(f"  - 128 jogos × {avg_points:.1f} pts = {projected:.0f} pts")
    print(f"  - Com grupos e pódio: ~{projected + 220:.0f} pts")
    
    # Avaliação
    print(f"\n💡 Avaliação:")
    if resultado_rate >= 0.50:
        print(f"  ✅ Modelo está performando BEM!")
        print(f"  ✅ Recomendado para uso no Bolão")
    else:
        print(f"  ⚠️  Modelo precisa de mais dados")
    
    if placar_exato_rate >= 0.10:
        print(f"  ✅ Taxa de placar exato está BOA!")
    
else:
    print("\n❌ Nenhum resultado gerado")

print("\n" + "=" * 80)
