"""
Explicação Detalhada do Raciocínio do Modelo
"""

import sys
sys.path.append('src')

import pandas as pd
import sqlite3
from utils import DatabaseManager
from data_processing import DataProcessor
from model import MatchPredictor

print("=" * 80)
print("EXPLICAÇÃO DO RACIOCÍNIO DO MODELO DE PREVISÃO")
print("=" * 80)

# Inicializar
db = DatabaseManager()
processor = DataProcessor()
predictor = MatchPredictor()

# Escolher um confronto real para demonstrar
print("\n🎯 Vamos analisar um confronto: BRASIL vs ARGENTINA")
print("=" * 80)

# Buscar IDs
conn = sqlite3.connect(db.db_path)
teams = pd.read_sql_query("SELECT * FROM teams WHERE name IN ('Brazil', 'Argentina')", conn)

if len(teams) < 2:
    print("⚠️ Times não encontrados no banco. Usando IDs genéricos...")
    brazil_id = 1
    argentina_id = 2
else:
    brazil_id = teams[teams['name'] == 'Brazil']['id'].values[0]
    argentina_id = teams[teams['name'] == 'Argentina']['id'].values[0]

print(f"\n📊 IDs no banco:")
print(f"  - Brasil: {brazil_id}")
print(f"  - Argentina: {argentina_id}")

# PASSO 1: Coletar histórico de cada time
print("\n" + "=" * 80)
print("PASSO 1: COLETAR HISTÓRICO DE CADA SELEÇÃO")
print("=" * 80)

brazil_matches = db.get_team_matches(brazil_id, limit=20)
argentina_matches = db.get_team_matches(argentina_id, limit=20)

print(f"\n🇧🇷 Brasil:")
print(f"  - Jogos encontrados: {len(brazil_matches)}")
if len(brazil_matches) > 0:
    print(f"  - Últimos 5 jogos:")
    for _, m in brazil_matches.head(5).iterrows():
        print(f"    {m['date'][:10]}: {m['home_team_name']} {m['home_goals']} x {m['away_goals']} {m['away_team_name']}")

print(f"\n🇦🇷 Argentina:")
print(f"  - Jogos encontrados: {len(argentina_matches)}")
if len(argentina_matches) > 0:
    print(f"  - Últimos 5 jogos:")
    for _, m in argentina_matches.head(5).iterrows():
        print(f"    {m['date'][:10]}: {m['home_team_name']} {m['home_goals']} x {m['away_goals']} {m['away_team_name']}")

# PASSO 2: Calcular estatísticas gerais
print("\n" + "=" * 80)
print("PASSO 2: CALCULAR ESTATÍSTICAS GERAIS")
print("=" * 80)

brazil_stats = processor.get_team_overall_stats(brazil_id)
argentina_stats = processor.get_team_overall_stats(argentina_id)

print(f"\n🇧🇷 Brasil - Estatísticas Gerais:")
if brazil_stats:
    print(f"  - Total de jogos: {brazil_stats.get('total_matches', 0)}")
    print(f"  - Vitórias: {brazil_stats.get('overall_wins', 0)}")
    print(f"  - Taxa de vitória: {brazil_stats.get('overall_win_rate', 0):.1%}")
    print(f"  - Média de gols marcados: {brazil_stats.get('overall_avg_goals_for', 0):.2f}")
    print(f"  - Média de gols sofridos: {brazil_stats.get('overall_avg_goals_against', 0):.2f}")
    print(f"  - Saldo de gols: {brazil_stats.get('overall_goal_difference', 0)}")
else:
    print("  ⚠️ Dados insuficientes")

print(f"\n🇦🇷 Argentina - Estatísticas Gerais:")
if argentina_stats:
    print(f"  - Total de jogos: {argentina_stats.get('total_matches', 0)}")
    print(f"  - Vitórias: {argentina_stats.get('overall_wins', 0)}")
    print(f"  - Taxa de vitória: {argentina_stats.get('overall_win_rate', 0):.1%}")
    print(f"  - Média de gols marcados: {argentina_stats.get('overall_avg_goals_for', 0):.2f}")
    print(f"  - Média de gols sofridos: {argentina_stats.get('overall_avg_goals_against', 0):.2f}")
    print(f"  - Saldo de gols: {argentina_stats.get('overall_goal_difference', 0)}")
else:
    print("  ⚠️ Dados insuficientes")

# PASSO 3: Calcular forma recente
print("\n" + "=" * 80)
print("PASSO 3: CALCULAR FORMA RECENTE (últimos 10 jogos)")
print("=" * 80)

brazil_recent = processor.get_team_recent_form(brazil_id)
argentina_recent = processor.get_team_recent_form(argentina_id)

print(f"\n🇧🇷 Brasil - Forma Recente:")
if brazil_recent:
    print(f"  - Jogos recentes: {brazil_recent.get('recent_matches', 0)}")
    print(f"  - Vitórias: {brazil_recent.get('recent_wins', 0)}")
    print(f"  - Taxa de vitória: {brazil_recent.get('recent_win_rate', 0):.1%}")
    print(f"  - Média de gols: {brazil_recent.get('recent_avg_goals_for', 0):.2f}")
else:
    print("  ⚠️ Dados insuficientes")

