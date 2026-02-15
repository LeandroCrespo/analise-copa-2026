"""
Sistema de Atualização Automática do Banco Neon
Baixa dados do GitHub e atualiza apenas jogos novos
100% automático - zero intervenção manual
"""

import subprocess
import pandas as pd
import json
from datetime import datetime
import os

PROJECT_ID = "restless-glitter-71170845"
DATABASE_NAME = "neondb"
GITHUB_CSV_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
LOCAL_CSV_PATH = "/home/ubuntu/analise-copa-2026/data/raw/results.csv"
LOG_FILE = "/home/ubuntu/analise-copa-2026/auto_update.log"

def log(message):
    """Registra mensagem no log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    with open(LOG_FILE, "a") as f:
        f.write(log_msg + "\n")

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
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return result.returncode == 0, result.stdout

def get_last_match_date():
    """Obtém data do último jogo no banco"""
    sql = "SELECT MAX(date) as last_date FROM matches"
    success, output = run_sql(sql)
    
    if not success:
        log("❌ Erro ao consultar última data")
        return None
    
    try:
        # Parsear output JSON
        lines = output.strip().split('\n')
        for line in lines:
            if '"last_date"' in line:
                # Extrair data do JSON
                import re
                match = re.search(r'"last_date":\s*"([^"]+)"', line)
                if match:
                    date_str = match.group(1).split('T')[0]
                    return datetime.strptime(date_str, "%Y-%m-%d")
        
        log("⚠️  Não foi possível extrair data, assumindo 2026-01-26")
        return datetime(2026, 1, 26)
    except Exception as e:
        log(f"❌ Erro ao parsear data: {e}")
        return datetime(2026, 1, 26)

def download_latest_csv():
    """Baixa CSV mais recente do GitHub"""
    log("📥 Baixando CSV do GitHub...")
    
    cmd = ["wget", "-q", "-O", LOCAL_CSV_PATH, GITHUB_CSV_URL]
    result = subprocess.run(cmd, capture_output=True)
    
    if result.returncode == 0:
        log("✅ CSV baixado com sucesso")
        return True
    else:
        log(f"❌ Erro ao baixar CSV: {result.stderr.decode()}")
        return False

def get_new_matches(last_date):
    """Identifica jogos novos desde a última atualização"""
    log(f"🔍 Buscando jogos após {last_date.strftime('%Y-%m-%d')}...")
    
    df = pd.read_csv(LOCAL_CSV_PATH)
    df['date'] = pd.to_datetime(df['date'])
    
    # Filtrar jogos novos
    df_new = df[df['date'] > last_date].copy()
    
    # Filtrar apenas seleções relevantes (mesma lista do reimport_complete.py)
    relevant_teams = [
        'Brazil', 'Argentina', 'Uruguay', 'Colombia', 'Ecuador', 'Venezuela',
        'Peru', 'Chile', 'Paraguay', 'Bolivia',
        'Germany', 'France', 'Spain', 'England', 'Portugal', 'Netherlands',
        'Italy', 'Belgium', 'Croatia', 'Denmark', 'Switzerland', 'Poland',
        'Serbia', 'Ukraine', 'Sweden', 'Austria', 'Wales', 'Scotland',
        'Czech Republic', 'Turkey', 'Romania', 'Greece', 'Norway', 'Iceland',
        'Republic of Ireland', 'Northern Ireland', 'Slovakia', 'Hungary',
        'Bosnia-Herzegovina', 'Slovenia', 'Albania', 'North Macedonia',
        'Finland', 'Bulgaria', 'Israel',
        'Senegal', 'Morocco', 'Tunisia', 'Cameroon', 'Nigeria', 'Ghana',
        'Algeria', 'Egypt', 'Ivory Coast', 'South Africa', 'Mali',
        'Burkina Faso', 'Congo DR', 'Zambia', 'Kenya', 'Uganda',
        'Japan', 'South Korea', 'Iran', 'Saudi Arabia', 'Australia',
        'Qatar', 'Iraq', 'United Arab Emirates', 'Uzbekistan', 'Jordan',
        'China PR', 'Oman', 'Syria', 'Lebanon', 'India', 'Thailand',
        'Vietnam', 'Indonesia', 'Philippines',
        'United States', 'Mexico', 'Canada', 'Costa Rica', 'Jamaica',
        'Panama', 'Honduras', 'El Salvador', 'Trinidad and Tobago',
        'Guatemala', 'Cuba', 'Haiti', 'Curaçao',
        'New Zealand', 'Tahiti', 'New Caledonia', 'Solomon Islands', 'Fiji'
    ]
    
    df_new = df_new[
        (df_new['home_team'].isin(relevant_teams)) | 
        (df_new['away_team'].isin(relevant_teams))
    ]
    
    log(f"✅ {len(df_new)} jogos novos encontrados")
    return df_new

def get_team_id(team_name):
    """Obtém ID do time no banco"""
    safe_name = team_name.replace("'", "''")
    sql = f"SELECT id FROM teams WHERE name = '{safe_name}' LIMIT 1"
    success, output = run_sql(sql)
    
    if not success:
        return None
    
    try:
        import re
        match = re.search(r'"id":\s*"?(\d+)"?', output)
        if match:
            return int(match.group(1))
        return None
    except:
        return None

def insert_new_matches(df_new):
    """Insere jogos novos no banco"""
    if len(df_new) == 0:
        log("ℹ️  Nenhum jogo novo para inserir")
        return 0
    
    log(f"📥 Inserindo {len(df_new)} jogos novos...")
    
    # Obter próximo ID
    sql = "SELECT COALESCE(MAX(id), 0) + 1 as next_id FROM matches"
    success, output = run_sql(sql)
    
    next_id = 7624  # Fallback
    if success:
        import re
        match = re.search(r'"next_id":\s*"?(\d+)"?', output)
        if match:
            next_id = int(match.group(1))
    
    inserted = 0
    batch_values = []
    BATCH_SIZE = 100
    
    for idx, row in df_new.iterrows():
        try:
            home_id = get_team_id(row['home_team'])
            away_id = get_team_id(row['away_team'])
            
            if not home_id or not away_id:
                log(f"⚠️  Time não encontrado: {row['home_team']} vs {row['away_team']}")
                continue
            
            match_id = next_id + inserted
            date = row['date'].strftime("%Y-%m-%d")
            home_goals = int(row['home_score'])
            away_goals = int(row['away_score'])
            competition = str(row['tournament']).replace("'", "''")[:100]
            city = str(row.get('city', '')).replace("'", "''")[:100] if pd.notna(row.get('city')) else ''
            country = str(row.get('country', '')).replace("'", "''")[:100] if pd.notna(row.get('country')) else ''
            neutral = 'TRUE' if row.get('neutral') == True else 'FALSE'
            
            value = f"""({match_id}, '{date}', {home_id}, {away_id},
                {home_goals}, {away_goals}, '{competition}',
                '{city}', '{country}', {neutral}, 'finished')"""
            
            batch_values.append(value)
            
            if len(batch_values) >= BATCH_SIZE:
                sql = f"""
                INSERT INTO matches (
                    id, date, home_team_id, away_team_id,
                    home_goals, away_goals, competition,
                    city, country, neutral, status
                ) VALUES {', '.join(batch_values)}
                """
                
                if run_sql(sql)[0]:
                    inserted += len(batch_values)
                    log(f"  ✅ {inserted} jogos inseridos...")
                else:
                    log(f"  ❌ Erro ao inserir lote")
                
                batch_values = []
        
        except Exception as e:
            log(f"⚠️  Erro no jogo {idx}: {e}")
            continue
    
    # Inserir últimos jogos
    if batch_values:
        sql = f"""
        INSERT INTO matches (
            id, date, home_team_id, away_team_id,
            home_goals, away_goals, competition,
            city, country, neutral, status
        ) VALUES {', '.join(batch_values)}
        """
        
        if run_sql(sql)[0]:
            inserted += len(batch_values)
    
    log(f"✅ Total inserido: {inserted} jogos")
    return inserted

def main():
    """Processo principal de atualização"""
    log("=" * 80)
    log("ATUALIZAÇÃO AUTOMÁTICA - INÍCIO")
    log("=" * 80)
    
    try:
        # 1. Obter última data do banco
        last_date = get_last_match_date()
        if not last_date:
            log("❌ Erro ao obter última data, abortando")
            return False
        
        log(f"📅 Última data no banco: {last_date.strftime('%Y-%m-%d')}")
        
        # 2. Baixar CSV atualizado
        if not download_latest_csv():
            log("❌ Erro ao baixar CSV, abortando")
            return False
        
        # 3. Identificar jogos novos
        df_new = get_new_matches(last_date)
        
        if len(df_new) == 0:
            log("✅ Banco de dados já está atualizado!")
            return True
        
        # 4. Inserir jogos novos
        inserted = insert_new_matches(df_new)
        
        if inserted > 0:
            log(f"✅ Atualização concluída: {inserted} jogos adicionados")
            return True
        else:
            log("⚠️  Nenhum jogo foi inserido")
            return False
    
    except Exception as e:
        log(f"❌ Erro durante atualização: {e}")
        return False
    
    finally:
        log("=" * 80)
        log("ATUALIZAÇÃO AUTOMÁTICA - FIM")
        log("=" * 80)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
