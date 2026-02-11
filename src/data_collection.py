"""
Módulo de coleta de dados via API-Football
"""

import time
from typing import List, Dict, Optional, Any
import requests
import logging
from datetime import datetime, timedelta

from config import API_FOOTBALL_BASE_URL, API_FOOTBALL_KEY, WORLD_CUP_2026_ID
from utils import DatabaseManager, get_logger

logger = get_logger(__name__)


class APIFootballCollector:
    """Coletor de dados da API-Football"""

    def __init__(self, api_key: str = API_FOOTBALL_KEY):
        """Inicializar coletor"""
        self.api_key = api_key
        self.base_url = API_FOOTBALL_BASE_URL
        self.headers = {"x-apisports-key": self.api_key}
        self.db = DatabaseManager()
        self.rate_limit_delay = 0.1  # Delay entre requisições em segundos

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """
        Fazer requisição à API
        
        Args:
            endpoint: Endpoint da API (sem base URL)
            params: Parâmetros da query
            
        Returns:
            Resposta JSON ou None em caso de erro
        """
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                time.sleep(self.rate_limit_delay)
                return response.json()
            elif response.status_code == 429:
                logger.warning("Rate limit atingido. Aguardando...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            else:
                logger.error(f"Erro na API: {response.status_code} - {response.text}")
                return None
        except requests.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            return None

    def get_world_cup_teams(self) -> List[Dict]:
        """
        Obter todas as seleções da Copa 2026
        
        Returns:
            Lista de seleções
        """
        logger.info("Coletando seleções da Copa 2026...")
        
        response = self._make_request("leagues", {"id": WORLD_CUP_2026_ID, "season": 2026})
        
        if not response or "response" not in response:
            logger.error("Erro ao obter seleções")
            return []

        teams = []
        if response["response"] and len(response["response"]) > 0:
            league_data = response["response"][0]
            if "seasons" in league_data:
                # Obter times da Copa 2026
                response = self._make_request(
                    "teams",
                    {"league": WORLD_CUP_2026_ID, "season": 2026}
                )
                
                if response and "response" in response:
                    teams = response["response"]
                    logger.info(f"Coletadas {len(teams)} seleções")

        return teams

    def get_team_matches(self, team_id: int, limit: int = 100) -> List[Dict]:
        """
        Obter histórico de jogos de uma seleção
        
        Args:
            team_id: ID da seleção
            limit: Número máximo de jogos
            
        Returns:
            Lista de jogos
        """
        logger.info(f"Coletando histórico de jogos para seleção {team_id}...")
        
        # Obter últimos 5 anos de jogos
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * 5)
        
        params = {
            "team": team_id,
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "status": "FT"  # Apenas jogos finalizados
        }
        
        response = self._make_request("fixtures", params)
        
        if not response or "response" not in response:
            logger.error(f"Erro ao obter jogos da seleção {team_id}")
            return []

        matches = response["response"]
        logger.info(f"Coletados {len(matches)} jogos para seleção {team_id}")
        
        return matches

    def get_team_info(self, team_id: int) -> Optional[Dict]:
        """
        Obter informações de uma seleção
        
        Args:
            team_id: ID da seleção
            
        Returns:
            Informações da seleção
        """
        response = self._make_request("teams", {"id": team_id})
        
        if response and "response" in response and response["response"]:
            return response["response"][0]
        
        return None

    def get_team_statistics(self, team_id: int, season: int = 2026) -> Optional[Dict]:
        """
        Obter estatísticas de uma seleção em uma temporada
        
        Args:
            team_id: ID da seleção
            season: Temporada
            
        Returns:
            Estatísticas da seleção
        """
        response = self._make_request(
            "teams/statistics",
            {"team": team_id, "season": season, "league": WORLD_CUP_2026_ID}
        )
        
        if response and "response" in response:
            return response["response"]
        
        return None

    def get_standings(self, season: int = 2026) -> List[Dict]:
        """
        Obter classificação da Copa 2026
        
        Args:
            season: Temporada
            
        Returns:
            Classificação
        """
        logger.info("Coletando classificação da Copa 2026...")
        
        response = self._make_request(
            "standings",
            {"league": WORLD_CUP_2026_ID, "season": season}
        )
        
        if response and "response" in response:
            standings = response["response"]
            logger.info(f"Classificação coletada")
            return standings
        
        return []

    def sync_all_data(self):
        """Sincronizar todos os dados da Copa 2026"""
        logger.info("Iniciando sincronização completa de dados...")
        
        # Obter seleções
        teams = self.get_world_cup_teams()
        
        if not teams:
            logger.error("Nenhuma seleção encontrada")
            return
        
        # Processar cada seleção
        for team_data in teams:
            team_id = team_data["team"]["id"]
            team_name = team_data["team"]["name"]
            
            logger.info(f"Processando {team_name}...")
            
            # Inserir seleção no banco
            self.db.insert_team(
                team_id=team_id,
                name=team_name,
                country=team_data.get("team", {}).get("country", "")
            )
            
            # Coletar histórico de jogos
            matches = self.get_team_matches(team_id)
            
            for match in matches:
                match_id = match["fixture"]["id"]
                date = match["fixture"]["date"]
                home_team_id = match["teams"]["home"]["id"]
                away_team_id = match["teams"]["away"]["id"]
                home_goals = match["goals"]["home"]
                away_goals = match["goals"]["away"]
                competition = match["league"]["name"]
                stage = match["league"].get("round", "")
                
                # Inserir jogo no banco
                self.db.insert_match(
                    match_id=match_id,
                    date=date,
                    home_team_id=home_team_id,
                    away_team_id=away_team_id,
                    home_goals=home_goals,
                    away_goals=away_goals,
                    competition=competition,
                    stage=stage
                )
        
        logger.info("Sincronização concluída!")


def collect_data():
    """Função principal para coleta de dados"""
    collector = APIFootballCollector()
    collector.sync_all_data()


if __name__ == "__main__":
    collect_data()
