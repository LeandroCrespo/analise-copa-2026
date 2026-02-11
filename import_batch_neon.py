"""
Importação em Lote Otimizada - Kaggle → Neon
Usa batch inserts para ser mais rápido
"""

import pandas as pd
import subprocess
import json
from datetime import datetime

PROJECT_ID = "restless-glitter-71170845"
DATABASE_NAME = "neondb"
CSV_PATH = "data/raw/results.csv"
BATCH_SIZE = 100

print("=" * 80)
print("IMPORTAÇÃO EM LOTE - KAGGLE → NEON")
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
    'Ecuador', 'Peru', 'Chile', 'Costa Rica', 'Jamaica', 'Panama',
    'Nigeria', 'Cameroon', 'Ghana', 'Tunisia', 'Algeria', 'Egypt',
    'South Africa', 'Ivory Coast', 'Paraguay', 'Venezuela', 'Bolivia',
    'Honduras', 'El Salvador', 'Trinidad and Tobago', 'Guatemala',
    'New Zealand', 'Iraq', 'United Arab Emirates', 'China PR', 'India'
]

# Filtrar últimos 10 anos (2015-2025)
df['date'] = pd.to_datetime(df['date'])
cutoff_date = datetime(2015, 1, 1)
df_filtered = df[df['date'] >= cutoff_date].copy()

# Filtrar seleções relevantes
df_filtered = df_filtered[
    (df_filtered['home_team'].isin(relevant_teams)) | 
    (df_filtered['away_team'].isin(relevant_teams))
]

print(f"✅ {len(df_filtered)} jogos filtrados (2015-2025, seleções relevantes)")

# Criar mapeamento de times
print("\n📊 Criando mapeamento de seleções...")

all_teams = sorted(set(df_filtered['home_team'].unique()) | set(df_filtered['away_team'].unique()))
team_id_map = {}

for idx, team_name in enumerate(all_teams, start=1):
    team_id_map[team_name] = idx

print(f"✅ {len(team_id_map)} seleções mapeadas")

# Inserir seleções em lote
print("\n📥 Inserindo seleções no Neon (em lote)...")

values_list = []
for team_name, team_id in team_id_map.items():
    safe_name = team_name.replace("'", "''")
    values_list.append(f"({team_id}, '{safe_name}', '{safe_name}')")

# Inserir em lotes de 50
for i in range(0, len(values_list), 50):
    batch = values_list[i:i+50]
    sql = f"""
    INSERT INTO teams (id, name, country) 
    VALUES {', '.join(batch)}
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        updated_at = CURRENT_TIMESTAMP
    """
    
    success, _, _ = run_sql(sql)
    if success:
        print(f"  ✅ {min(i+50, len(values_list))}/{len(values_list)} seleções...")

print(f"✅ Todas as seleções inseridas")

# Inserir jogos em lote
print("\n📥 Inserindo jogos no Neon (em lote)...")

total_inserted = 0
batch_values = []

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
        
        value = f"""({match_id}, '{date}', {home_team_id}, {away_team_id},
            {home_goals}, {away_goals}, '{competition}',
            '{city}', '{country}', {neutral}, 'finished')"""
        
        batch_values.append(value)
        
        # Inserir em lotes
        if len(batch_values) >= BATCH_SIZE:
            sql = f"""
            INSERT INTO matches (
                id, date, home_team_id, away_team_id,
                home_goals, away_goals, competition,
                city, country, neutral, status
            ) VALUES {', '.join(batch_values)}
            ON CONFLICT (id) DO NOTHING
            """
            
            success, _, _ = run_sql(sql)
            if success:
                total_inserted += len(batch_values)
                print(f"  ⏳ {total_inserted} jogos inseridos...")
            
            batch_values = []
            
    except Exception as e:
        continue

# Inserir últimos jogos restantes
if batch_values:
    sql = f"""
    INSERT INTO matches (
        id, date, home_team_id, away_team_id,
        home_goals, away_goals, competition,
        city, country, neutral, status
    ) VALUES {', '.join(batch_values)}
    ON CONFLICT (id) DO NOTHING
    """
    
    success, _, _ = run_sql(sql)
    if success:
        total_inserted += len(batch_values)

print(f"✅ {total_inserted} jogos inseridos")

# Verificar dados finais
print("\n" + "=" * 80)
print("VERIFICANDO DADOS FINAIS")
print("=" * 80)

# Total de jogos
sql_count = "SELECT COUNT(*) as total FROM matches"
success, stdout, _ = run_sql(sql_count)
if success:
    try:
        data = json.loads(stdout)
        total = data['rows'][0]['total']
        print(f"\n✅ Total de jogos no banco: {total}")
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

# Período dos dados
sql_period = "SELECT MIN(date) as inicio, MAX(date) as fim FROM matches"
success, stdout, _ = run_sql(sql_period)
if success:
    try:
        data = json.loads(stdout)
        inicio = data['rows'][0]['inicio'][:10]
        fim = data['rows'][0]['fim'][:10]
        print(f"\n📅 Período dos dados: {inicio} até {fim}")
    except:
        pass

print("\n" + "=" * 80)
print("✅ IMPORTAÇÃO COMPLETA!")
print("=" * 80)

print(f"""
📊 Resumo Final:
  - Seleções: {len(team_id_map)}
  - Jogos: {total_inserted}
  - Período: 2015-2025
  - Fonte: Kaggle (dados reais)

💾 Banco: Neon PostgreSQL
  - Project ID: {PROJECT_ID}
  - Database: {DATABASE_NAME}

🚀 Próximo Passo: Executar backtesting com dados reais!
""")

print("=" * 80)
