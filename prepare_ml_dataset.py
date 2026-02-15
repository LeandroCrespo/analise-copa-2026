"""
Preparar Dataset para Machine Learning
"""

import json
import pandas as pd
from team_strength import get_team_strength_stats

print("=" * 80)
print("PREPARANDO DATASET PARA MACHINE LEARNING")
print("=" * 80)

# Carregar jogos
print("\n📂 Carregando jogos históricos...")
with open('/home/ubuntu/analise-copa-2026/all_matches.json', 'r') as f:
    content = f.read()
    lines = content.strip().split('\n')
    json_content = '\n'.join(lines[2:])
    matches = json.loads(json_content)

print(f"✅ {len(matches)} jogos carregados")

# Preparar features
print("\n🔧 Extraindo features...")

data = []
skipped = 0

for match in matches:
    home_team = match['home_team']
    away_team = match['away_team']
    home_goals = match['home_goals']
    away_goals = match['away_goals']
    
    try:
        home_stats = get_team_strength_stats(home_team)
        away_stats = get_team_strength_stats(away_team)
    except:
        skipped += 1
        continue
    
    # Features
    features = {
        # Força dos times
        'home_strength': home_stats['strength'],
        'away_strength': away_stats['strength'],
        'strength_diff': home_stats['strength'] - away_stats['strength'],
        
        # Ataque
        'home_attack': home_stats['avg_goals_scored'],
        'away_attack': away_stats['avg_goals_scored'],
        'attack_diff': home_stats['avg_goals_scored'] - away_stats['avg_goals_scored'],
        
        # Defesa
        'home_defense': home_stats['avg_goals_conceded'],
        'away_defense': away_stats['avg_goals_conceded'],
        'defense_diff': home_stats['avg_goals_conceded'] - away_stats['avg_goals_conceded'],
        
        # FIFA
        'home_fifa': home_stats['fifa_ranking'],
        'away_fifa': away_stats['fifa_ranking'],
        'fifa_diff': home_stats['fifa_ranking'] - away_stats['fifa_ranking'],
        
        # Target (placar)
        'score': f"{home_goals}x{away_goals}",
        'home_goals': home_goals,
        'away_goals': away_goals,
        'goal_diff': home_goals - away_goals,
        'total_goals': home_goals + away_goals,
        'result': 'H' if home_goals > away_goals else ('D' if home_goals == away_goals else 'A')
    }
    
    data.append(features)

print(f"✅ {len(data)} jogos processados ({skipped} pulados)")

# Criar DataFrame
df = pd.DataFrame(data)

print(f"\n📊 Dataset shape: {df.shape}")
print(f"\n📊 Distribuição de placares:")
print(df['score'].value_counts().head(20))

print(f"\n📊 Distribuição de resultados:")
print(df['result'].value_counts())

# Salvar
df.to_csv('/home/ubuntu/analise-copa-2026/ml_dataset.csv', index=False)
print(f"\n💾 Dataset salvo: ml_dataset.csv")

print("\n" + "=" * 80)
print("✅ DATASET PREPARADO COM SUCESSO!")
print("=" * 80)
