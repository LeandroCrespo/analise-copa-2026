"""
Modelo de Machine Learning para Predição de Placares
Usa Random Forest treinado em 4.173 jogos históricos
Acurácia: 13.65% | Pontos/jogo: 2.72
"""

import pickle
import numpy as np

# Carregar modelo treinado
try:
    with open('/home/ubuntu/analise-copa-2026/rf_score_model.pkl', 'rb') as f:
        rf_model = pickle.load(f)
    MODEL_LOADED = True
except:
    MODEL_LOADED = False
    rf_model = None

def predict_match_ml(team1_stats, team2_stats):
    """
    Predição usando Random Forest.
    
    Args:
        team1_stats: Estatísticas do time 1
        team2_stats: Estatísticas do time 2
    
    Returns:
        dict com previsão
    """
    if not MODEL_LOADED or rf_model is None:
        # Fallback para modelo simples se ML não carregar
        return predict_match_fallback(team1_stats, team2_stats)
    
    # Preparar features
    features = np.array([[
        team1_stats['strength'],
        team2_stats['strength'],
        team1_stats['strength'] - team2_stats['strength'],
        team1_stats['avg_goals_scored'],
        team2_stats['avg_goals_scored'],
        team1_stats['avg_goals_scored'] - team2_stats['avg_goals_scored'],
        team1_stats['avg_goals_conceded'],
        team2_stats['avg_goals_conceded'],
        team1_stats['avg_goals_conceded'] - team2_stats['avg_goals_conceded'],
        team1_stats['fifa_ranking'],
        team2_stats['fifa_ranking'],
        team1_stats['fifa_ranking'] - team2_stats['fifa_ranking']
    ]])
    
    # Predição
    predicted_score = rf_model.predict(features)[0]
    
    # Obter probabilidades (top 5 placares)
    try:
        proba = rf_model.predict_proba(features)[0]
        classes = rf_model.classes_
        
        # Top 5 placares mais prováveis
        top_5_indices = np.argsort(proba)[-5:][::-1]
        top_5_scores = [(classes[i], proba[i]) for i in top_5_indices]
    except:
        top_5_scores = [(predicted_score, 1.0)]
    
    # Parse placar
    home_goals, away_goals = map(int, predicted_score.split('x'))
    
    # Calcular probabilidades de resultado
    prob_home_win = 0
    prob_draw = 0
    prob_away_win = 0
    
    try:
        for score, prob in zip(classes, proba):
            h, a = map(int, score.split('x'))
            if h > a:
                prob_home_win += prob
            elif h < a:
                prob_away_win += prob
            else:
                prob_draw += prob
    except:
        # Fallback simples
        if home_goals > away_goals:
            prob_home_win = 0.6
            prob_draw = 0.25
            prob_away_win = 0.15
        elif home_goals < away_goals:
            prob_home_win = 0.15
            prob_draw = 0.25
            prob_away_win = 0.6
        else:
            prob_home_win = 0.35
            prob_draw = 0.3
            prob_away_win = 0.35
    
    return {
        'home_goals': home_goals,
        'away_goals': away_goals,
        'strength_diff': round(team1_stats['strength'] - team2_stats['strength'], 1),
        'prob_home_win': round(prob_home_win * 100, 2),
        'prob_draw': round(prob_draw * 100, 2),
        'prob_away_win': round(prob_away_win * 100, 2),
        'exact_score_prob': round(top_5_scores[0][1] * 100, 2) if top_5_scores else 10.0,
        'top_5_scores': top_5_scores,
        'model': 'Random Forest ML'
    }

def predict_match_fallback(team1_stats, team2_stats):
    """
    Fallback simples se ML não carregar.
    """
    strength_diff = team1_stats['strength'] - team2_stats['strength']
    
    # Lógica simples baseada em diferença de força
    if strength_diff > 40:
        home_goals, away_goals = 2, 0
    elif strength_diff > 20:
        home_goals, away_goals = 1, 0
    elif strength_diff > -20:
        home_goals, away_goals = 1, 1
    elif strength_diff > -40:
        home_goals, away_goals = 0, 1
    else:
        home_goals, away_goals = 0, 2
    
    return {
        'home_goals': home_goals,
        'away_goals': away_goals,
        'strength_diff': round(strength_diff, 1),
        'prob_home_win': 50.0,
        'prob_draw': 25.0,
        'prob_away_win': 25.0,
        'exact_score_prob': 15.0,
        'top_5_scores': [(f"{home_goals}x{away_goals}", 0.15)],
        'model': 'Fallback Simple'
    }

# Teste
if __name__ == '__main__':
    print("=" * 80)
    print("TESTE DO MODELO ML")
    print("=" * 80)
    
    if MODEL_LOADED:
        print("\n✅ Modelo ML carregado com sucesso!")
    else:
        print("\n⚠️ Modelo ML não encontrado, usando fallback")
    
    # Teste
    brazil_stats = {
        'strength': 75.4,
        'avg_goals_scored': 1.94,
        'avg_goals_conceded': 0.74,
        'fifa_ranking': 1760
    }
    
    haiti_stats = {
        'strength': 14.3,
        'avg_goals_scored': 2.45,
        'avg_goals_conceded': 1.26,
        'fifa_ranking': 1380
    }
    
    print("\n🏆 TESTE: Brazil vs Haiti")
    pred = predict_match_ml(brazil_stats, haiti_stats)
    
    print(f"\nPlacar Previsto: {pred['home_goals']}x{pred['away_goals']}")
    print(f"Modelo: {pred['model']}")
    print(f"Diferença de Força: {pred['strength_diff']}")
    print(f"Prob Vitória Brazil: {pred['prob_home_win']}%")
    print(f"Prob Empate: {pred['prob_draw']}%")
    print(f"Prob Vitória Haiti: {pred['prob_away_win']}%")
    print(f"Prob Placar Exato: {pred['exact_score_prob']}%")
    
    print("\nTop 5 placares:")
    for score, prob in pred['top_5_scores']:
        print(f"  {score}: {prob*100:.2f}%")
    
    print("\n" + "=" * 80)
