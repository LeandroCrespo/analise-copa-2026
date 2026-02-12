"""
Força estimada dos times da Copa 2026
Baseado em ranking FIFA e desempenho histórico
"""

TEAM_STRENGTH = {
    # Grupo A
    'United States': 72,
    'Wales': 68,
    'Panama': 62,
    'Trinidad and Tobago': 58,
    
    # Grupo B
    'Mexico': 70,
    'Jamaica': 64,
    'Costa Rica': 66,
    'Honduras': 60,
    
    # Grupo C
    'Canada': 69,
    'Peru': 67,
    'Chile': 68,
    'Paraguay': 65,
    
    # Grupo D
    'Brazil': 88,
    'Colombia': 74,
    'Ecuador': 70,
    'Venezuela': 63,
    
    # Grupo E
    'Argentina': 87,
    'Uruguay': 76,
    'Bolivia': 61,
    'Haiti': 56,
    
    # Grupo F
    'England': 84,
    'Scotland': 71,
    'Republic of Ireland': 69,
    'Northern Ireland': 67,
    
    # Grupo G
    'Spain': 85,
    'Portugal': 82,
    'Morocco': 73,
    'Egypt': 70,
    
    # Grupo H
    'France': 86,
    'Netherlands': 81,
    'Belgium': 80,
    'Denmark': 75,
    
    # Grupo I
    'Germany': 85,
    'Italy': 83,
    'Switzerland': 77,
    'Austria': 74,
    
    # Grupo J
    'Croatia': 79,
    'Poland': 76,
    'Serbia': 74,
    'Ukraine': 72,
    
    # Grupo K
    'Japan': 75,
    'South Korea': 73,
    'Australia': 71,
    'Iran': 72,
    
    # Grupo L
    'Senegal': 76,
    'Nigeria': 74,
    'Cameroon': 72,
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
