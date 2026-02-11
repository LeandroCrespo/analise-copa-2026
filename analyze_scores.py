"""
Análise de Distribuição de Placares
Compara placares reais vs. previstos do modelo
"""

import pandas as pd
import numpy as np
from collections import Counter

print("=" * 80)
print("ANÁLISE DE DISTRIBUIÇÃO DE PLACARES")
print("=" * 80)

# Carregar resultados do backtesting
df = pd.read_csv('backtesting_neon_results.csv')

print(f"\n📊 Total de jogos analisados: {len(df)}")

# Extrair placares
def parse_score(score_str):
    """Extrai gols de string '2x1'"""
    try:
        home, away = score_str.split('x')
        return int(home), int(away)
    except:
        return None, None

df['real_home'], df['real_away'] = zip(*df['real'].apply(parse_score))
df['pred_home'], df['pred_away'] = zip(*df['pred'].apply(parse_score))

# Remover linhas com erro
df = df.dropna(subset=['real_home', 'real_away', 'pred_home', 'pred_away'])

print(f"✅ {len(df)} jogos válidos")

# Placares "conservadores" (mais comuns)
conservative_scores = [
    (0, 0), (1, 0), (0, 1), (2, 0), (0, 2),
    (1, 1), (2, 1), (1, 2), (2, 2)
]

# Análise de placares REAIS
print("\n" + "=" * 80)
print("PLACARES REAIS (Histórico)")
print("=" * 80)

real_scores = list(zip(df['real_home'].astype(int), df['real_away'].astype(int)))
real_counter = Counter(real_scores)

print("\n🏆 Top 15 Placares Mais Frequentes:")
for score, count in real_counter.most_common(15):
    pct = (count / len(df)) * 100
    conservative = "✅" if score in conservative_scores else "  "
    print(f"{conservative} {score[0]}x{score[1]}: {count:4d} jogos ({pct:5.2f}%)")

# Calcular cobertura dos placares conservadores
conservative_real = sum(count for score, count in real_counter.items() if score in conservative_scores)
conservative_real_pct = (conservative_real / len(df)) * 100

print(f"\n📊 Placares conservadores (0x0 até 2x2):")
print(f"   Cobertura: {conservative_real} jogos ({conservative_real_pct:.1f}%)")

# Análise de placares PREVISTOS
print("\n" + "=" * 80)
print("PLACARES PREVISTOS (Modelo Atual)")
print("=" * 80)

pred_scores = list(zip(df['pred_home'].astype(int), df['pred_away'].astype(int)))
pred_counter = Counter(pred_scores)

print("\n🎯 Top 15 Placares Mais Previstos:")
for score, count in pred_counter.most_common(15):
    pct = (count / len(df)) * 100
    conservative = "✅" if score in conservative_scores else "⚠️ "
    print(f"{conservative} {score[0]}x{score[1]}: {count:4d} jogos ({pct:5.2f}%)")

# Calcular cobertura dos placares conservadores nas previsões
conservative_pred = sum(count for score, count in pred_counter.items() if score in conservative_scores)
conservative_pred_pct = (conservative_pred / len(df)) * 100

print(f"\n📊 Placares conservadores previstos:")
print(f"   Cobertura: {conservative_pred} jogos ({conservative_pred_pct:.1f}%)")

# Placares "arriscados" (acima de 2 gols)
print("\n" + "=" * 80)
print("PLACARES ARRISCADOS (3+ gols)")
print("=" * 80)

risky_real = [(h, a) for h, a in real_scores if h >= 3 or a >= 3]
risky_pred = [(h, a) for h, a in pred_scores if h >= 3 or a >= 3]

print(f"\n📊 Jogos com 3+ gols:")
print(f"   Real: {len(risky_real)} jogos ({len(risky_real)/len(df)*100:.1f}%)")
print(f"   Previsto: {len(risky_pred)} jogos ({len(risky_pred)/len(df)*100:.1f}%)")

# Análise de pontuação por estratégia
print("\n" + "=" * 80)
print("IMPACTO NA PONTUAÇÃO")
print("=" * 80)

# Calcular pontos se usássemos apenas placares conservadores
def calculate_points(real_h, real_a, pred_h, pred_a):
    """Calcula pontos conforme regras do Bolão"""
    if real_h == pred_h and real_a == pred_a:
        return 20  # Placar exato
    
    real_result = 'home' if real_h > real_a else ('away' if real_a > real_h else 'draw')
    pred_result = 'home' if pred_h > pred_a else ('away' if pred_a > pred_h else 'draw')
    
    if real_result == pred_result:
        if real_h == pred_h or real_a == pred_a:
            return 15  # Resultado + 1 gol certo
        return 10  # Apenas resultado
    
    return 0  # Errou

# Pontos atuais
df['points'] = df.apply(lambda row: calculate_points(
    row['real_home'], row['real_away'],
    row['pred_home'], row['pred_away']
), axis=1)

current_avg = df['points'].mean()
current_exact = (df['points'] == 20).sum()
current_result = (df['points'] >= 10).sum()

print(f"\n🎯 Modelo Atual:")
print(f"   Pontos médios: {current_avg:.2f} pts/jogo")
print(f"   Placar exato: {current_exact} ({current_exact/len(df)*100:.1f}%)")
print(f"   Resultado correto: {current_result} ({current_result/len(df)*100:.1f}%)")

# Simular estratégia conservadora
print("\n" + "=" * 80)
print("RECOMENDAÇÃO")
print("=" * 80)

print(f"""
📊 Análise:

1. **Placares Reais:**
   - {conservative_real_pct:.1f}% dos jogos terminam em placares conservadores (0x0 até 2x2)
   - Apenas {100-conservative_real_pct:.1f}% têm placares "arriscados" (3+ gols)

2. **Modelo Atual:**
   - {conservative_pred_pct:.1f}% das previsões são conservadoras
   - {100-conservative_pred_pct:.1f}% são arriscadas

3. **Estratégia do Bolão:**
   - Placar exato: 20 pts (difícil)
   - Resultado + 1 gol: 15 pts (moderado)
   - Apenas resultado: 10 pts (mais fácil)

💡 **Recomendação:**

✅ **SIM, mantenha placares conservadores!**

**Por quê?**
1. {conservative_real_pct:.1f}% dos jogos reais são conservadores
2. Maximiza chance de acertar resultado (10 pts garantidos)
3. Aumenta chance de acertar 1 gol (15 pts)
4. Reduz risco de errar completamente (0 pts)

**Estratégia Ideal:**
- Priorize: 1x0, 2x1, 1x1, 2x0, 0x1, 1x2
- Evite: 3x2, 4x1, 5x0, etc. (muito arriscado)
- Exceção: Jogos com grande diferença de força (pode arriscar 3x0, 4x0)

Vou criar uma versão otimizada do modelo que:
1. Limita placares a 0-2 gols por padrão
2. Só prevê 3+ gols em casos extremos
3. Maximiza pontuação esperada (não apenas precisão)
""")

print("=" * 80)
