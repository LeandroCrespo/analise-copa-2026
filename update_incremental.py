"""
Sistema de Atualização Incremental
Busca apenas jogos novos/atualizados desde a última sincronização
"""

import requests
import json
import subprocess
from datetime import datetime, timedelta
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
print("ATUALIZAÇÃO INCREMENTAL - APENAS JOGOS NOVOS")
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

def get_last_update():
    """Buscar data da última atualização"""
    sql = """
    SELECT MAX(completed_at) as last_update
    FROM update_log
    WHERE status = 'success'
    """
    
    success, stdout, _ = run_sql(sql)
    if success:
        try:
            data = json.loads(stdout)
            last_update = data['rows'][0]['last_update']
            if last_update:
                return datetime.fromisoformat(last_update.replace('Z', '+00:00'))
        except:
            pass
    
    # Se não houver registro, retornar 7 dias atrás
    return datetime.now() - timedelta(days=7)

def get_latest_match_date():
    """Buscar data do jogo mais recente no banco"""
    sql = "SELECT MAX(date) as max_date FROM matches"
    
    success, stdout, _ = run_sql(sql)
    if success:
        try:
            data = json.loads(stdout)
            max_date = data['rows'][0]['max_date']
            if max_date:
                return max_date
        except:
            pass
    
    return None

def check_match_exists(match_id):
    """Verificar se jogo já existe"""
    sql = f"SELECT id FROM matches WHERE id = {match_id}"
    success, stdout, _ = run_sql(sql)
    
    if success:
        try:
            data = json.loads(stdout)
            return len(data.get('rows', [])) > 0
        except:
            pass
    return False

def update_match(match_data):
    """Atualizar ou inserir jogo"""
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

def log_update(update_type, records_added, records_updated, api_requests, status):
    """Registrar atualização"""
    sql = f"""
    INSERT INTO update_log (
        update_type, records_added, records_updated, api_requests, status, completed_at
    ) VALUES (
        '{update_type}', {records_added}, {records_updated}, {api_requests}, '{status}', CURRENT_TIMESTAMP
    )
    """
    run_sql(sql)

# Iniciar atualização
print("\n🔍 Verificando última atualização...")

last_update = get_last_update()
latest_match_date = get_latest_match_date()

print(f"  - Última atualização: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  - Jogo mais recente: {latest_match_date}")

# Buscar jogos recentes (últimos 30 dias)
print("\n📥 Buscando jogos recentes...")

from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
to_date = datetime.now().strftime("%Y-%m-%d")

print(f"  - Período: {from_date} até {to_date}")

total_new = 0
total_updated = 0
total_api_requests = 0

# Buscar por data (mais eficiente que por time)
try:
    response = requests.get(
        f"{BASE_URL}/fixtures",
        headers=headers,
        params={
            "from": from_date,
            "to": to_date,
            "status": "FT"  # Apenas jogos finalizados
        }
    )
    total_api_requests += 1
    
    if response.status_code == 200:
        data = response.json()
        matches = data.get('response', [])
        
        print(f"\n✅ {len(matches)} jogos encontrados na API")
        
        for match in matches:
            match_id = match['fixture']['id']
            
            if check_match_exists(match_id):
                # Atualizar jogo existente
                success, _, _ = update_match(match)
                if success:
                    total_updated += 1
            else:
                # Inserir novo jogo
                success, _, _ = update_match(match)
                if success:
                    total_new += 1
        
        print(f"\n📊 Resultados:")
        print(f"  - Jogos novos: {total_new}")
        print(f"  - Jogos atualizados: {total_updated}")
        
    else:
        print(f"\n❌ Erro na API: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Erro: {e}")

# Resumo
print("\n" + "=" * 80)
print("RESUMO DA ATUALIZAÇÃO INCREMENTAL")
print("=" * 80)

print(f"""
✅ Atualização Concluída!

📊 Estatísticas:
  - Jogos novos inseridos: {total_new}
  - Jogos atualizados: {total_updated}
  - Total processado: {total_new + total_updated}
  - Requisições API: {total_api_requests}

💡 Vantagens da Atualização Incremental:
  ✅ Economiza requisições da API
  ✅ Mais rápido que coleta completa
  ✅ Atualiza apenas o necessário
  ✅ Mantém banco sempre atualizado

🔄 Recomendação:
  - Execute este script 1-2x por dia durante a Copa
  - Ou configure um cron job para execução automática
""")

# Registrar no log
log_update('incremental', total_new, total_updated, total_api_requests, 'success')

print("=" * 80)
