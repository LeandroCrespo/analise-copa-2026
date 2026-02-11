"""
Backtesting Simplificado - Dados Reais do Neon
"""

import subprocess
import json
import pandas as pd
import numpy as np
from scipy.stats import poisson
import glob
import os

PROJECT_ID = "restless-glitter-71170845"
DATABASE_NAME = "neondb"

print("=" * 80)
print("BACKTESTING COM DADOS REAIS DO NEON")
print("=" * 80)

def run_sql_and_get_result(sql):
    """Executar SQL e ler resultado do arquivo"""
    input_data = {
        "projectId": PROJECT_ID,
        "databaseName": DATABASE_NAME,
        "sql": sql
    }
    
    cmd = [
        "manus-mcp-cli", "tool", "call", "run_sql",
        "--server", "neon",
        "--input", json.dumps(input_data)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Encontrar arquivo de resultado mais recente
    result_files = glob.glob("/home/ubuntu/.mcp/tool-results/*_neon_run_sql.json")
    if result_files:
        latest_file = max(result_files, key=os.path.getctime)
        with open(latest_file, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    
    return []

# 1. Buscar jogos
print("\n📊 Buscando jogos do Neon...")

sql = """
SELECT 
    m.id,
    m.date,
    m.home_team_id,
    m.away_team_id,
    m.home_goals,
    m.away_goals,
    ht.name as home_team,
    at.name as away_team
FROM matches m
JOIN teams ht ON m.home_team_id = ht.id
JOIN teams at ON m.away_team_id = at.id
ORDER BY m.date
"""

matches = run_sql_and_get_result(sql)
print(f"✅ {len(matches)} jogos encontrados")

if len(matches) < 50:
    print("\n⚠️  Poucos jogos. Aguardando importação...")
    exit(0)

# Converter para DataFrame
df = pd.DataFrame(matches)
df['date'] = pd.to_datetime(df['date'])
df['home_goals'] = pd.to_numeric(df['home_goals'])
df['away_goals'] = pd.to_numeric(df['away_goals'])

print(f"📅 Período: {df['date'].min().date()} até {df['date'].max().date()}")

# Dividir treino/teste (70/30)
split = int(len(df) * 0.7)
train = df.iloc[:split]
test = df.iloc[split:]

print(f"\n📊 Treino: {len(train)} jogos | Teste: {len(test)} jogos")

# Calcular estatísticas
print("\n📈 Calculando estatísticas...")

stats = {}

for tid in set(train['home_team_id'].unique()) | set(train['away_team_id'].unique()):
    home = train[train['home_team_id'] == tid]
    away = train[train['away_team_id'] == tid]
    
    total = len(home) + len(away)
    if total == 0:
        continue
    
    gf = home['home_goals'].sum() + away['away_goals'].sum()
    ga = home['away_goals'].sum() + away['home_goals'].sum()
    
    stats[tid] = {
        'avg_gf': gf / total if total > 0 else 1.5,
        'avg_ga': ga / total if total > 0 else 1.5
    }

print(f"✅ {len(stats)} times analisados")

# Prever jogos de teste
print("\n🔍 Testando previsões...")

results = []

for _, row in test.iterrows():
    hid = row['home_team_id']
    aid = row['away_team_id']
    
    # Estatísticas
    h_stats = stats.get(hid, {'avg_gf': 1.5, 'avg_ga': 1.5})
    a_stats = stats.get(aid, {'avg_gf': 1.5, 'avg_ga': 1.5})
    
    # Gols esperados
    h_exp = (h_stats['avg_gf'] + a_stats['avg_ga']) / 2 + 0.3  # vantagem casa
    a_exp = (a_stats['avg_gf'] + h_stats['avg_ga']) / 2
    
    # Limitar
    h_exp = max(0.5, min(4.0, h_exp))
    a_exp = max(0.5, min(4.0, a_exp))
    
    # Prever
    pred_h = int(round(h_exp))
    pred_a = int(round(a_exp))
    
    # Real
    real_h = int(row['home_goals'])
    real_a = int(row['away_goals'])
    
    # Acertos
    exact = (pred_h == real_h and pred_a == real_a)
    result_ok = ((pred_h > pred_a and real_h > real_a) or 
                 (pred_h < pred_a and real_h < real_a) or
                 (pred_h == pred_a and real_h == real_a))
    
    # Pontos
    pts = 20 if exact else (10 if result_ok else 0)
    if result_ok and not exact:
        if pred_h == real_h or pred_a == real_a:
            pts = 15
    
    results.append({
        'match': f"{row['home_team']} vs {row['away_team']}",
        'real': f"{real_h}x{real_a}",
        'pred': f"{pred_h}x{pred_a}",
        'exact': exact,
        'result': result_ok,
        'pts': pts
    })

# Métricas
rdf = pd.DataFrame(results)

print("\n" + "=" * 80)
print("RESULTADOS")
print("=" * 80)

total = len(rdf)
exact_pct = (rdf['exact'].sum() / total) * 100
result_pct = (rdf['result'].sum() / total) * 100
avg_pts = rdf['pts'].mean()

print(f"\n📊 Métricas ({total} jogos):")
print(f"  ✅ Placar exato: {exact_pct:.1f}% ({rdf['exact'].sum()} acertos)")
print(f"  ✅ Resultado correto: {result_pct:.1f}% ({rdf['result'].sum()} acertos)")
print(f"  ✅ Pontos médios: {avg_pts:.1f} pts/jogo")

print(f"\n🎯 Benchmarks:")
print(f"  - Placar exato: {exact_pct:.1f}% (alvo: 10-15%)")
print(f"  - Resultado: {result_pct:.1f}% (alvo: 50-60%)")
print(f"  - Pontos: {avg_pts:.1f} pts (alvo: 10-12 pts)")

# Exemplos
print(f"\n📋 Exemplos:")
for _, r in rdf.sample(min(10, len(rdf))).iterrows():
    s = "✅" if r['exact'] else ("🟡" if r['result'] else "❌")
    print(f"  {s} {r['match']:35s} Real {r['real']:5s} Prev {r['pred']:5s} ({r['pts']} pts)")

# Salvar
rdf.to_csv('backtesting_neon_results.csv', index=False)
print(f"\n💾 Salvo em: backtesting_neon_results.csv")

print("\n" + "=" * 80)
if result_pct >= 50:
    print("✅ MODELO COM BOA PRECISÃO!")
elif result_pct >= 40:
    print("🟡 MODELO MODERADO - Precisa mais dados")
else:
    print("⚠️  MODELO BAIXA PRECISÃO - Aguardar importação completa")

print(f"\n💡 Baseado em {len(train)} jogos de treino")
print("=" * 80)
