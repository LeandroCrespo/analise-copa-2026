"""
Preparar Dataset V2 com Features Categóricas de Força
"""

import json
import pandas as pd
from team_strength import get_team_strength_stats

def categorize_strength(strength):
    """Categorizar força em 5 níveis"""
    if strength < 20:
        return 'Muito Fraca'
    elif strength < 40:
        return 'Fraca'
    elif strength < 60:
        return 'Média'
    elif strength < 80:
        return 'Forte'
    else:
        return 'Muito Forte'

def get_matchup_type(home_cat, away_cat):
    """Tipo de confronto baseado nas categorias"""
    return f"{home_cat} vs {away_cat}"

print("=" * 80)
print("PREPARANDO DATASET V2 COM FEATURES CATEGÓRICAS")
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
print("\n🔧 Extraindo features com categorias...")

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
    
    # Categorias de força
    home_category = categorize_strength(home_stats['strength'])
    away_category = categorize_strength(away_stats['strength'])
    matchup_type = get_matchup_type(home_category, away_category)
    
    # Features
    features = {
        # Força dos times (numérica)
        'home_strength': home_stats['strength'],
        'away_strength': away_stats['strength'],
        'strength_diff': home_stats['strength'] - away_stats['strength'],
        
        # Força dos times (categórica) ✨ NOVO
        'home_category': home_category,
        'away_category': away_category,
        'matchup_type': matchup_type,
        
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

print(f"\n📊 Distribuição de categorias HOME:")
print(df['home_category'].value_counts())

print(f"\n📊 Distribuição de categorias AWAY:")
print(df['away_category'].value_counts())

print(f"\n📊 Top 10 tipos de confronto:")
print(df['matchup_type'].value_counts().head(10))

# Analisar placares por tipo de confronto
print(f"\n📊 Placares mais comuns por tipo de confronto:")
for matchup in ['Muito Forte vs Muito Fraca', 'Muito Forte vs Fraca', 'Forte vs Média', 'Média vs Média']:
    if matchup in df['matchup_type'].values:
        subset = df[df['matchup_type'] == matchup]
        print(f"\n{matchup} ({len(subset)} jogos):")
        print(subset['score'].value_counts().head(5))

# Salvar
df.to_csv('/home/ubuntu/analise-copa-2026/ml_dataset_v2.csv', index=False)
print(f"\n💾 Dataset V2 salvo: ml_dataset_v2.csv")

print("\n" + "=" * 80)
print("✅ DATASET V2 PREPARADO COM SUCESSO!")
print("=" * 80)
