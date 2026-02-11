"""
Funções auxiliares para o projeto
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

import pandas as pd
from config import LOG_LEVEL, LOG_FORMAT, DATABASE_PATH

# Configurar logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """Obter logger configurado"""
    return logging.getLogger(name)


class DatabaseManager:
    """Gerenciador de banco de dados SQLite"""

    def __init__(self, db_path: Path = DATABASE_PATH):
        """Inicializar gerenciador de banco de dados"""
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Inicializar banco de dados com tabelas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabela de seleções
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                country TEXT,
                fifa_rank INTEGER,
                elo_rating REAL,
                last_updated TIMESTAMP
            )
        """)

        # Tabela de jogos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY,
                date TIMESTAMP,
                home_team_id INTEGER,
                away_team_id INTEGER,
                home_goals INTEGER,
                away_goals INTEGER,
                competition TEXT,
                stage TEXT,
                last_updated TIMESTAMP,
                FOREIGN KEY (home_team_id) REFERENCES teams(id),
                FOREIGN KEY (away_team_id) REFERENCES teams(id)
            )
        """)

        # Tabela de previsões
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY,
                match_id INTEGER,
                predicted_home_goals REAL,
                predicted_away_goals REAL,
                predicted_result TEXT,
                confidence REAL,
                confidence_interval_lower REAL,
                confidence_interval_upper REAL,
                created_at TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES matches(id)
            )
        """)

        conn.commit()
        conn.close()
        logger.info(f"Banco de dados inicializado em {self.db_path}")

    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """Executar query SELECT"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Executar query INSERT/UPDATE/DELETE"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected

    def insert_team(self, team_id: int, name: str, country: str, 
                   fifa_rank: Optional[int] = None, elo_rating: Optional[float] = None):
        """Inserir ou atualizar seleção"""
        query = """
            INSERT OR REPLACE INTO teams (id, name, country, fifa_rank, elo_rating, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (team_id, name, country, fifa_rank, elo_rating, datetime.now())
        self.execute_update(query, params)

    def insert_match(self, match_id: int, date: str, home_team_id: int, 
                    away_team_id: int, home_goals: int, away_goals: int,
                    competition: str, stage: str):
        """Inserir ou atualizar jogo"""
        query = """
            INSERT OR REPLACE INTO matches 
            (id, date, home_team_id, away_team_id, home_goals, away_goals, competition, stage, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (match_id, date, home_team_id, away_team_id, home_goals, away_goals, 
                 competition, stage, datetime.now())
        self.execute_update(query, params)

    def get_team_matches(self, team_id: int, limit: int = 100) -> pd.DataFrame:
        """Obter histórico de jogos de uma seleção"""
        query = """
            SELECT m.*, 
                   t1.name as home_team_name,
                   t2.name as away_team_name
            FROM matches m
            LEFT JOIN teams t1 ON m.home_team_id = t1.id
            LEFT JOIN teams t2 ON m.away_team_id = t2.id
            WHERE m.home_team_id = ? OR m.away_team_id = ?
            ORDER BY m.date DESC
            LIMIT ?
        """
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(query, conn, params=(team_id, team_id, limit))
        conn.close()
        return df

    def get_all_teams(self) -> pd.DataFrame:
        """Obter todas as seleções"""
        query = "SELECT * FROM teams ORDER BY fifa_rank"
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df


def calculate_team_stats(matches_df: pd.DataFrame, team_id: int) -> Dict[str, Any]:
    """
    Calcular estatísticas de uma seleção baseado em histórico de jogos
    
    Args:
        matches_df: DataFrame com histórico de jogos
        team_id: ID da seleção
        
    Returns:
        Dicionário com estatísticas
    """
    stats = {
        "total_matches": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
        "win_rate": 0.0,
        "draw_rate": 0.0,
        "loss_rate": 0.0,
        "avg_goals_for": 0.0,
        "avg_goals_against": 0.0,
        "goal_difference": 0,
    }

    if matches_df.empty:
        return stats

    for _, match in matches_df.iterrows():
        stats["total_matches"] += 1

        if match["home_team_id"] == team_id:
            goals_for = match["home_goals"]
            goals_against = match["away_goals"]
        else:
            goals_for = match["away_goals"]
            goals_against = match["home_goals"]

        stats["goals_for"] += goals_for
        stats["goals_against"] += goals_against

        if goals_for > goals_against:
            stats["wins"] += 1
        elif goals_for == goals_against:
            stats["draws"] += 1
        else:
            stats["losses"] += 1

    if stats["total_matches"] > 0:
        stats["win_rate"] = stats["wins"] / stats["total_matches"]
        stats["draw_rate"] = stats["draws"] / stats["total_matches"]
        stats["loss_rate"] = stats["losses"] / stats["total_matches"]
        stats["avg_goals_for"] = stats["goals_for"] / stats["total_matches"]
        stats["avg_goals_against"] = stats["goals_against"] / stats["total_matches"]
        stats["goal_difference"] = stats["goals_for"] - stats["goals_against"]

    return stats


def normalize_team_name(name: str) -> str:
    """Normalizar nome de seleção para comparação"""
    return name.strip().lower()
