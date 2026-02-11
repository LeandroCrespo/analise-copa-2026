"""
Módulo de atualização automática de resultados em tempo real
Monitora jogos da Copa 2026 e atualiza banco de dados automaticamente
"""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from data_collection import APIFootballCollector
from utils import DatabaseManager, get_logger
from config import WORLD_CUP_2026_ID

logger = get_logger(__name__)


class LiveUpdater:
    """Atualizador de resultados em tempo real"""

    def __init__(self):
        """Inicializar atualizador"""
        self.collector = APIFootballCollector()
        self.db = DatabaseManager()

    def update_match_results(self, match_id: int) -> bool:
        """
        Atualizar resultado de um jogo específico
        
        Args:
            match_id: ID do jogo
            
        Returns:
            True se atualizado com sucesso
        """
        logger.info(f"Atualizando resultado do jogo {match_id}...")
        
        # Buscar dados atualizados do jogo
        response = self.collector._make_request("fixtures", {"id": match_id})
        
        if not response or "response" not in response or not response["response"]:
            logger.error(f"Erro ao buscar dados do jogo {match_id}")
            return False
        
        match_data = response["response"][0]
        
        # Verificar se o jogo já tem resultado
        if match_data["fixture"]["status"]["short"] not in ["FT", "AET", "PEN"]:
            logger.info(f"Jogo {match_id} ainda não finalizado")
            return False
        
        # Atualizar no banco de dados
        home_goals = match_data["goals"]["home"]
        away_goals = match_data["goals"]["away"]
        
        if home_goals is not None and away_goals is not None:
            query = """
                UPDATE matches 
                SET home_goals = ?, away_goals = ?, last_updated = ?
                WHERE id = ?
            """
            self.db.execute_update(query, (home_goals, away_goals, datetime.now(), match_id))
            logger.info(f"Jogo {match_id} atualizado: {home_goals} x {away_goals}")
            return True
        
        return False

    def update_all_matches(self, date: Optional[str] = None) -> int:
        """
        Atualizar resultados de todos os jogos de uma data
        
        Args:
            date: Data no formato YYYY-MM-DD (None = hoje)
            
        Returns:
            Número de jogos atualizados
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Atualizando jogos de {date}...")
        
        # Buscar jogos da data
        response = self.collector._make_request(
            "fixtures",
            {"league": WORLD_CUP_2026_ID, "season": 2026, "date": date}
        )
        
        if not response or "response" not in response:
            logger.error(f"Erro ao buscar jogos de {date}")
            return 0
        
        matches = response["response"]
        updated_count = 0
        
        for match in matches:
            match_id = match["fixture"]["id"]
            
            # Verificar se o jogo já finalizou
            if match["fixture"]["status"]["short"] in ["FT", "AET", "PEN"]:
                if self.update_match_results(match_id):
                    updated_count += 1
        
        logger.info(f"{updated_count} jogos atualizados em {date}")
        return updated_count

    def get_upcoming_matches(self, days_ahead: int = 7) -> List[Dict]:
        """
        Obter jogos que acontecerão nos próximos N dias
        
        Args:
            days_ahead: Número de dias à frente
            
        Returns:
            Lista de jogos futuros
        """
        today = datetime.now()
        end_date = today + timedelta(days=days_ahead)
        
        logger.info(f"Buscando jogos de {today.strftime('%Y-%m-%d')} até {end_date.strftime('%Y-%m-%d')}...")
        
        response = self.collector._make_request(
            "fixtures",
            {
                "league": WORLD_CUP_2026_ID,
                "season": 2026,
                "from": today.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d")
            }
        )
        
        if not response or "response" not in response:
            return []
        
        upcoming = []
        for match in response["response"]:
            upcoming.append({
                "match_id": match["fixture"]["id"],
                "date": match["fixture"]["date"],
                "home_team": match["teams"]["home"]["name"],
                "away_team": match["teams"]["away"]["name"],
                "status": match["fixture"]["status"]["long"]
            })
        
        return upcoming

    def get_live_matches(self) -> List[Dict]:
        """
        Obter jogos que estão acontecendo agora
        
        Returns:
            Lista de jogos ao vivo
        """
        logger.info("Buscando jogos ao vivo...")
        
        response = self.collector._make_request(
            "fixtures",
            {"league": WORLD_CUP_2026_ID, "season": 2026, "live": "all"}
        )
        
        if not response or "response" not in response:
            return []
        
        live_matches = []
        for match in response["response"]:
            live_matches.append({
                "match_id": match["fixture"]["id"],
                "home_team": match["teams"]["home"]["name"],
                "away_team": match["teams"]["away"]["name"],
                "home_goals": match["goals"]["home"],
                "away_goals": match["goals"]["away"],
                "elapsed": match["fixture"]["status"]["elapsed"],
                "status": match["fixture"]["status"]["long"]
            })
        
        return live_matches

    def monitor_matches(self, interval_minutes: int = 5):
        """
        Monitorar jogos continuamente e atualizar resultados
        
        Args:
            interval_minutes: Intervalo entre verificações em minutos
        """
        logger.info(f"Iniciando monitoramento de jogos (intervalo: {interval_minutes} min)...")
        
        while True:
            try:
                # Atualizar jogos de hoje
                self.update_all_matches()
                
                # Verificar jogos ao vivo
                live = self.get_live_matches()
                if live:
                    logger.info(f"{len(live)} jogos ao vivo")
                    for match in live:
                        logger.info(
                            f"  {match['home_team']} {match['home_goals']} x "
                            f"{match['away_goals']} {match['away_team']} "
                            f"({match['elapsed']}')"
                        )
                
                # Aguardar próximo ciclo
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                time.sleep(60)  # Aguardar 1 minuto em caso de erro

    def sync_copa_2026_matches(self):
        """
        Sincronizar todos os jogos da Copa 2026
        Útil para primeira carga ou ressincronização completa
        """
        logger.info("Sincronizando todos os jogos da Copa 2026...")
        
        response = self.collector._make_request(
            "fixtures",
            {"league": WORLD_CUP_2026_ID, "season": 2026}
        )
        
        if not response or "response" not in response:
            logger.error("Erro ao sincronizar jogos da Copa 2026")
            return
        
        matches = response["response"]
        logger.info(f"Encontrados {len(matches)} jogos")
        
        for match in matches:
            match_id = match["fixture"]["id"]
            date = match["fixture"]["date"]
            home_team_id = match["teams"]["home"]["id"]
            away_team_id = match["teams"]["away"]["id"]
            home_goals = match["goals"]["home"]
            away_goals = match["goals"]["away"]
            competition = match["league"]["name"]
            stage = match["league"].get("round", "")
            
            # Inserir ou atualizar jogo
            self.db.insert_match(
                match_id=match_id,
                date=date,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                home_goals=home_goals if home_goals is not None else 0,
                away_goals=away_goals if away_goals is not None else 0,
                competition=competition,
                stage=stage
            )
        
        logger.info("Sincronização concluída!")


def update_results():
    """Função principal para atualização de resultados"""
    updater = LiveUpdater()
    updater.update_all_matches()


def monitor_live():
    """Função principal para monitoramento contínuo"""
    updater = LiveUpdater()
    updater.monitor_matches(interval_minutes=5)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_live()
    else:
        update_results()
