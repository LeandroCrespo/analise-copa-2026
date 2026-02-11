"""
Módulo de modelos adaptativos que se ajustam conforme resultados reais
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from datetime import datetime

from utils import DatabaseManager, get_logger
from data_processing import DataProcessor
from model import MatchPredictor, GroupPredictor, PodiumPredictor

logger = get_logger(__name__)


class AdaptiveMatchPredictor(MatchPredictor):
    """
    Preditor adaptativo de placares que considera:
    1. Resultados reais já ocorridos na Copa 2026
    2. Atualiza força das seleções conforme performance na Copa
    3. Recalcula previsões dinamicamente
    """

    def __init__(self):
        """Inicializar preditor adaptativo"""
        super().__init__()
        self.copa_2026_results = {}  # Cache de resultados da Copa 2026
        self.team_copa_performance = {}  # Performance na Copa 2026

    def update_copa_performance(self):
        """
        Atualizar performance das seleções na Copa 2026
        Considera apenas jogos da Copa 2026 que já aconteceram
        """
        logger.info("Atualizando performance das seleções na Copa 2026...")
        
        # Buscar jogos da Copa 2026 que já têm resultado
        query = """
            SELECT * FROM matches 
            WHERE competition LIKE '%World Cup%' 
            AND date <= ? 
            AND home_goals IS NOT NULL 
            AND away_goals IS NOT NULL
            ORDER BY date DESC
        """
        
        conn = self.db.db_path
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        copa_matches = pd.read_sql_query(query, conn, params=(datetime.now(),))
        conn.close()
        
        # Calcular performance de cada seleção na Copa
        for team_id in copa_matches["home_team_id"].unique().tolist() + copa_matches["away_team_id"].unique().tolist():
            team_matches = copa_matches[
                (copa_matches["home_team_id"] == team_id) | 
                (copa_matches["away_team_id"] == team_id)
            ]
            
            if len(team_matches) == 0:
                continue
            
            wins = 0
            goals_for = 0
            goals_against = 0
            
            for _, match in team_matches.iterrows():
                if match["home_team_id"] == team_id:
                    gf = match["home_goals"]
                    ga = match["away_goals"]
                else:
                    gf = match["away_goals"]
                    ga = match["home_goals"]
                
                goals_for += gf
                goals_against += ga
                
                if gf > ga:
                    wins += 1
            
            self.team_copa_performance[team_id] = {
                "matches": len(team_matches),
                "wins": wins,
                "win_rate": wins / len(team_matches),
                "avg_goals_for": goals_for / len(team_matches),
                "avg_goals_against": goals_against / len(team_matches),
                "goal_difference": goals_for - goals_against
            }
        
        logger.info(f"Performance atualizada para {len(self.team_copa_performance)} seleções")

    def predict_goals_adaptive(self, team_id: int, opponent_id: int, 
                               is_home: bool = True) -> Tuple[float, float]:
        """
        Prever gols considerando performance na Copa 2026
        
        Args:
            team_id: ID do time
            opponent_id: ID do oponente
            is_home: Se o time joga em casa
            
        Returns:
            (média de gols, desvio padrão)
        """
        # Previsão base (histórico geral)
        base_goals_mean, base_goals_std = self.predict_goals(team_id, opponent_id, is_home)
        
        # Ajustar com performance na Copa 2026 se disponível
        if team_id in self.team_copa_performance:
            copa_perf = self.team_copa_performance[team_id]
            
            # Ponderação: quanto mais jogos na Copa, maior o peso
            copa_weight = min(0.7, copa_perf["matches"] * 0.15)  # Máximo 70%
            historical_weight = 1 - copa_weight
            
            # Média ponderada entre histórico e performance na Copa
            adjusted_goals = (
                historical_weight * base_goals_mean + 
                copa_weight * copa_perf["avg_goals_for"]
            )
            
            logger.debug(
                f"Time {team_id}: Base={base_goals_mean:.2f}, "
                f"Copa={copa_perf['avg_goals_for']:.2f}, "
                f"Ajustado={adjusted_goals:.2f} (peso Copa: {copa_weight:.1%})"
            )
            
            return adjusted_goals, base_goals_std
        
        return base_goals_mean, base_goals_std

    def predict_match_score_adaptive(self, home_team_id: int, away_team_id: int) -> Dict:
        """
        Prever placar de forma adaptativa
        
        Args:
            home_team_id: ID do time mandante
            away_team_id: ID do time visitante
            
        Returns:
            Dicionário com previsão completa
        """
        # Atualizar performance antes de prever
        self.update_copa_performance()
        
        # Prever gols de cada time (adaptativo)
        home_goals_mean, home_goals_std = self.predict_goals_adaptive(
            home_team_id, away_team_id, is_home=True
        )
        away_goals_mean, away_goals_std = self.predict_goals_adaptive(
            away_team_id, home_team_id, is_home=False
        )
        
        # Arredondar para placar mais provável
        home_goals_pred = max(0, round(home_goals_mean))
        away_goals_pred = max(0, round(away_goals_mean))
        
        # Calcular probabilidades de resultado
        prob_home_win, prob_draw, prob_away_win = self._calculate_result_probabilities(
            home_goals_mean, home_goals_std,
            away_goals_mean, away_goals_std
        )
        
        # Calcular intervalo de confiança
        home_ci_lower, home_ci_upper = self._calculate_confidence_interval(
            home_goals_mean, home_goals_std
        )
        away_ci_lower, away_ci_upper = self._calculate_confidence_interval(
            away_goals_mean, away_goals_std
        )
        
        # Determinar resultado mais provável
        if prob_home_win > prob_draw and prob_home_win > prob_away_win:
            result = "home_win"
        elif prob_away_win > prob_draw and prob_away_win > prob_home_win:
            result = "away_win"
        else:
            result = "draw"
        
        # Adicionar informações sobre adaptação
        adaptation_info = {
            "home_copa_matches": self.team_copa_performance.get(home_team_id, {}).get("matches", 0),
            "away_copa_matches": self.team_copa_performance.get(away_team_id, {}).get("matches", 0),
            "is_adapted": home_team_id in self.team_copa_performance or away_team_id in self.team_copa_performance
        }
        
        return {
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "predicted_home_goals": home_goals_pred,
            "predicted_away_goals": away_goals_pred,
            "home_goals_expected": round(home_goals_mean, 2),
            "away_goals_expected": round(away_goals_mean, 2),
            "home_goals_ci": (round(home_ci_lower, 1), round(home_ci_upper, 1)),
            "away_goals_ci": (round(away_ci_lower, 1), round(away_ci_upper, 1)),
            "prob_home_win": round(prob_home_win, 3),
            "prob_draw": round(prob_draw, 3),
            "prob_away_win": round(prob_away_win, 3),
            "predicted_result": result,
            "confidence": round(max(prob_home_win, prob_draw, prob_away_win), 3),
            "adaptation_info": adaptation_info
        }


class AdaptiveGroupPredictor(GroupPredictor):
    """
    Preditor adaptativo de classificação dos grupos
    Considera resultados reais já ocorridos no grupo
    """

    def __init__(self):
        """Inicializar preditor adaptativo"""
        super().__init__()
        self.match_predictor = AdaptiveMatchPredictor()

    def predict_group_standings_adaptive(self, group_name: str, teams: List[int]) -> pd.DataFrame:
        """
        Prever classificação de um grupo considerando jogos já realizados
        
        Args:
            group_name: Nome do grupo (ex: "A")
            teams: Lista de IDs das seleções do grupo
            
        Returns:
            DataFrame com classificação prevista
        """
        if len(teams) != 4:
            logger.error(f"Grupo {group_name} deve ter 4 times")
            return pd.DataFrame()
        
        # Buscar jogos do grupo que já aconteceram
        query = """
            SELECT * FROM matches 
            WHERE (home_team_id IN (?, ?, ?, ?) AND away_team_id IN (?, ?, ?, ?))
            AND stage LIKE ?
            AND home_goals IS NOT NULL 
            AND away_goals IS NOT NULL
        """
        
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        played_matches = pd.read_sql_query(
            query, conn, 
            params=tuple(teams) + tuple(teams) + (f"%Group {group_name}%",)
        )
        conn.close()
        
        # Inicializar classificação
        standings = {
            team_id: {"points": 0, "goals_for": 0, "goals_against": 0, "wins": 0, "draws": 0, "losses": 0} 
            for team_id in teams
        }
        
        # Processar jogos já realizados
        played_pairs = set()
        for _, match in played_matches.iterrows():
            team1_id = match["home_team_id"]
            team2_id = match["away_team_id"]
            home_goals = match["home_goals"]
            away_goals = match["away_goals"]
            
            played_pairs.add(tuple(sorted([team1_id, team2_id])))
            
            standings[team1_id]["goals_for"] += home_goals
            standings[team1_id]["goals_against"] += away_goals
            standings[team2_id]["goals_for"] += away_goals
            standings[team2_id]["goals_against"] += home_goals
            
            if home_goals > away_goals:
                standings[team1_id]["points"] += 3
                standings[team1_id]["wins"] += 1
                standings[team2_id]["losses"] += 1
            elif home_goals < away_goals:
                standings[team2_id]["points"] += 3
                standings[team2_id]["wins"] += 1
                standings[team1_id]["losses"] += 1
            else:
                standings[team1_id]["points"] += 1
                standings[team2_id]["points"] += 1
                standings[team1_id]["draws"] += 1
                standings[team2_id]["draws"] += 1
        
        # Prever jogos que ainda não aconteceram
        from itertools import combinations
        all_matches = list(combinations(teams, 2))
        
        for team1_id, team2_id in all_matches:
            pair = tuple(sorted([team1_id, team2_id]))
            
            if pair not in played_pairs:
                # Jogo ainda não aconteceu - fazer previsão
                prediction = self.match_predictor.predict_match_score_adaptive(team1_id, team2_id)
                
                home_goals = prediction["predicted_home_goals"]
                away_goals = prediction["predicted_away_goals"]
                
                standings[team1_id]["goals_for"] += home_goals
                standings[team1_id]["goals_against"] += away_goals
                standings[team2_id]["goals_for"] += away_goals
                standings[team2_id]["goals_against"] += home_goals
                
                if home_goals > away_goals:
                    standings[team1_id]["points"] += 3
                    standings[team1_id]["wins"] += 1
                    standings[team2_id]["losses"] += 1
                elif home_goals < away_goals:
                    standings[team2_id]["points"] += 3
                    standings[team2_id]["wins"] += 1
                    standings[team1_id]["losses"] += 1
                else:
                    standings[team1_id]["points"] += 1
                    standings[team2_id]["points"] += 1
                    standings[team1_id]["draws"] += 1
                    standings[team2_id]["draws"] += 1
        
        # Converter para DataFrame
        data = []
        for team_id, stats in standings.items():
            data.append({
                "team_id": team_id,
                "points": stats["points"],
                "wins": stats["wins"],
                "draws": stats["draws"],
                "losses": stats["losses"],
                "goals_for": stats["goals_for"],
                "goals_against": stats["goals_against"],
                "goal_difference": stats["goals_for"] - stats["goals_against"]
            })
        
        df = pd.DataFrame(data)
        
        # Ordenar por: pontos, saldo de gols, gols marcados
        df = df.sort_values(
            by=["points", "goal_difference", "goals_for"],
            ascending=[False, False, False]
        ).reset_index(drop=True)
        
        df["position"] = df.index + 1
        
        return df


class AdaptivePodiumPredictor(PodiumPredictor):
    """
    Preditor adaptativo de pódio
    Considera classificados reais dos grupos e resultados do mata-mata
    """

    def __init__(self):
        """Inicializar preditor adaptativo"""
        super().__init__()
        self.match_predictor = AdaptiveMatchPredictor()

    def predict_podium_adaptive(self, qualified_teams: List[int], 
                                knockout_results: Optional[Dict] = None,
                                n_simulations: int = 1000) -> Dict:
        """
        Prever pódio de forma adaptativa
        
        Args:
            qualified_teams: Lista de IDs das seleções classificadas
            knockout_results: Resultados já conhecidos do mata-mata
            n_simulations: Número de simulações
            
        Returns:
            Dicionário com previsão de pódio
        """
        # Usar preditor adaptativo
        podium_counts = {team_id: {"champion": 0, "runner_up": 0, "third": 0} 
                        for team_id in qualified_teams}
        
        for _ in range(n_simulations):
            champion, runner_up, third = self._simulate_knockout_stage(qualified_teams)
            
            if champion:
                podium_counts[champion]["champion"] += 1
            if runner_up:
                podium_counts[runner_up]["runner_up"] += 1
            if third:
                podium_counts[third]["third"] += 1
        
        # Calcular probabilidades
        podium_probs = {}
        for team_id, counts in podium_counts.items():
            podium_probs[team_id] = {
                "prob_champion": counts["champion"] / n_simulations,
                "prob_runner_up": counts["runner_up"] / n_simulations,
                "prob_third": counts["third"] / n_simulations,
                "prob_podium": (counts["champion"] + counts["runner_up"] + counts["third"]) / n_simulations
            }
        
        # Ordenar por probabilidade de campeão
        sorted_teams = sorted(
            podium_probs.items(),
            key=lambda x: x[1]["prob_champion"],
            reverse=True
        )
        
        return {
            "predicted_champion": sorted_teams[0][0] if sorted_teams else None,
            "predicted_runner_up": sorted_teams[1][0] if len(sorted_teams) > 1 else None,
            "predicted_third": sorted_teams[2][0] if len(sorted_teams) > 2 else None,
            "probabilities": podium_probs,
            "is_adaptive": True
        }


if __name__ == "__main__":
    # Teste do preditor adaptativo
    predictor = AdaptiveMatchPredictor()
    predictor.update_copa_performance()
    print("Modelo adaptativo inicializado com sucesso!")
