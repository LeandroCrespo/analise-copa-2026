"""
Importar dados históricos do Kaggle para Neon PostgreSQL
"""

import pandas as pd
import subprocess
import json
from datetime import datetime

PROJECT_ID = "restless-glitter-71170845"
DATABASE_NAME = "neondb"
CSV_PATH = "data/raw/results.csv"

print("=" * 80)
print("IMPORTAÇÃO DE DADOS KAGGLE → NEON")
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
    return result.returncode == 0, result.stdout, result.stderr

# Carregar CSV
print(f"\n📂 Carregando {CSV_PATH}...")
df = pd.read_csv(CSV_PATH)
print(f"✅ {len(df)} jogos carregados")

# Filtrar dados relevantes
print("\n🔍 Filtrando dados relevantes...")

relevant_teams = [
    'Brazil', 'Argentina', 'France', 'Germany', 'Spain', 'England', 
    'Portugal', 'Netherlands', 'Italy', 'Uruguay', 'Belgium', 'Croatia',
    'Mexico', 'United States', 'Colombia', 'Japan', 'South Korea', 
    'Senegal', 'Morocco', 'Canada', 'Switzerland', 'Denmark', 'Poland',
    'Serbia', 'Wales', 'Australia', 'Iran', 'Saudi Arabia', 'Qatar',
    'Ecuador', 'Peru', 'Chile', 'Costa Rica', 'Jamaica', 'Panama'
]

# Filtrar últimos 10 anos
df['date'] = pd.to_datetime(df['date'])
cutoff_date = datetime(2015, 1, 1)
df_filtered = df[df['date'] >= cutoff_date].copy()

# Filtrar seleções relevantes
df_filtered = df_filtered[
    (df_filtered['home_team'].isin(relevant_teams)) | 
    (df_filtered['away_team'].isin(relevant_teams))
]

print(f"✅ {len(df_filtered)} jogos filtrados (2015-2025)")

# Criar mapeamento de times
print("\n📊 Criando mapeamento de seleções...")

all_teams = sorted(set(df_filtered['home_team'].unique()) | set(df_filtered['away_team'].unique()))
team_id_map = {}

for idx, team_name in enumerate(all_teams, start=1):
    team_id_map[team_name] = idx

print(f"✅ {len(team_id_map)} seleções mapeadas")

# Inserir seleções
print("\n📥 Inserindo seleções no Neon...")

teams_inserted = 0
for team_name, team_id in team_id_map.items():
    sql = f"""
    INSERT INTO teams (id, name, country) 
    VALUES ({team_id}, '{team_name.replace("'", "''")}', '{team_name.replace("'", "''")}')
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        updated_at = CURRENT_TIMESTAMP
    """
    
    success, _, _ = run_sql(sql)
    if success:
        teams_inserted += 1
        if teams_inserted % 10 == 0:
            print(f"  ⏳ {teams_inserted} seleções...")

print(f"✅ {teams_inserted} seleções inseridas")

# Inserir jogos
print("\n📥 Inserindo jogos no Neon...")

matches_inserted = 0
batch_size = 50

for idx, row in df_filtered.iterrows():
    try:
        home_team_id = team_id_map[row['home_team']]
        away_team_id = team_id_map[row['away_team']]
        
        match_id = idx
        date = row['date'].strftime("%Y-%m-%d")
        home_goals = int(row['home_score'])
        away_goals = int(row['away_score'])
        competition = row['tournament'].replace("'", "''")
        city = row.get('city', '').replace("'", "''") if pd.notna(row.get('city')) else ''
        country = row.get('country', '').replace("'", "''") if pd.notna(row.get('country')) else ''
        neutral = 'TRUE' if row.get('neutral') == True else 'FALSE'
        
        sql = f"""
        INSERT INTO matches (
            id, date, home_team_id, away_team_id,
            home_goals, away_goals, competition,
            city, country, neutral, status
        ) VALUES (
            {match_id}, '{date}', {home_team_id}, {away_team_id},
            {home_goals}, {away_goals}, '{competition}',
            '{city}', '{country}', {neutral}, 'finished'
        )
        ON CONFLICT (id) DO NOTHING
        """
        
        success, _, _ = run_sql(sql)
        if success:
            matches_inserted += 1
            
            if matches_inserted % 100 == 0:
                print(f"  ⏳ {matches_inserted} jogos...")
                
    except Exception as e:
        continue

print(f"✅ {matches_inserted} jogos inseridos")

# Verificar dados
print("\n" + "=" * 80)
print("VERIFICANDO DADOS NO NEON")
print("=" * 80)

# Contar times
sql_teams = "SELECT COUNT(*) as count FROM teams"
success, stdout, _ = run_sql(sql_teams)
if success:
    try:
        data = json.loads(stdout)
        count = data['rows'][0]['count']
        print(f"\n✅ Total de seleções: {count}")
    except:
        pass

# Contar jogos
sql_matches = "SELECT COUNT(*) as count FROM matches"
success, stdout, _ = run_sql(sql_matches)
if success:
    try:
        data = json.loads(stdout)
        count = data['rows'][0]['count']
        print(f"✅ Total de jogos: {count}")
    except:
        pass

# Top 10 seleções
sql_top = """
SELECT t.name, COUNT(*) as jogos
FROM matches m
JOIN teams t ON (m.home_team_id = t.id OR m.away_team_id = t.id)
GROUP BY t.name
ORDER BY jogos DESC
LIMIT 10
"""

success, stdout, _ = run_sql(sql_top)
if success:
    try:
        data = json.loads(stdout)
        print(f"\n🏆 Top 10 Seleções com Mais Jogos:")
        for row in data['rows']:
            print(f"  {row['name']:20s} - {row['jogos']:4d} jogos")
    except:
        pass

# Registrar no log
sql_log = f"""
INSERT INTO update_log (
    update_type, records_added, api_requests, status, completed_at
) VALUES (
    'kaggle_import', {matches_inserted}, 0, 'success', CURRENT_TIMESTAMP
)
"""
run_sql(sql_log)

print("\n" + "=" * 80)
print("✅ IMPORTAÇÃO CONCLUÍDA!")
print("=" * 80)

print(f"""
📊 Resumo:
  - Seleções: {teams_inserted}
  - Jogos: {matches_inserted}
  - Período: 2015-2025
  - Fonte: Kaggle (dados reais)

💾 Banco: Neon PostgreSQL
  - Project ID: {PROJECT_ID}
  - Database: {DATABASE_NAME}

🚀 Próximos Passos:
  1. Calcular estatísticas
  2. Executar backtesting
  3. Gerar previsões
""")

print("=" * 80)
