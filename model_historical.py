"""
Modelo de Predição Baseado em Distribuição Histórica
Usa placares reais dos 4.173 jogos (2020-2026) ajustados por diferença de força
"""

import numpy as np

# Distribuição real de placares (4.173 jogos, 2020-2026)
HISTORICAL_SCORES = {
    # Formato: (home_goals, away_goals): frequência
    (1, 0): 0.1083,  # 10.83%
    (1, 1): 0.1042,  # 10.42%
    (0, 0): 0.0851,  # 8.51%
    (0, 1): 0.0798,  # 7.98%
    (2, 0): 0.0769,  # 7.69%
    (2, 1): 0.0733,  # 7.33%
    (3, 0): 0.0525,  # 5.25%
    (1, 2): 0.0522,  # 5.22%
    (0, 2): 0.0508,  # 5.08%
    (3, 1): 0.0367,  # 3.67%
    (2, 2): 0.0329,  # 3.29%
    (4, 0): 0.0253,  # 2.53%
    (0, 3): 0.0236,  # 2.36%
    (4, 1): 0.0215,  # 2.15%
    (3, 2): 0.0203,  # 2.03%
    (1, 3): 0.0181,  # 1.81%
    (2, 3): 0.0122,  # 1.22%
    (4, 2): 0.0105,  # 1.05%
    (5, 0): 0.0103,  # 1.03%
    (3, 3): 0.0086,  # 0.86%
    # Outros placares raros somam ~10%
}

def adjust_probabilities_by_strength(strength_diff):
    """
    Ajusta probabilidades dos placares baseado na diferença de força.
    
    Args:
        strength_diff: Diferença de força (team1 - team2), range: -100 a +100
    
    Returns:
        dict com probabilidades ajustadas
    """
    adjusted_probs = {}
    
    # Normalizar diferença para -1 a +1
    normalized_diff = max(-1.0, min(1.0, strength_diff / 100))
    
    for (home_goals, away_goals), base_prob in HISTORICAL_SCORES.items():
        # Calcular "vantagem" do placar
        goal_diff = home_goals - away_goals
        
        # Ajustar probabilidade baseado em alinhamento com diferença de força
        # Se team1 é forte (+diff) e placar favorece team1 (+goal_diff) → aumentar prob
        # Se team1 é forte (+diff) e placar favorece team2 (-goal_diff) → diminuir prob
        
        alignment = normalized_diff * goal_diff
        
        # Fator de ajuste: exponencial para amplificar diferenças (BALANCEADO)
        # alignment = 1.0 (perfeitamente alinhado) → fator = 1.65
        # alignment = 0.0 (neutro) → fator = 1.0
        # alignment = -1.0 (opostos) → fator = 0.61
        adjustment_factor = np.exp(alignment * 0.5)
        
        adjusted_prob = base_prob * adjustment_factor
        adjusted_probs[(home_goals, away_goals)] = adjusted_prob
    
    # Normalizar para somar 1.0
    total = sum(adjusted_probs.values())
    for score in adjusted_probs:
        adjusted_probs[score] /= total
    
    return adjusted_probs

def predict_match_historical(team1_stats, team2_stats):
    """
    Predição baseada em distribuição histórica ajustada por força.
    
    Args:
        team1_stats: Estatísticas do time 1
        team2_stats: Estatísticas do time 2
    
    Returns:
        dict com previsão
    """
    # Obter força dos times
    strength1 = team1_stats.get('strength', 50)
    strength2 = team2_stats.get('strength', 50)
    
    # Calcular diferença
    strength_diff = strength1 - strength2
    
    # Ajustar probabilidades
    adjusted_probs = adjust_probabilities_by_strength(strength_diff)
    
    # Escolher placar mais provável
    best_score = max(adjusted_probs.items(), key=lambda x: x[1])
    home_goals, away_goals = best_score[0]
    exact_prob = best_score[1]
    
    # Calcular probabilidades de resultado
    prob_home_win = sum(prob for (h, a), prob in adjusted_probs.items() if h > a)
    prob_draw = sum(prob for (h, a), prob in adjusted_probs.items() if h == a)
    prob_away_win = sum(prob for (h, a), prob in adjusted_probs.items() if h < a)
    
    return {
        'home_goals': home_goals,
        'away_goals': away_goals,
        'strength_diff': round(strength_diff, 1),
        'prob_home_win': round(prob_home_win * 100, 2),
        'prob_draw': round(prob_draw * 100, 2),
        'prob_away_win': round(prob_away_win * 100, 2),
        'exact_score_prob': round(exact_prob * 100, 2),
        'top_5_scores': sorted(adjusted_probs.items(), key=lambda x: x[1], reverse=True)[:5]
    }

