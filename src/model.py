"""
Módulo de modelos de previsão para Copa 2026
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from scipy import stats
from itertools import combinations
import random

from utils import DatabaseManager, get_logger
from data_processing import DataProcessor
from config import CONFIDENCE_INTERVAL, BOOTSTRAP_SAMPLES

logger = get_logger(__name__)


class MatchPredictor:
    """Preditor de placares de jogos"""

    def __init__(self):
        """Inicializar preditor"""
        self.db = DatabaseManager()
        self.processor = DataProcessor()

    def predict_goals(self, team_id: int, opponent_id: int, 
                     is_home: bool = True) -> Tuple[float, float]:
        """
        Prever número de gols de um time contra um oponente
        
        Args:
            team_id: ID do time
            opponent_id: ID do oponente
            is_home: Se o time joga em casa (não relevante para Copa)
            
        Returns:
            (média de gols, desvio padrão)
        """
        # Obter estatísticas do time
        overall_stats = self.processor.get_team_overall_stats(team_id)
        recent_form = self.processor.get_team_recent_form(team_id)
        
        # Obter estatísticas do oponente
        opponent_overall = self.processor.get_team_overall_stats(opponent_id)
        opponent_recent = self.processor.get_team_recent_form(opponent_id)
        
        if not overall_stats or not recent_form:
            return 1.5, 1.0  # Valores padrão
        
        # Média de gols marcados (ponderando forma recente)
        avg_goals_overall = overall_stats.get("overall_avg_goals_for", 1.5)
        avg_goals_recent = recent_form.get("recent_avg_goals_for", 1.5)
        
        # Média de gols sofridos pelo oponente
        opponent_avg_conceded_overall = opponent_overall.get("overall_avg_goals_against", 1.5)
        opponent_avg_conceded_recent = opponent_recent.get("recent_avg_goals_against", 1.5)
        
        # Ponderação: 60% forma recente, 40% histórico geral
        expected_goals_attack = 0.6 * avg_goals_recent + 0.4 * avg_goals_overall
        expected_goals_defense = 0.6 * opponent_avg_conceded_recent + 0.4 * opponent_avg_conceded_overall
        
        # Média ponderada entre ataque e defesa
        expected_goals = (expected_goals_attack + expected_goals_defense) / 2
        
        # Ajustar por força relativa
        team_strength = self.processor.calculate_team_strength(team_id)
        opponent_strength = self.processor.calculate_team_strength(opponent_id)
        
        strength_factor = team_strength / max(1, opponent_strength)
        expected_goals *= strength_factor
        
        # Desvio padrão baseado na variância histórica
        std_dev = max(0.8, expected_goals * 0.5)
        
        return expected_goals, std_dev

    def predict_match_score(self, home_team_id: int, away_team_id: int) -> Dict:
        """
        Prever placar de um jogo
        
        Args:
            home_team_id: ID do time mandante
            away_team_id: ID do time visitante
            
        Returns:
            Dicionário com previsão completa
        """
        # Prever gols de cada time
        home_goals_mean, home_goals_std = self.predict_goals(home_team_id, away_team_id, is_home=True)
        away_goals_mean, away_goals_std = self.predict_goals(away_team_id, home_team_id, is_home=False)
        
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
            "confidence": round(max(prob_home_win, prob_draw, prob_away_win), 3)
        }

    def _calculate_result_probabilities(self, home_mean: float, home_std: float,
                                       away_mean: float, away_std: float) -> Tuple[float, float, float]:
        """
        Calcular probabilidades de vitória mandante, empate e vitória visitante
        usando simulação de Monte Carlo
        """
        n_simulations = 10000
        
        home_goals = np.random.poisson(home_mean, n_simulations)
        away_goals = np.random.poisson(away_mean, n_simulations)
        
        home_wins = np.sum(home_goals > away_goals)
        draws = np.sum(home_goals == away_goals)
        away_wins = np.sum(home_goals < away_goals)
        
        return (
            home_wins / n_simulations,
            draws / n_simulations,
            away_wins / n_simulations
        )

    def _calculate_confidence_interval(self, mean: float, std: float) -> Tuple[float, float]:
        """Calcular intervalo de confiança"""
        z_score = stats.norm.ppf((1 + CONFIDENCE_INTERVAL) / 2)
        margin = z_score * std
        
        return max(0, mean - margin), mean + margin


class GroupPredictor:
    """Preditor de classificação dos grupos"""

    def __init__(self):
        """Inicializar preditor"""
        self.db = DatabaseManager()
        self.match_predictor = MatchPredictor()

    def predict_group_standings(self, group_name: str, teams: List[int]) -> pd.DataFrame:
        """
        Prever classificação de um grupo
        
        Args:
            group_name: Nome do grupo (ex: "A")
            teams: Lista de IDs das seleções do grupo
            
        Returns:
            DataFrame com classificação prevista
        """
        if len(teams) != 4:
            logger.error(f"Grupo {group_name} deve ter 4 times")
            return pd.DataFrame()
        
        # Simular todos os jogos do grupo
        standings = {team_id: {"points": 0, "goals_for": 0, "goals_against": 0, "wins": 0, "draws": 0} 
                    for team_id in teams}
        
        # Gerar todos os confrontos (6 jogos por grupo)
        matches = list(combinations(teams, 2))
        
        for team1_id, team2_id in matches:
            prediction = self.match_predictor.predict_match_score(team1_id, team2_id)
            
            home_goals = prediction["predicted_home_goals"]
            away_goals = prediction["predicted_away_goals"]
            
            standings[team1_id]["goals_for"] += home_goals
            standings[team1_id]["goals_against"] += away_goals
            standings[team2_id]["goals_for"] += away_goals
            standings[team2_id]["goals_against"] += home_goals
            
            if home_goals > away_goals:
                standings[team1_id]["points"] += 3
                standings[team1_id]["wins"] += 1
            elif home_goals < away_goals:
                standings[team2_id]["points"] += 3
                standings[team2_id]["wins"] += 1
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
                "losses": 3 - stats["wins"] - stats["draws"],
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

    def predict_all_groups(self, groups: Dict[str, List[int]]) -> Dict[str, pd.DataFrame]:
        """
        Prever classificação de todos os grupos
        
        Args:
            groups: Dicionário {nome_grupo: [lista de team_ids]}
            
        Returns:
            Dicionário com classificações de cada grupo
        """
        predictions = {}
        
        for group_name, teams in groups.items():
            logger.info(f"Prevendo classificação do Grupo {group_name}...")
            predictions[group_name] = self.predict_group_standings(group_name, teams)
        
        return predictions


class PodiumPredictor:
    """Preditor de pódio (campeão, vice, 3º lugar)"""

    def __init__(self):
        """Inicializar preditor"""
        self.db = DatabaseManager()
        self.processor = DataProcessor()
        self.match_predictor = MatchPredictor()

    def predict_podium(self, qualified_teams: List[int], n_simulations: int = 1000) -> Dict:
        """
        Prever pódio através de simulação de Monte Carlo
        
        Args:
            qualified_teams: Lista de IDs das seleções classificadas para mata-mata
            n_simulations: Número de simulações
            
        Returns:
            Dicionário com previsão de pódio
        """
        podium_counts = {team_id: {"champion": 0, "runner_up": 0, "third": 0} 
                        for team_id in qualified_teams}
        
        for _ in range(n_simulations):
            # Simular mata-mata completo
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
        
        # Retornar top 3 mais prováveis
        return {
            "predicted_champion": sorted_teams[0][0] if sorted_teams else None,
            "predicted_runner_up": sorted_teams[1][0] if len(sorted_teams) > 1 else None,
            "predicted_third": sorted_teams[2][0] if len(sorted_teams) > 2 else None,
            "probabilities": podium_probs
        }

    def _simulate_knockout_stage(self, teams: List[int]) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
        Simular fase de mata-mata completa
        
        Returns:
            (campeão, vice, 3º lugar)
        """
        if len(teams) < 4:
            return None, None, None
        
        # Embaralhar times (simulação aleatória de chaveamento)
        teams_copy = teams.copy()
        random.shuffle(teams_copy)
        
        # Simular oitavas, quartas, semifinais
        remaining = teams_copy
        
        # Oitavas de final (se houver 16 times)
        if len(remaining) == 16:
            remaining = self._simulate_round(remaining)
        
        # Quartas de final (8 times)
        if len(remaining) == 8:
            remaining = self._simulate_round(remaining)
        
        # Semifinais (4 times)
        if len(remaining) == 4:
            semifinal_losers = []
            winners = []
            
            for i in range(0, 4, 2):
                winner, loser = self._simulate_match_with_loser(remaining[i], remaining[i+1])
                winners.append(winner)
                semifinal_losers.append(loser)
            
            # Final
            champion, runner_up = self._simulate_match_with_loser(winners[0], winners[1])
            
            # Disputa de 3º lugar
            third, _ = self._simulate_match_with_loser(semifinal_losers[0], semifinal_losers[1])
            
            return champion, runner_up, third
        
        return None, None, None

    def _simulate_round(self, teams: List[int]) -> List[int]:
        """Simular uma rodada de mata-mata"""
        winners = []
        for i in range(0, len(teams), 2):
            if i + 1 < len(teams):
                winner = self._simulate_match(teams[i], teams[i+1])
                winners.append(winner)
        return winners

    def _simulate_match(self, team1_id: int, team2_id: int) -> int:
        """Simular um jogo e retornar vencedor"""
        prediction = self.match_predictor.predict_match_score(team1_id, team2_id)
        
        # Usar probabilidades para determinar vencedor
        rand = random.random()
        
        if rand < prediction["prob_home_win"]:
            return team1_id
        elif rand < prediction["prob_home_win"] + prediction["prob_draw"]:
            # Empate - decidir nos pênaltis (50/50)
            return team1_id if random.random() < 0.5 else team2_id
        else:
            return team2_id

    def _simulate_match_with_loser(self, team1_id: int, team2_id: int) -> Tuple[int, int]:
        """Simular um jogo e retornar vencedor e perdedor"""
        winner = self._simulate_match(team1_id, team2_id)
        loser = team2_id if winner == team1_id else team1_id
        return winner, loser


if __name__ == "__main__":
    # Teste do preditor
    predictor = MatchPredictor()
    print("Modelo de previsão inicializado com sucesso!")
