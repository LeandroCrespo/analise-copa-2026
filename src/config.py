"""
Configurações do projeto de análise e previsão de Copa 2026
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(Path(__file__).parent.parent / '.env')

# Caminhos
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATABASE_PATH = DATA_DIR / "database.db"

# API Configuration
API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "your_api_key_here")

# Copa 2026 Configuration
WORLD_CUP_2026_ID = 848  # ID da Copa 2026 na API-Football
WORLD_CUP_2026_SEASON = 2026

# Análise de Dados
RECENT_MATCHES_WINDOW = 10  # Últimos 10 jogos para análise de forma recente
MIN_MATCHES_FOR_ANALYSIS = 5  # Mínimo de jogos para análise

# Modelo de Previsão
CONFIDENCE_INTERVAL = 0.95  # Intervalo de confiança de 95%
BOOTSTRAP_SAMPLES = 1000  # Número de amostras para bootstrap

# Banco de Dados
DB_TIMEOUT = 30  # Timeout em segundos

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