# Teste
if __name__ == '__main__':
    print("=" * 80)
    print("MODELO HISTÓRICO - TESTES")
    print("=" * 80)
    
    # Teste 1: Brazil vs Haiti (diferença grande)
    print("\n🏆 TESTE 1: Brazil (75.4) vs Haiti (14.3)")
    print("Diferença: +61.1 (Brazil MUITO mais forte)\n")
    
    brazil_stats = {'strength': 75.4, 'avg_goals_scored': 1.94, 'avg_goals_conceded': 0.74}
    haiti_stats = {'strength': 14.3, 'avg_goals_scored': 2.45, 'avg_goals_conceded': 1.26}
    
    pred = predict_match_historical(brazil_stats, haiti_stats)
    print(f"Placar Previsto: {pred['home_goals']}x{pred['away_goals']}")
    print(f"Prob Placar Exato: {pred['exact_score_prob']}%")
    print(f"Prob Vitória Brazil: {pred['prob_home_win']}%")
    print(f"Prob Empate: {pred['prob_draw']}%")
    print(f"Prob Vitória Haiti: {pred['prob_away_win']}%")
    print("\nTop 5 placares mais prováveis:")
    for (h, a), prob in pred['top_5_scores']:
        print(f"  {h}x{a}: {prob*100:.2f}%")
    
    # Teste 2: Brazil vs Morocco (equilibrado)
    print("\n" + "=" * 80)
    print("\n🏆 TESTE 2: Brazil (75.4) vs Morocco (73.4)")
    print("Diferença: +2.0 (EQUILIBRADO)\n")
    
    morocco_stats = {'strength': 73.4, 'avg_goals_scored': 1.98, 'avg_goals_conceded': 0.46}
    
    pred = predict_match_historical(brazil_stats, morocco_stats)
    print(f"Placar Previsto: {pred['home_goals']}x{pred['away_goals']}")
    print(f"Prob Placar Exato: {pred['exact_score_prob']}%")
    print(f"Prob Vitória Brazil: {pred['prob_home_win']}%")
    print(f"Prob Empate: {pred['prob_draw']}%")
    print(f"Prob Vitória Morocco: {pred['prob_away_win']}%")
    print("\nTop 5 placares mais prováveis:")
    for (h, a), prob in pred['top_5_scores']:
        print(f"  {h}x{a}: {prob*100:.2f}%")
    
    # Teste 3: Haiti vs Brazil (invertido)
    print("\n" + "=" * 80)
    print("\n🏆 TESTE 3: Haiti (14.3) vs Brazil (75.4)")
    print("Diferença: -61.1 (Brazil MUITO mais forte, mas é visitante)\n")
    
    pred = predict_match_historical(haiti_stats, brazil_stats)
    print(f"Placar Previsto: {pred['home_goals']}x{pred['away_goals']}")
    print(f"Prob Placar Exato: {pred['exact_score_prob']}%")
    print(f"Prob Vitória Haiti: {pred['prob_home_win']}%")
    print(f"Prob Empate: {pred['prob_draw']}%")
    print(f"Prob Vitória Brazil: {pred['prob_away_win']}%")
    print("\nTop 5 placares mais prováveis:")
    for (h, a), prob in pred['top_5_scores']:
        print(f"  {h}x{a}: {prob*100:.2f}%")
    
    print("\n" + "=" * 80)
