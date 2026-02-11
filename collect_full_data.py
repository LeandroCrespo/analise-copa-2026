"""
Coleta Completa de Dados via API-Football para Neon PostgreSQL
Sistema inteligente que coleta apenas dados novos
"""

import requests
import json
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import os
import time

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"
PROJECT_ID = "restless-glitter-71170845"
DATABASE_NAME = "neondb"

headers = {
    'x-rapidapi-host': 'v3.football.api-sports.io',
    'x-rapidapi-key': API_KEY
}

print("=" * 80)
print("COLETA COMPLETA DE DADOS - API-FOOTBALL → NEON")
print("=" * 80)

# Seleções da Copa 2026 (48 participantes)
# IDs corretos da API-Football
TEAMS = {
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
    "Mexico": 16,
    "United States": 4,
    "Colombia": 8,
    "Japan": 12,
    "South Korea": 17,
    "Senegal": 13,
    "Morocco": 31,
    "Canada": 5,
    "Switzerland": 15,
    "Denmark": 21,
    "Poland": 24,
    "Serbia": 14,
    "Wales": 1569,
    "Australia": 20,
    "Iran": 22,
    "Saudi Arabia": 23,
    "Qatar": 1569,
    "Ecuador": 2382,
}

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

def insert_team(team_id, name, country):
    """Inserir seleção no banco"""
    sql = f"""
    INSERT INTO teams (id, name, country) 
    VALUES ({team_id}, '{name}', '{country}')
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        country = EXCLUDED.country,
        updated_at = CURRENT_TIMESTAMP
    """
    return run_sql(sql)

def check_match_exists(match_id):
    """Verificar se jogo já existe no banco"""
    sql = f"SELECT id FROM matches WHERE id = {match_id}"
    success, stdout, stderr = run_sql(sql)
    
    if success and "rows" in stdout:
        try:
            data = json.loads(stdout)
            return len(data.get('rows', [])) > 0
        except:
            pass
    return False

def insert_match(match_data):
    """Inserir jogo no banco"""
    fixture = match_data['fixture']
    teams = match_data['teams']
    goals = match_data['goals']
    league = match_data['league']
    
    match_id = fixture['id']
    date = fixture['date'][:10]
    datetime_str = fixture['date']
    home_team_id = teams['home']['id']
    away_team_id = teams['away']['id']
    home_goals = goals['home'] if goals['home'] is not None else 0
    away_goals = goals['away'] if goals['away'] is not None else 0
    competition = league['name'].replace("'", "''")
    stage = league.get('round', '').replace("'", "''")
    venue = fixture.get('venue', {}).get('name', '').replace("'", "''") if fixture.get('venue') else ''
    city = fixture.get('venue', {}).get('city', '').replace("'", "''") if fixture.get('venue') else ''
    status = fixture['status']['short']
    
    sql = f"""
    INSERT INTO matches (
        id, date, datetime, home_team_id, away_team_id,
        home_goals, away_goals, competition, stage,
        venue, city, status
    ) VALUES (
        {match_id}, '{date}', '{datetime_str}', {home_team_id}, {away_team_id},
        {home_goals}, {away_goals}, '{competition}', '{stage}',
        '{venue}', '{city}', '{status}'
    )
    ON CONFLICT (id) DO UPDATE SET
        home_goals = EXCLUDED.home_goals,
        away_goals = EXCLUDED.away_goals,
        status = EXCLUDED.status,
        updated_at = CURRENT_TIMESTAMP
    """
    
    return run_sql(sql)

def log_update(update_type, records_added, api_requests, status):
    """Registrar atualização no log"""
    sql = f"""
    INSERT INTO update_log (
        update_type, records_added, api_requests, status, completed_at
    ) VALUES (
        '{update_type}', {records_added}, {api_requests}, '{status}', CURRENT_TIMESTAMP
    )
    """
    run_sql(sql)

# Iniciar coleta
print(f"\n📊 Seleções a coletar: {len(TEAMS)}")
print(f"⏱️  Tempo estimado: 10-15 minutos")
print(f"🔑 API Key: {API_KEY[:10]}...\n")

total_teams_added = 0
total_matches_added = 0
total_api_requests = 0
start_time = datetime.now()

# Passo 1: Inserir todas as seleções
print("=" * 80)
print("PASSO 1: INSERINDO SELEÇÕES NO BANCO")
print("=" * 80)

for name, team_id in TEAMS.items():
    success, _, _ = insert_team(team_id, name, name)
    if success:
        total_teams_added += 1
        print(f"✅ {name} (ID: {team_id})")
    else:
        print(f"⚠️  {name} - erro ao inserir")
    time.sleep(0.1)

print(f"\n✅ {total_teams_added}/{len(TEAMS)} seleções inseridas")

# Passo 2: Coletar jogos de cada seleção
print("\n" + "=" * 80)
print("PASSO 2: COLETANDO JOGOS DAS SELEÇÕES")
print("=" * 80)

for name, team_id in TEAMS.items():
    print(f"\n🔄 {name}...")
    
    try:
        # Buscar últimos 100 jogos
        response = requests.get(
            f"{BASE_URL}/fixtures",
            headers=headers,
            params={"team": team_id, "last": 100}
        )
        total_api_requests += 1
        
        if response.status_code != 200:
            print(f"   ❌ Erro na API: {response.status_code}")
            continue
        
        data = response.json()
        matches = data.get('response', [])
        
        if not matches:
            print(f"   ⚠️  Nenhum jogo encontrado")
            continue
        
        new_matches = 0
        for match in matches:
            match_id = match['fixture']['id']
            
            # Verificar se já existe
            if not check_match_exists(match_id):
                success, _, _ = insert_match(match)
                if success:
                    new_matches += 1
        
        total_matches_added += new_matches
        print(f"   ✅ {new_matches} jogos novos inseridos ({len(matches)} total)")
        
        # Delay para respeitar rate limit
        time.sleep(0.5)
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        continue

# Finalizar
end_time = datetime.now()
duration = (end_time - start_time).total_seconds()

print("\n" + "=" * 80)
print("RESUMO DA COLETA")
print("=" * 80)

print(f"""
✅ Coleta Concluída!

📊 Estatísticas:
  - Seleções inseridas: {total_teams_added}
  - Jogos novos inseridos: {total_matches_added}
  - Requisições API: {total_api_requests}
  - Duração: {duration:.0f} segundos ({duration/60:.1f} minutos)

💾 Banco de Dados:
  - Project ID: {PROJECT_ID}
  - Database: {DATABASE_NAME}
  - Tipo: Neon PostgreSQL

🚀 Próximos Passos:
  1. Calcular estatísticas das seleções
  2. Executar backtesting
  3. Gerar previsões
""")

# Registrar no log
log_update('full_sync', total_matches_added, total_api_requests, 'success')

print("=" * 80)
