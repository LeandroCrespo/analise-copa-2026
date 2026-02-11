-- Schema do Banco de Dados - Análise Copa 2026
-- PostgreSQL (Neon)

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

CREATE INDEX idx_teams_name ON teams(name);
CREATE INDEX idx_teams_country ON teams(country);

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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_different_teams CHECK (home_team_id != away_team_id)
);

CREATE INDEX idx_matches_date ON matches(date DESC);
CREATE INDEX idx_matches_home_team ON matches(home_team_id);
CREATE INDEX idx_matches_away_team ON matches(away_team_id);
CREATE INDEX idx_matches_competition ON matches(competition);
CREATE INDEX idx_matches_status ON matches(status);

-- Tabela de Estatísticas de Times (cache)
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

-- Tabela de Forma Recente (últimos 10 jogos)
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
    predicted_result VARCHAR(10), -- 'home', 'draw', 'away'
    home_goals_expected DECIMAL(4,2),
    away_goals_expected DECIMAL(4,2),
    prob_home_win DECIMAL(5,4),
    prob_draw DECIMAL(5,4),
    prob_away_win DECIMAL(5,4),
    confidence DECIMAL(5,4),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_predictions_match ON predictions(match_id);
CREATE INDEX idx_predictions_created ON predictions(created_at DESC);

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

-- Tabela de Classificação de Grupos (para palpites)
CREATE TABLE IF NOT EXISTS group_predictions (
    id SERIAL PRIMARY KEY,
    group_name CHAR(1) NOT NULL, -- A, B, C, ..., L
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
    update_type VARCHAR(50), -- 'full_sync', 'incremental', 'manual'
    records_added INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    api_requests INTEGER DEFAULT 0,
    status VARCHAR(20), -- 'success', 'partial', 'failed'
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_update_log_started ON update_log(started_at DESC);

-- View: Estatísticas Consolidadas por Time
CREATE OR REPLACE VIEW v_team_statistics AS
SELECT 
    t.id,
    t.name,
    t.country,
    ts.total_matches,
    ts.wins,
    ts.draws,
    ts.losses,
    ts.goals_for,
    ts.goals_against,
    ts.goal_difference,
    ts.win_rate,
    ts.avg_goals_for,
    ts.avg_goals_against,
    ts.strength_score,
    trf.recent_win_rate,
    trf.recent_avg_goals_for,
    ts.last_updated
FROM teams t
LEFT JOIN team_stats ts ON t.id = ts.team_id
LEFT JOIN team_recent_form trf ON t.id = trf.team_id;

-- View: Próximos Jogos (para palpites)
CREATE OR REPLACE VIEW v_upcoming_matches AS
SELECT 
    m.id,
    m.date,
    m.datetime,
    ht.name as home_team,
    at.name as away_team,
    m.competition,
    m.stage,
    m.venue,
    m.status
FROM matches m
JOIN teams ht ON m.home_team_id = ht.id
JOIN teams at ON m.away_team_id = at.id
WHERE m.status IN ('scheduled', 'not_started')
ORDER BY m.date, m.datetime;

-- View: Histórico de Jogos
CREATE OR REPLACE VIEW v_match_history AS
SELECT 
    m.id,
    m.date,
    ht.name as home_team,
    m.home_goals,
    m.away_goals,
    at.name as away_team,
    m.competition,
    m.stage,
    CASE 
        WHEN m.home_goals > m.away_goals THEN ht.name
        WHEN m.away_goals > m.home_goals THEN at.name
        ELSE 'Empate'
    END as winner
FROM matches m
JOIN teams ht ON m.home_team_id = ht.id
JOIN teams at ON m.away_team_id = at.id
WHERE m.status = 'finished'
ORDER BY m.date DESC;

-- Função: Atualizar timestamp de updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar updated_at
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_matches_updated_at BEFORE UPDATE ON matches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comentários nas tabelas
COMMENT ON TABLE teams IS 'Seleções participantes da Copa 2026';
COMMENT ON TABLE matches IS 'Histórico de jogos das seleções';
COMMENT ON TABLE team_stats IS 'Estatísticas gerais de cada seleção (cache)';
COMMENT ON TABLE team_recent_form IS 'Forma recente das seleções (últimos 10 jogos)';
COMMENT ON TABLE predictions IS 'Previsões geradas pelo modelo';
COMMENT ON TABLE user_predictions IS 'Palpites do usuário para os jogos';
COMMENT ON TABLE group_predictions IS 'Palpites de classificação dos grupos';
COMMENT ON TABLE podium_prediction IS 'Palpite de pódio (1º, 2º, 3º)';
COMMENT ON TABLE update_log IS 'Log de atualizações do banco de dados';
