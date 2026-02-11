"""
Módulo de processamento e análise de dados
"""

from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from utils import DatabaseManager, calculate_team_stats, get_logger
from config import RECENT_MATCHES_WINDOW, MIN_MATCHES_FOR_ANALYSIS

logger = get_logger(__name__)


class DataProcessor:
    """Processador de dados para análise"""

    def __init__(self):
        """Inicializar processador"""
        self.db = DatabaseManager()

    def get_team_recent_form(self, team_id: int, window: int = RECENT_MATCHES_WINDOW) -> Dict:
        """
        Calcular forma recente de uma seleção (últimos N jogos)
        
        Args:
            team_id: ID da seleção
            window: Número de jogos recentes a analisar
            
        Returns:
            Dicionário com estatísticas de forma recente
        """
        matches_df = self.db.get_team_matches(team_id, limit=window)
        
        if matches_df.empty or len(matches_df) < MIN_MATCHES_FOR_ANALYSIS:
            logger.warning(f"Seleção {team_id} tem menos de {MIN_MATCHES_FOR_ANALYSIS} jogos")
            return {}

        stats = calculate_team_stats(matches_df, team_id)
        
        return {
            "recent_matches": len(matches_df),
            "recent_wins": stats["wins"],
            "recent_draws": stats["draws"],
            "recent_losses": stats["losses"],
            "recent_win_rate": stats["win_rate"],
            "recent_avg_goals_for": stats["avg_goals_for"],
            "recent_avg_goals_against": stats["avg_goals_against"],
            "recent_goal_difference": stats["goal_difference"],
        }

    def get_team_overall_stats(self, team_id: int) -> Dict:
        """
        Calcular estatísticas gerais de uma seleção
        
        Args:
            team_id: ID da seleção
            
        Returns:
            Dicionário com estatísticas gerais
        """
        matches_df = self.db.get_team_matches(team_id, limit=1000)
        
        if matches_df.empty:
            return {}

        stats = calculate_team_stats(matches_df, team_id)
        
        return {
            "total_matches": stats["total_matches"],
            "overall_wins": stats["wins"],
            "overall_draws": stats["draws"],
            "overall_losses": stats["losses"],
            "overall_win_rate": stats["win_rate"],
            "overall_avg_goals_for": stats["avg_goals_for"],
            "overall_avg_goals_against": stats["avg_goals_against"],
            "overall_goal_difference": stats["goal_difference"],
        }

    def get_head_to_head(self, team1_id: int, team2_id: int) -> Dict:
        """
        Calcular confronto direto entre duas seleções
        
        Args:
            team1_id: ID da primeira seleção
            team2_id: ID da segunda seleção
            
        Returns:
            Dicionário com estatísticas do confronto
        """
        matches_df = self.db.get_team_matches(team1_id, limit=1000)
        
        # Filtrar apenas jogos entre as duas seleções
        h2h_matches = matches_df[
            ((matches_df["home_team_id"] == team1_id) & (matches_df["away_team_id"] == team2_id)) |
            ((matches_df["home_team_id"] == team2_id) & (matches_df["away_team_id"] == team1_id))
        ]
        
        h2h_stats = {
            "total_matches": len(h2h_matches),
            "team1_wins": 0,
            "team1_draws": 0,
            "team1_losses": 0,
            "team1_goals_for": 0,
            "team1_goals_against": 0,
        }
        
        for _, match in h2h_matches.iterrows():
            if match["home_team_id"] == team1_id:
                goals_for = match["home_goals"]
                goals_against = match["away_goals"]
            else:
                goals_for = match["away_goals"]
                goals_against = match["home_goals"]
            
            h2h_stats["team1_goals_for"] += goals_for
            h2h_stats["team1_goals_against"] += goals_against
            
            if goals_for > goals_against:
                h2h_stats["team1_wins"] += 1
            elif goals_for == goals_against:
                h2h_stats["team1_draws"] += 1
            else:
                h2h_stats["team1_losses"] += 1
        
        return h2h_stats

    def calculate_team_strength(self, team_id: int, fifa_rank: Optional[int] = None, 
                               elo_rating: Optional[float] = None) -> float:
        """
        Calcular força geral de uma seleção (0-100)
        
        Args:
            team_id: ID da seleção
            fifa_rank: Ranking FIFA (opcional)
            elo_rating: Rating ELO (opcional)
            
        Returns:
            Score de força (0-100)
        """
        overall_stats = self.get_team_overall_stats(team_id)
        recent_form = self.get_team_recent_form(team_id)
        
        if not overall_stats or not recent_form:
            return 50.0  # Score neutro se não houver dados
        
        # Componentes do score
        win_rate_score = overall_stats.get("overall_win_rate", 0) * 40
        recent_form_score = recent_form.get("recent_win_rate", 0) * 30
        goals_score = min(overall_stats.get("overall_avg_goals_for", 0) / 2 * 20, 20)
        
        # Ajustar por ranking FIFA se disponível
        ranking_bonus = 0
        if fifa_rank:
            # Quanto melhor o ranking (menor número), maior o bônus
            ranking_bonus = max(0, (200 - fifa_rank) / 2)
        
        total_score = win_rate_score + recent_form_score + goals_score + ranking_bonus
        
        # Normalizar para 0-100
        return min(100, max(0, total_score))

    def prepare_match_features(self, home_team_id: int, away_team_id: int) -> Dict:
        """
        Preparar features para previsão de um confronto
        
        Args:
            home_team_id: ID da seleção mandante
            away_team_id: ID da seleção visitante
            
        Returns:
            Dicionário com features do confronto
        """
        # Estatísticas gerais
        home_overall = self.get_team_overall_stats(home_team_id)
        away_overall = self.get_team_overall_stats(away_team_id)
        
        # Forma recente
        home_recent = self.get_team_recent_form(home_team_id)
        away_recent = self.get_team_recent_form(away_team_id)
        
        # Confronto direto
        h2h = self.get_head_to_head(home_team_id, away_team_id)
        
        # Força das seleções
        home_strength = self.calculate_team_strength(home_team_id)
        away_strength = self.calculate_team_strength(away_team_id)
        
        features = {
            # Estatísticas gerais
            "home_overall_win_rate": home_overall.get("overall_win_rate", 0),
            "away_overall_win_rate": away_overall.get("overall_win_rate", 0),
            "home_overall_avg_goals_for": home_overall.get("overall_avg_goals_for", 0),
            "away_overall_avg_goals_for": away_overall.get("overall_avg_goals_for", 0),
            "home_overall_avg_goals_against": home_overall.get("overall_avg_goals_against", 0),
            "away_overall_avg_goals_against": away_overall.get("overall_avg_goals_against", 0),
            
            # Forma recente
            "home_recent_win_rate": home_recent.get("recent_win_rate", 0),
            "away_recent_win_rate": away_recent.get("recent_win_rate", 0),
            "home_recent_avg_goals_for": home_recent.get("recent_avg_goals_for", 0),
            "away_recent_avg_goals_for": away_recent.get("recent_avg_goals_for", 0),
            
            # Confronto direto
            "h2h_total_matches": h2h.get("total_matches", 0),
            "h2h_home_win_rate": h2h.get("team1_wins", 0) / max(1, h2h.get("total_matches", 1)),
            
            # Força relativa
            "home_strength": home_strength,
            "away_strength": away_strength,
            "strength_difference": home_strength - away_strength,
        }
        
        return features

    def get_all_teams_data(self) -> pd.DataFrame:
        """
        Obter dados consolidados de todas as seleções
        
        Returns:
            DataFrame com dados de todas as seleções
        """
        teams_df = self.db.get_all_teams()
        
        if teams_df.empty:
            return pd.DataFrame()
        
        # Adicionar estatísticas para cada seleção
        data = []
        for _, team in teams_df.iterrows():
            team_id = team["id"]
            overall_stats = self.get_team_overall_stats(team_id)
            recent_form = self.get_team_recent_form(team_id)
            strength = self.calculate_team_strength(team_id, team.get("fifa_rank"))
            
            row = {
                "team_id": team_id,
                "team_name": team["name"],
                "country": team.get("country", ""),
                "fifa_rank": team.get("fifa_rank"),
                "elo_rating": team.get("elo_rating"),
                "strength_score": strength,
            }
            
            # Adicionar estatísticas gerais
            row.update({f"overall_{k}": v for k, v in overall_stats.items()})
            
            # Adicionar forma recente
            row.update({f"recent_{k}": v for k, v in recent_form.items()})
            
            data.append(row)
        
        return pd.DataFrame(data)


if __name__ == "__main__":
    processor = DataProcessor()
    teams_data = processor.get_all_teams_data()
    print(teams_data)
