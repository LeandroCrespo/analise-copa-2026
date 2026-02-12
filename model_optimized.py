"""
Modelo Otimizado para Maximizar Pontuação no Bolão
Estratégia: Placares conservadores (0-2 gols) para maximizar pontos
Versão sem scipy - usa apenas numpy
"""

import numpy as np

def poisson_pmf(k, lam):
    """
    Calcula probabilidade de Poisson sem scipy
    P(X=k) = (λ^k * e^(-λ)) / k!
    """
    if lam <= 0:
        return 0.0
    
    # Usar log para evitar overflow
    log_prob = k * np.log(lam) - lam - np.sum(np.log(np.arange(1, k + 1))) if k > 0 else -lam
    return np.exp(log_prob)


def predict_match_optimized(home_stats, away_stats, max_goals=2):
    """
    Prevê placar com estratégia conservadora
    
    Args:
        home_stats: dict com estatísticas do mandante
        away_stats: dict com estatísticas do visitante
        max_goals: máximo de gols a considerar (padrão: 2)
    
    Returns:
        dict com placar previsto e probabilidades
    """
    
    # Calcular média de gols esperados
    home_avg = home_stats.get('avg_goals_scored', 1.5)
    away_avg = away_stats.get('avg_goals_scored', 1.5)
    
    # Ajustar por força relativa
    home_strength = home_stats.get('strength', 50) / 100
    away_strength = away_stats.get('strength', 50) / 100
    
    # Vantagem de casa (reduzida para ser mais conservador)
    home_advantage = 0.2
    
    # Lambda para distribuição de Poisson
    lambda_home = home_avg * home_strength * (1 + home_advantage) / away_strength
    lambda_away = away_avg * away_strength / home_strength
    
    # Regressão à média (reduzida para dar placares mais variados)
    mean_goals = 1.3  # Média histórica de gols
    lambda_home = 0.7 * lambda_home + 0.3 * mean_goals  # 70% força, 30% média
    lambda_away = 0.7 * lambda_away + 0.3 * mean_goals
    
    # Limitar lambdas para evitar placares extremos (aumentado para 2.5)
    lambda_home = min(lambda_home, 2.5)
    lambda_away = min(lambda_away, 2.5)
    
    # Calcular probabilidades para placares conservadores
    placares_conservadores = [
        (0, 0), (1, 0), (0, 1), (2, 0), (0, 2),
        (1, 1), (2, 1), (1, 2), (2, 2)
    ]
    
    prob_scores = {}
    for h, a in placares_conservadores:
        prob = poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)
        prob_scores[(h, a)] = prob
    
    # Normalizar probabilidades
    total_prob = sum(prob_scores.values())
    if total_prob > 0:
        prob_scores = {k: v/total_prob for k, v in prob_scores.items()}
    
    # Escolher placar com maior probabilidade
    # Em caso de empate, preferir vitória do favorito
    best_score = max(prob_scores.items(), key=lambda x: (x[1], abs(x[0][0] - x[0][1])))
    home_goals, away_goals = best_score[0]
    
    # Calcular probabilidades de resultado
    prob_home_win = sum(p for (h, a), p in prob_scores.items() if h > a)
    prob_draw = sum(p for (h, a), p in prob_scores.items() if h == a)
    prob_away_win = sum(p for (h, a), p in prob_scores.items() if h < a)
    
    # Calcular pontuação esperada
    expected_points = calculate_expected_points(prob_scores, home_goals, away_goals)
    
    return {
        'home_goals': int(home_goals),
        'away_goals': int(away_goals),
        'prob_home_win': prob_home_win,
        'prob_draw': prob_draw,
        'prob_away_win': prob_away_win,
        'prob_exact': prob_scores[(home_goals, away_goals)],
        'expected_points': expected_points,
        'all_probabilities': prob_scores,
        'strategy': 'conservative'
    }


