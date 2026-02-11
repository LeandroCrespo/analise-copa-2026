-- Schema Simplificado - Análise Copa 2026

-- Tabela de Seleções
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(100),
    code VARCHAR(10),
    logo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Jogos
CREATE TABLE IF NOT EXISTS matches (
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
);

-- Tabela de Estatísticas de Times
CREATE TABLE IF NOT EXISTS team_stats (
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
);

-- Tabela de Forma Recente
CREATE TABLE IF NOT EXISTS team_recent_form (
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
);

-- Tabela de Previsões
CREATE TABLE IF NOT EXISTS predictions (
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
);

-- Tabela de Palpites do Usuário
CREATE TABLE IF NOT EXISTS user_predictions (
    id SERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES matches(id),
    home_goals INTEGER NOT NULL,
    away_goals INTEGER NOT NULL,
    points INTEGER DEFAULT 0,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(match_id)
);

-- Tabela de Classificação de Grupos
CREATE TABLE IF NOT EXISTS group_predictions (
    id SERIAL PRIMARY KEY,
    group_name CHAR(1) NOT NULL,
    first_place_team_id INTEGER REFERENCES teams(id),
    second_place_team_id INTEGER REFERENCES teams(id),
    points INTEGER DEFAULT 0,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_name)
);

-- Tabela de Palpite de Pódio
CREATE TABLE IF NOT EXISTS podium_prediction (
    id SERIAL PRIMARY KEY,
    champion_team_id INTEGER REFERENCES teams(id),
    runner_up_team_id INTEGER REFERENCES teams(id),
    third_place_team_id INTEGER REFERENCES teams(id),
    points INTEGER DEFAULT 0,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Log de Atualizações
CREATE TABLE IF NOT EXISTS update_log (
    id SERIAL PRIMARY KEY,
    update_type VARCHAR(50),
    records_added INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    api_requests INTEGER DEFAULT 0,
    status VARCHAR(20),
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_teams_name ON teams(name);
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(date DESC);
CREATE INDEX IF NOT EXISTS idx_matches_home_team ON matches(home_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_away_team ON matches(away_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_competition ON matches(competition);
CREATE INDEX IF NOT EXISTS idx_predictions_match ON predictions(match_id);
CREATE INDEX IF NOT EXISTS idx_update_log_started ON update_log(started_at DESC);
