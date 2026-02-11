"""
Script de coleta de dados reais via API-Football
Otimizado para o limite de 100 requisições/dia do plano gratuito
"""

import sys
sys.path.append('src')

import time
from data_collection import APIFootballCollector
from utils import DatabaseManager

print("=" * 80)
print("COLETA DE DADOS REAIS - API-FOOTBALL")
print("=" * 80)

# Inicializar
collector = APIFootballCollector()
db = DatabaseManager()

# Seleções principais da Copa 2026 (48 seleções participantes)
# Vamos focar nas top 20 para otimizar requisições
teams_to_collect = {
    "Brasil": 6,
    "Argentina": 26,
    "França": 2,
    "Alemanha": 25,
    "Espanha": 9,
    "Inglaterra": 10,
    "Portugal": 27,
    "Holanda": 1118,
    "Itália": 768,
    "Uruguai": 7,
    "Bélgica": 1,
    "Croácia": 3,
    "México": 16,
    "Estados Unidos": 4,
    "Colômbia": 8,
    "Japão": 12,
    "Coreia do Sul": 17,
    "Senegal": 13,
    "Marrocos": 31,
    "Canadá": 5,
}

print(f"\n📥 Coletando dados de {len(teams_to_collect)} seleções principais")
print("⏱️  Tempo estimado: 5-10 minutos")
print("📊 Limite da API: 100 requisições/dia (plano gratuito)\n")

total_matches = 0
total_requests = 0
MAX_REQUESTS = 95  # Deixar margem de segurança

for name, team_id in teams_to_collect.items():
    if total_requests >= MAX_REQUESTS:
        print(f"\n⚠️  Limite de requisições atingido ({MAX_REQUESTS})")
        print("💡 Continue amanhã ou upgrade para plano pago")
        break
    
    print(f"\n🔄 {name} (ID: {team_id})...")
    
    try:
        # Inserir seleção
        db.insert_team(team_id=team_id, name=name, country=name)
        
        # Coletar histórico (últimos 50 jogos para economizar requisições)
        print(f"   Buscando histórico de jogos...")
        matches = collector.get_team_matches(team_id, limit=50)
        total_requests += 1
        
        if not matches:
            print(f"   ⚠️  Nenhum jogo encontrado")
            continue
        
        count = 0
        for match in matches:
            try:
                match_id = match["fixture"]["id"]
                date = match["fixture"]["date"]
                home_team_id = match["teams"]["home"]["id"]
                away_team_id = match["teams"]["away"]["id"]
                home_goals = match["goals"]["home"]
                away_goals = match["goals"]["away"]
                competition = match["league"]["name"]
                stage = match["league"].get("round", "")
                
                if home_goals is not None and away_goals is not None:
                    db.insert_match(
                        match_id=match_id,
                        date=date,
                        home_team_id=home_team_id,
                        away_team_id=away_team_id,
                        home_goals=home_goals,
                        away_goals=away_goals,
                        competition=competition,
                        stage=stage
                    )
                    count += 1
            except Exception as e:
                continue
        
        total_matches += count
        print(f"   ✅ {count} jogos coletados")
        
        # Delay para respeitar rate limit
        time.sleep(0.5)
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        continue

print("\n" + "=" * 80)
print("RESUMO DA COLETA")
print("=" * 80)

print(f"""
✅ Coleta Concluída!

📊 Estatísticas:
  - Seleções processadas: {len(teams_to_collect)}
  - Total de jogos coletados: {total_matches}
  - Requisições utilizadas: {total_requests}/{MAX_REQUESTS}
  - Requisições restantes hoje: {MAX_REQUESTS - total_requests}

💾 Dados armazenados em: /home/ubuntu/analise-copa-2026/data/database.db

🚀 Próximos Passos:
  1. Executar backtesting: python backtesting.py
  2. Executar dashboard: streamlit run app/dashboard.py
  3. Gerar previsões para a Copa 2026
""")

print("=" * 80)