print(f"\n🇦🇷 Argentina - Forma Recente:")
if argentina_recent:
    print(f"  - Jogos recentes: {argentina_recent.get('recent_matches', 0)}")
    print(f"  - Vitórias: {argentina_recent.get('recent_wins', 0)}")
    print(f"  - Taxa de vitória: {argentina_recent.get('recent_win_rate', 0):.1%}")
    print(f"  - Média de gols: {argentina_recent.get('recent_avg_goals_for', 0):.2f}")
else:
    print("  ⚠️ Dados insuficientes")

# PASSO 4: Calcular força das seleções
print("\n" + "=" * 80)
print("PASSO 4: CALCULAR FORÇA DAS SELEÇÕES (0-100)")
print("=" * 80)

brazil_strength = processor.calculate_team_strength(brazil_id)
argentina_strength = processor.calculate_team_strength(argentina_id)

print(f"\n💪 Força Calculada:")
print(f"  - Brasil: {brazil_strength:.1f}/100")
print(f"  - Argentina: {argentina_strength:.1f}/100")

print(f"\n📊 Fórmula da Força:")
print(f"  Força = (Taxa de Vitória × 40) + (Saldo de Gols Normalizado × 30) + (Forma Recente × 30)")

# PASSO 5: Prever gols de cada time
print("\n" + "=" * 80)
print("PASSO 5: PREVER GOLS USANDO DISTRIBUIÇÃO DE POISSON")
print("=" * 80)

print(f"\n🎯 Metodologia:")
print(f"  1. Calcular média de gols esperados para cada time")
print(f"  2. Ajustar pela força do adversário")
print(f"  3. Aplicar vantagem de jogar em casa (+0.3 gols)")
print(f"  4. Usar Distribuição de Poisson para modelar probabilidades")

# Fazer previsão
try:
    prediction = predictor.predict_match_score(brazil_id, argentina_id)
    
    print(f"\n📈 Cálculo Detalhado:")
    print(f"\n  Brasil (mandante):")
    print(f"    - Média histórica de gols: {brazil_stats.get('overall_avg_goals_for', 1.5):.2f}")
    print(f"    - Ajuste por força do adversário: considerado")
    print(f"    - Vantagem de casa: +0.3 gols")
    print(f"    - Gols esperados: {prediction['home_goals_expected']:.2f}")
    print(f"    - Intervalo de confiança: {prediction['home_goals_ci'][0]:.1f} - {prediction['home_goals_ci'][1]:.1f}")
    
    print(f"\n  Argentina (visitante):")
    print(f"    - Média histórica de gols: {argentina_stats.get('overall_avg_goals_for', 1.5):.2f}")
    print(f"    - Ajuste por força do adversário: considerado")
    print(f"    - Gols esperados: {prediction['away_goals_expected']:.2f}")
    print(f"    - Intervalo de confiança: {prediction['away_goals_ci'][0]:.1f} - {prediction['away_goals_ci'][1]:.1f}")
    
    # PASSO 6: Resultado final
    print("\n" + "=" * 80)
    print("PASSO 6: RESULTADO FINAL DA PREVISÃO")
    print("=" * 80)
    
    print(f"\n🎯 PLACAR PREVISTO: {prediction['predicted_home_goals']} x {prediction['predicted_away_goals']}")
    
    print(f"\n📊 Probabilidades:")
    print(f"  - Vitória Brasil: {prediction['prob_home_win']:.1%}")
    print(f"  - Empate: {prediction['prob_draw']:.1%}")
    print(f"  - Vitória Argentina: {prediction['prob_away_win']:.1%}")
    
    print(f"\n💡 Resultado mais provável: ", end="")
    if prediction['predicted_result'] == 'home':
        print("Vitória do Brasil")
    elif prediction['predicted_result'] == 'away':
        print("Vitória da Argentina")
    else:
        print("Empate")
    
    print(f"\n🎲 Confiança da previsão: {prediction['confidence']:.1%}")
    
except Exception as e:
    print(f"\n❌ Erro ao gerar previsão: {e}")
    import traceback
    traceback.print_exc()

# RESUMO
print("\n" + "=" * 80)
print("RESUMO DO RACIOCÍNIO")
print("=" * 80)

print(f"""
O modelo segue este fluxo:

1️⃣ COLETA DE DADOS
   - Busca histórico de jogos de cada seleção
   - Foca nos últimos anos (mais relevante)

2️⃣ ANÁLISE ESTATÍSTICA
   - Calcula médias de gols marcados/sofridos
   - Calcula taxa de vitórias
   - Analisa forma recente (últimos 10 jogos)

3️⃣ CÁLCULO DE FORÇA
   - Combina múltiplos fatores (vitórias, gols, forma)
   - Gera score de 0-100 para cada seleção

4️⃣ PREVISÃO DE GOLS
   - Usa Distribuição de Poisson (padrão em futebol)
   - Ajusta pela força relativa dos times
   - Considera vantagem de jogar em casa

5️⃣ CÁLCULO DE PROBABILIDADES
   - Simula milhares de cenários
   - Calcula probabilidade de cada resultado
   - Gera intervalo de confiança

6️⃣ RESULTADO FINAL
   - Placar mais provável
   - Probabilidades de vitória/empate/derrota
   - Nível de confiança da previsão

⚠️ LIMITAÇÕES ATUAIS:
   - Se não há dados suficientes, usa valores padrão (1.5 gols)
   - Isso explica previsões genéricas quando faltam dados
   - Com mais jogos no histórico, previsões melhoram
""")

print("=" * 80)

conn.close()
