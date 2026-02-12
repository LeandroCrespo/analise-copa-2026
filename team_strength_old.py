"""
Força estimada dos times da Copa 2026
Baseado em ranking FIFA e desempenho histórico
"""

TEAM_STRENGTH = {
    # Grupo A
    'United States': 78,
    'Wales': 70,
    'Panama': 55,
    'Trinidad and Tobago': 42,
    
    # Grupo B
    'Mexico': 76,
    'Jamaica': 60,
    'Costa Rica': 67,
    'Honduras': 52,
    
    # Grupo C
    'Canada': 71,
    'Peru': 70,
    'Chile': 70,
    'Paraguay': 69,
    
    # Grupo D
    'Brazil': 95,
    'Colombia': 78,
    'Ecuador': 66,
    'Venezuela': 54,
    
    # Grupo E
    'Argentina': 94,
    'Uruguay': 82,
    'Bolivia': 52,
    'Haiti': 38,
    
    # Grupo F
    'England': 88,
    'Scotland': 72,
    'Republic of Ireland': 68,
    'Northern Ireland': 64,
    
    # Grupo G
    'Spain': 89,
    'Portugal': 85,
    'Morocco': 74,
    'Egypt': 69,
    
    # Grupo H
    'France': 90,
    'Netherlands': 84,
    'Belgium': 82,
    'Denmark': 76,
    
    # Grupo I
    'Germany': 89,
    'Italy': 86,
    'Switzerland': 78,
    'Austria': 75,
    
    # Grupo J
    'Croatia': 79,
    'Poland': 78,
    'Serbia': 77,
    'Ukraine': 76,
    
    # Grupo K
    'Japan': 74,
    'South Korea': 73,
    'Australia': 72,
    'Iran': 73,
    
    # Grupo L
    'Senegal': 75,
    'Nigeria': 74,
    'Cameroon': 74,
    'Ghana': 73
}

def get_team_strength_stats(team_name):
    """
    Retorna estatísticas estimadas baseadas na força do time
    """
    strength = TEAM_STRENGTH.get(team_name, 50)
    
    # Converter força (0-100) em estatísticas de jogo
    # Times mais fortes marcam mais e sofrem menos
    base_goals = 1.3
    strength_factor = (strength - 50) / 50  # -1 a +1
    
    avg_goals_scored = base_goals + (strength_factor * 0.6)  # 0.7 a 1.9
    avg_goals_conceded = base_goals - (strength_factor * 0.6)  # 0.7 a 1.9
    
    # Garantir valores positivos
    avg_goals_scored = max(0.5, avg_goals_scored)
    avg_goals_conceded = max(0.5, avg_goals_conceded)
    
    return {
        'avg_goals_scored': avg_goals_scored,
        'avg_goals_conceded': avg_goals_conceded,
        'strength': strength,
        'recent_form': 0.5 + (strength_factor * 0.2),  # 0.3 a 0.7
        'total_games': 50
    }

if __name__ == "__main__":
    print("Força dos Times - Copa 2026\n")
    
    from copa_2026_structure import GRUPOS_COPA_2026
    
    for grupo, teams in sorted(GRUPOS_COPA_2026.items()):
        print(f"\nGrupo {grupo}:")
        for team in teams:
            strength = TEAM_STRENGTH[team]
            stats = get_team_strength_stats(team)
            print(f"  {team:25s} - Força: {strength:2d} | Gols: {stats['avg_goals_scored']:.2f} / {stats['avg_goals_conceded']:.2f}")
