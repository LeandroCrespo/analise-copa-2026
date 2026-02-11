"""
Importar dados históricos do Kaggle para o banco de dados
"""

import sys
sys.path.append('src')

import pandas as pd
from utils import DatabaseManager
from datetime import datetime

print("=" * 80)
print("IMPORTAÇÃO DE DADOS HISTÓRICOS REAIS (KAGGLE)")
print("=" * 80)

# Carregar CSV
csv_path = "data/raw/results.csv"
print(f"\n📂 Carregando {csv_path}...")

df = pd.read_csv(csv_path)
print(f"✅ {len(df)} jogos carregados!")

# Inicializar banco
db = DatabaseManager()

# Filtrar apenas jogos relevantes (últimos 10 anos + seleções principais)
print("\n🔍 Filtrando dados relevantes...")

# Seleções da Copa 2026 (principais)
relevant_teams = [
    'Brazil', 'Argentina', 'France', 'Germany', 'Spain', 'England', 
    'Portugal', 'Netherlands', 'Italy', 'Uruguay', 'Belgium', 'Croatia',
    'Mexico', 'United States', 'Colombia', 'Japan', 'South Korea', 
    'Senegal', 'Morocco', 'Canada', 'Switzerland', 'Denmark', 'Poland',
    'Serbia', 'Wales', 'Australia', 'Iran', 'Saudi Arabia', 'Qatar',
    'Ecuador', 'Peru', 'Chile', 'Costa Rica', 'Jamaica', 'Panama'
]

# Filtrar jogos dos últimos 10 anos
df['date'] = pd.to_datetime(df['date'])
cutoff_date = datetime(2015, 1, 1)
df_filtered = df[df['date'] >= cutoff_date].copy()

# Filtrar apenas jogos com seleções relevantes
df_filtered = df_filtered[
    (df_filtered['home_team'].isin(relevant_teams)) | 
    (df_filtered['away_team'].isin(relevant_teams))
]

print(f"✅ {len(df_filtered)} jogos relevantes (últimos 10 anos, seleções principais)")

# Criar mapeamento de times
print("\n📊 Criando mapeamento de seleções...")

all_teams = set(df_filtered['home_team'].unique()) | set(df_filtered['away_team'].unique())
team_id_map = {}

for idx, team_name in enumerate(sorted(all_teams), start=1):
    team_id_map[team_name] = idx
    db.insert_team(team_id=idx, name=team_name, country=team_name)

print(f"✅ {len(team_id_map)} seleções cadastradas")

# Importar jogos
print("\n📥 Importando jogos para o banco de dados...")

count = 0
for idx, row in df_filtered.iterrows():
    try:
        home_team_id = team_id_map[row['home_team']]
        away_team_id = team_id_map[row['away_team']]
        
        # Usar índice como match_id único
        match_id = idx
        
        db.insert_match(
            match_id=match_id,
            date=row['date'].strftime("%Y-%m-%d"),
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            home_goals=int(row['home_score']),
            away_goals=int(row['away_score']),
            competition=row['tournament'],
            stage=""
        )
        count += 1
        
        if count % 500 == 0:
            print(f"  ⏳ {count} jogos importados...")
            
    except Exception as e:
        continue

print(f"✅ {count} jogos importados com sucesso!")

# Estatísticas finais
print("\n" + "=" * 80)
print("RESUMO DA IMPORTAÇÃO")
print("=" * 80)

import sqlite3
conn = sqlite3.connect(db.db_path)

total_matches = pd.read_sql_query("SELECT COUNT(*) as count FROM matches", conn)
total_teams = pd.read_sql_query("SELECT COUNT(*) as count FROM teams", conn)

# Top 10 seleções com mais jogos
top_teams = pd.read_sql_query("""
    SELECT t.name, COUNT(*) as jogos
    FROM matches m
    JOIN teams t ON (m.home_team_id = t.id OR m.away_team_id = t.id)
    GROUP BY t.name
    ORDER BY jogos DESC
    LIMIT 10
""", conn)

conn.close()

print(f"""
✅ Importação Concluída!

📊 Estatísticas do Banco de Dados:
  - Total de seleções: {total_teams['count'].values[0]}
  - Total de jogos: {total_matches['count'].values[0]}
  - Período: 2015-2025 (últimos 10 anos)
  - Fonte: Kaggle (dados reais)

🏆 Top 10 Seleções com Mais Jogos:
""")

for _, row in top_teams.iterrows():
    print(f"  {row['name']:20s} - {row['jogos']:4d} jogos")

print(f"""
💾 Banco de dados: /home/ubuntu/analise-copa-2026/data/database.db

🚀 Próximos Passos:
  1. Executar backtesting: python backtesting.py
  2. Executar dashboard: streamlit run app/dashboard.py
  3. Gerar previsões para a Copa 2026
""")

print("=" * 80)