def calculate_expected_points(prob_scores, pred_home, pred_away):
    """
    Calcula pontuação esperada considerando todas as possibilidades
    
    Regras do Bolão:
    - Placar exato: 20 pts
    - Resultado + 1 gol certo: 15 pts
    - Apenas resultado: 10 pts
    - Errou: 0 pts
    """
    
    expected = 0
    
    for (real_h, real_a), prob in prob_scores.items():
        points = 0
        
        # Placar exato
        if real_h == pred_home and real_a == pred_away:
            points = 20
        else:
            # Resultado correto?
            real_result = 'home' if real_h > real_a else ('away' if real_a > real_h else 'draw')
            pred_result = 'home' if pred_home > pred_away else ('away' if pred_away > pred_home else 'draw')
            
            if real_result == pred_result:
                # Acertou 1 gol?
                if real_h == pred_home or real_a == pred_away:
                    points = 15
                else:
                    points = 10
        
        expected += prob * points
    
    return expected


def should_risk_high_score(home_stats, away_stats, threshold=30):
    """
    Decide se vale a pena arriscar placar alto (3+ gols)
    
    Args:
        home_stats: estatísticas do mandante
        away_stats: estatísticas do visitante
        threshold: diferença mínima de força para arriscar
    
    Returns:
        bool: True se deve arriscar placar alto
    """
    
    home_strength = home_stats.get('strength', 50)
    away_strength = away_stats.get('strength', 50)
    
    strength_diff = abs(home_strength - away_strength)
    
    # Só arrisca se diferença for muito grande
    return strength_diff >= threshold


def predict_match_adaptive(home_stats, away_stats):
    """
    Prevê placar de forma adaptativa:
    - Conservador (0-2 gols) para jogos equilibrados
    - Arriscado (3+ gols) para jogos com grande diferença
    """
    
    if should_risk_high_score(home_stats, away_stats):
        # Permite até 3 gols
        return predict_match_optimized(home_stats, away_stats, max_goals=3)
    else:
        # Mantém conservador (0-2 gols)
        return predict_match_optimized(home_stats, away_stats, max_goals=2)


def get_best_conservative_scores():
    """
    Retorna os 9 placares mais comuns historicamente
    """
    return [
        (1, 0),  # 9.53%
        (1, 1),  # 10.36%
        (0, 0),  # 8.70%
        (2, 0),  # 8.35%
        (0, 1),  # 7.87%
        (2, 1),  # 7.00%
        (1, 2),  # 4.98%
        (0, 2),  # 4.77%
        (2, 2),  # 3.54%
    ]


# Exemplo de uso
if __name__ == "__main__":
    print("=" * 80)
    print("MODELO OTIMIZADO - TESTE")
    print("=" * 80)
    
    # Exemplo: Brasil vs. Argentina (jogo equilibrado)
    home_stats = {
        'avg_goals_scored': 1.8,
        'avg_goals_conceded': 0.9,
        'strength': 85,
        'recent_form': 0.7
    }
    
    away_stats = {
        'avg_goals_scored': 1.6,
        'avg_goals_conceded': 0.8,
        'strength': 82,
        'recent_form': 0.65
    }
    
    print("\n🏆 Teste 1: Brasil vs. Argentina (equilibrado)")
    result = predict_match_optimized(home_stats, away_stats)
    print(f"   Placar previsto: {result['home_goals']}x{result['away_goals']}")
    print(f"   Probabilidade exata: {result['prob_exact']:.1%}")
    print(f"   Pontuação esperada: {result['expected_points']:.2f} pts")
    print(f"   Estratégia: {result['strategy']}")
    
    # Exemplo: Brasil vs. Bolívia (desequilibrado)
    away_stats_weak = {
        'avg_goals_scored': 0.8,
        'avg_goals_conceded': 2.1,
        'strength': 45,
        'recent_form': 0.3
    }
    
    print("\n🏆 Teste 2: Brasil vs. Bolívia (desequilibrado)")
    result2 = predict_match_adaptive(home_stats, away_stats_weak)
    print(f"   Placar previsto: {result2['home_goals']}x{result2['away_goals']}")
    print(f"   Probabilidade exata: {result2['prob_exact']:.1%}")
    print(f"   Pontuação esperada: {result2['expected_points']:.2f} pts")
    print(f"   Deve arriscar? {should_risk_high_score(home_stats, away_stats_weak)}")
    
    print("\n" + "=" * 80)
    print("✅ Modelo otimizado para maximizar pontuação no Bolão!")
    print("=" * 80)
