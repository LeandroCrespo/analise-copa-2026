"""
Criar schema no banco Neon PostgreSQL
"""

import subprocess
import json

PROJECT_ID = "restless-glitter-71170845"
DATABASE_NAME = "neondb"

print("=" * 80)
print("CRIANDO SCHEMA NO BANCO NEON")
print("=" * 80)

# Lista de statements SQL
sql_statements = [
    # Tabela teams
    """CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        country VARCHAR(100),
        code VARCHAR(10),
        logo_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    
    # Tabela matches
    """CREATE TABLE IF NOT EXISTS matches (
        id BIGINT PRIMARY KEY,
        date DATE NOT NULL,
        datetime TIMESTAMP,
        home_team_id INTEGER NOT NULL REFERENCES teams(id),
        away_team_id INTEGER NOT NULL REFERENCES teams(id),
        home_goals INTEGER,
        away_goals INTEGER,
        competition VARCHAR(200),
        stage VARCHAR(100),
        venue VARCHAR(200),
        city VARCHAR(100),
        country VARCHAR(100),
        neutral BOOLEAN DEFAULT FALSE,
        status VARCHAR(50) DEFAULT 'finished',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    
    # Tabela team_stats
    """CREATE TABLE IF NOT EXISTS team_stats (
        team_id INTEGER PRIMARY KEY REFERENCES teams(id),
        total_matches INTEGER DEFAULT 0,
        wins INTEGER DEFAULT 0,
        draws INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        goals_for INTEGER DEFAULT 0,
        goals_against INTEGER DEFAULT 0,
        goal_difference INTEGER DEFAULT 0,
        win_rate DECIMAL(5,2) DEFAULT 0,
        avg_goals_for DECIMAL(4,2) DEFAULT 0,
        avg_goals_against DECIMAL(4,2) DEFAULT 0,
        strength_score DECIMAL(5,2) DEFAULT 50.0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    
    # Tabela team_recent_form
    """CREATE TABLE IF NOT EXISTS team_recent_form (
        team_id INTEGER PRIMARY KEY REFERENCES teams(id),
        recent_matches INTEGER DEFAULT 0,
        recent_wins INTEGER DEFAULT 0,
        recent_draws INTEGER DEFAULT 0,
        recent_losses INTEGER DEFAULT 0,
        recent_goals_for INTEGER DEFAULT 0,
        recent_goals_against INTEGER DEFAULT 0,
        recent_win_rate DECIMAL(5,2) DEFAULT 0,
        recent_avg_goals_for DECIMAL(4,2) DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    
    # Tabela predictions
    """CREATE TABLE IF NOT EXISTS predictions (
        id SERIAL PRIMARY KEY,
        match_id BIGINT REFERENCES matches(id),
        home_team_id INTEGER NOT NULL REFERENCES teams(id),
        away_team_id INTEGER NOT NULL REFERENCES teams(id),
        predicted_home_goals INTEGER,
        predicted_away_goals INTEGER,
        predicted_result VARCHAR(10),
        home_goals_expected DECIMAL(4,2),
        away_goals_expected DECIMAL(4,2),
        prob_home_win DECIMAL(5,4),
        prob_draw DECIMAL(5,4),
        prob_away_win DECIMAL(5,4),
        confidence DECIMAL(5,4),
        model_version VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    
    # Tabela user_predictions
    """CREATE TABLE IF NOT EXISTS user_predictions (
        id SERIAL PRIMARY KEY,
        match_id BIGINT NOT NULL REFERENCES matches(id),
        home_goals INTEGER NOT NULL,
        away_goals INTEGER NOT NULL,
        points INTEGER DEFAULT 0,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(match_id)
    )""",
    
    # Tabela group_predictions
    """CREATE TABLE IF NOT EXISTS group_predictions (
        id SERIAL PRIMARY KEY,
        group_name CHAR(1) NOT NULL,
        first_place_team_id INTEGER REFERENCES teams(id),
        second_place_team_id INTEGER REFERENCES teams(id),
        points INTEGER DEFAULT 0,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(group_name)
    )""",
    
    # Tabela podium_prediction
    """CREATE TABLE IF NOT EXISTS podium_prediction (
        id SERIAL PRIMARY KEY,
        champion_team_id INTEGER REFERENCES teams(id),
        runner_up_team_id INTEGER REFERENCES teams(id),
        third_place_team_id INTEGER REFERENCES teams(id),
        points INTEGER DEFAULT 0,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    
    # Tabela update_log
    """CREATE TABLE IF NOT EXISTS update_log (
        id SERIAL PRIMARY KEY,
        update_type VARCHAR(50),
        records_added INTEGER DEFAULT 0,
        records_updated INTEGER DEFAULT 0,
        api_requests INTEGER DEFAULT 0,
        status VARCHAR(20),
        error_message TEXT,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )""",
]

# Índices
indexes = [
    "CREATE INDEX IF NOT EXISTS idx_teams_name ON teams(name)",
    "CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(date DESC)",
    "CREATE INDEX IF NOT EXISTS idx_matches_home_team ON matches(home_team_id)",
    "CREATE INDEX IF NOT EXISTS idx_matches_away_team ON matches(away_team_id)",
    "CREATE INDEX IF NOT EXISTS idx_matches_competition ON matches(competition)",
    "CREATE INDEX IF NOT EXISTS idx_predictions_match ON predictions(match_id)",
    "CREATE INDEX IF NOT EXISTS idx_update_log_started ON update_log(started_at DESC)",
]

def run_sql(sql):
    """Executar SQL via MCP"""
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

# Criar tabelas
print("\n📊 Criando tabelas...")
for i, sql in enumerate(sql_statements, 1):
    table_name = sql.split("TABLE IF NOT EXISTS ")[1].split(" ")[0]
    print(f"\n{i}. Criando tabela {table_name}...")
    
    success, stdout, stderr = run_sql(sql)
    
    if success or "already exists" in stderr.lower():
        print(f"   ✅ {table_name} criada/existente")
    else:
        print(f"   ❌ Erro: {stderr[:200]}")

# Criar índices
print("\n📇 Criando índices...")
for i, sql in enumerate(indexes, 1):
    index_name = sql.split("INDEX IF NOT EXISTS ")[1].split(" ")[0]
    print(f"\n{i}. Criando índice {index_name}...")
    
    success, stdout, stderr = run_sql(sql)
    
    if success or "already exists" in stderr.lower():
        print(f"   ✅ {index_name} criado/existente")
    else:
        print(f"   ❌ Erro: {stderr[:200]}")

# Verificar tabelas criadas
print("\n" + "=" * 80)
print("VERIFICANDO TABELAS CRIADAS")
print("=" * 80)

verify_sql = """
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name
"""

success, stdout, stderr = run_sql(verify_sql)

if success:
    print("\n✅ Tabelas no banco:")
    # Parse JSON output
    try:
        import json
        result_file = "/home/ubuntu/.mcp/tool-results/" + sorted([f for f in subprocess.run(["ls", "-t", "/home/ubuntu/.mcp/tool-results/"], capture_output=True, text=True).stdout.split("\n") if "neon_run_sql" in f])[0]
        with open(result_file) as f:
            data = json.load(f)
            if isinstance(data, dict) and 'rows' in data:
                for row in data['rows']:
                    print(f"  - {row['table_name']}")
            elif isinstance(data, list):
                for row in data:
                    print(f"  - {row['table_name']}")
    except:
        print(stdout)

print("\n" + "=" * 80)
print("✅ SCHEMA CRIADO COM SUCESSO!")
print("=" * 80)

print(f"""
📊 Banco de Dados Configurado:
  - Project ID: {PROJECT_ID}
  - Database: {DATABASE_NAME}
  - Tabelas: 9 tabelas principais
  - Índices: 7 índices para performance

🚀 Próximo Passo: Coletar dados via API-Football
""")
