"""
Força dos times baseada em DADOS REAIS:
1. Dados históricos do Neon (2020-2026)
2. Ranking FIFA (19 Janeiro 2026)

Força calculada como:
- 10% baseada em gols marcados vs média
- 10% baseada em gols sofridos vs média  
- 80% baseada em ranking FIFA normalizado
"""

# Dados históricos do Neon (gols por jogo desde 2020)
NEON_STATS = {
    'Argentina': {'scored': 2.06, 'conceded': 0.45, 'games': 71},
    'Australia': {'scored': 1.77, 'conceded': 0.75, 'games': 57},
    'Austria': {'scored': 1.84, 'conceded': 1.07, 'games': 68},
    'Belgium': {'scored': 2.11, 'conceded': 0.93, 'games': 71},
    'Bolivia': {'scored': 0.92, 'conceded': 1.98, 'games': 65},
    'Brazil': {'scored': 1.94, 'conceded': 0.74, 'games': 66},
    'Cameroon': {'scored': 1.38, 'conceded': 0.83, 'games': 66},
    'Canada': {'scored': 1.88, 'conceded': 0.89, 'games': 76},
    'Chile': {'scored': 1.06, 'conceded': 1.22, 'games': 65},
    'Colombia': {'scored': 1.62, 'conceded': 0.88, 'games': 68},
    'Costa Rica': {'scored': 1.40, 'conceded': 1.17, 'games': 81},
    'Croatia': {'scored': 1.75, 'conceded': 1.07, 'games': 73},
    'Denmark': {'scored': 1.90, 'conceded': 0.90, 'games': 71},
    'Ecuador': {'scored': 1.16, 'conceded': 0.80, 'games': 70},
    'Egypt': {'scored': 1.56, 'conceded': 0.69, 'games': 75},
    'England': {'scored': 2.18, 'conceded': 0.58, 'games': 77},
    'France': {'scored': 2.17, 'conceded': 0.88, 'games': 75},
    'Germany': {'scored': 2.21, 'conceded': 1.21, 'games': 72},
    'Ghana': {'scored': 1.27, 'conceded': 1.13, 'games': 62},
    'Haiti': {'scored': 2.45, 'conceded': 1.26, 'games': 47},
    'Honduras': {'scored': 1.15, 'conceded': 1.35, 'games': 74},
    'Iran': {'scored': 2.07, 'conceded': 0.73, 'games': 60},
    'Italy': {'scored': 1.90, 'conceded': 0.99, 'games': 72},
    'Jamaica': {'scored': 1.27, 'conceded': 1.26, 'games': 78},
    'Japan': {'scored': 2.67, 'conceded': 0.67, 'games': 69},
    'Mexico': {'scored': 1.42, 'conceded': 0.90, 'games': 99},
    'Morocco': {'scored': 1.98, 'conceded': 0.46, 'games': 84},
    'Netherlands': {'scored': 2.36, 'conceded': 0.99, 'games': 73},
    'Nigeria': {'scored': 1.56, 'conceded': 0.91, 'games': 70},
    'Northern Ireland': {'scored': 1.09, 'conceded': 1.24, 'games': 58},
    'Panama': {'scored': 1.61, 'conceded': 1.23, 'games': 88},
    'Paraguay': {'scored': 0.87, 'conceded': 1.20, 'games': 60},
    'Peru': {'scored': 0.89, 'conceded': 1.15, 'games': 65},
    'Poland': {'scored': 1.67, 'conceded': 1.26, 'games': 69},
    'Portugal': {'scored': 2.45, 'conceded': 0.80, 'games': 74},
    'Republic of Ireland': {'scored': 1.10, 'conceded': 1.13, 'games': 60},
    'Scotland': {'scored': 1.42, 'conceded': 1.24, 'games': 66},
    'Senegal': {'scored': 1.80, 'conceded': 0.64, 'games': 80},
    'Serbia': {'scored': 1.55, 'conceded': 1.06, 'games': 67},
    'South Korea': {'scored': 2.00, 'conceded': 0.93, 'games': 69},
    'Spain': {'scored': 2.33, 'conceded': 0.79, 'games': 76},
    'Switzerland': {'scored': 1.77, 'conceded': 1.18, 'games': 73},
    'Trinidad and Tobago': {'scored': 1.59, 'conceded': 1.44, 'games': 63},
    'Ukraine': {'scored': 1.40, 'conceded': 1.45, 'games': 67},
    'United States': {'scored': 1.95, 'conceded': 0.86, 'games': 92},
    'Uruguay': {'scored': 1.34, 'conceded': 0.82, 'games': 67},
    'Venezuela': {'scored': 0.98, 'conceded': 1.40, 'games': 60},
    'Wales': {'scored': 1.27, 'conceded': 1.14, 'games': 66},
}

# Ranking FIFA (19 Janeiro 2026)
FIFA_RANKING = {
    'Spain': 1877.18,
    'Argentina': 1873.33,
    'France': 1870.00,
    'England': 1834.12,
    'Brazil': 1760.46,
    'Portugal': 1760.38,
    'Netherlands': 1756.27,
    'Morocco': 1736.56,
    'Belgium': 1730.71,
    'Germany': 1724.15,
    'Croatia': 1716.88,
    'Italy': 1702.06,
    'Colombia': 1701.30,
    'Senegal': 1684.86,
    'United States': 1681.88,
    'Mexico': 1675.75,
    'Uruguay': 1672.62,
    'Switzerland': 1654.69,
    'Japan': 1650.12,
    'Iran': 1617.02,
    'Denmark': 1616.75,
    'South Korea': 1599.45,
    'Ecuador': 1591.73,
    'Austria': 1585.51,
    'Nigeria': 1581.56,
    'Australia': 1574.01,
    'Canada': 1559.15,
    'Ukraine': 1557.47,
    'Egypt': 1556.72,
    'Panama': 1540.43,
    'Poland': 1532.04,
    'Wales': 1529.71,
    'Scotland': 1506.77,
    'Serbia': 1506.34,
    'Paraguay': 1501.50,
    'Cameroon': 1482.39,
    'Ghana': 1470.00,  # Estimado
    'Peru': 1460.00,  # Estimado
    'Chile': 1455.00,  # Estimado
    'Venezuela': 1465.22,
    'Jamaica': 1440.00,  # Estimado
    'Costa Rica': 1435.00,  # Estimado
    'Honduras': 1420.00,  # Estimado
    'Bolivia': 1410.00,  # Estimado
    'Haiti': 1380.00,  # Estimado
    'Trinidad and Tobago': 1370.00,  # Estimado
    'Republic of Ireland': 1500.00,  # Estimado
    'Northern Ireland': 1480.00,  # Estimado
}

def calculate_team_strength(team_name):
    """
    Calcula força do time (0-100) baseada em dados reais.
    
    Fórmula:
    - 10% baseada em gols marcados (vs média de 1.66)
    - 10% baseada em gols sofridos (vs média de 1.05)
    - 80% baseada em ranking FIFA normalizado
    """
    # Médias gerais
    AVG_GOALS_SCORED = 1.66
    AVG_GOALS_CONCEDED = 1.05
    
    # Pegar dados do time
    neon_data = NEON_STATS.get(team_name, {'scored': AVG_GOALS_SCORED, 'conceded': AVG_GOALS_CONCEDED})
    fifa_points = FIFA_RANKING.get(team_name, 1500.0)
    
    # Componente 1: Gols marcados (0-100)
    # Time que marca 2.67 gols/jogo (Japan) = 100
    # Time que marca 0.87 gols/jogo (Paraguay) = 0
    scored_component = ((neon_data['scored'] - 0.5) / 2.5) * 100
    scored_component = max(0, min(100, scored_component))
    
    # Componente 2: Gols sofridos (0-100, invertido)
    # Time que sofre 0.45 gols/jogo (Argentina) = 100
    # Time que sofre 1.98 gols/jogo (Bolivia) = 0
    conceded_component = ((2.0 - neon_data['conceded']) / 1.5) * 100
    conceded_component = max(0, min(100, conceded_component))
    
    # Componente 3: Ranking FIFA (0-100)
    # Spain (1877) = 100, Haiti (1380) = 0
    fifa_component = ((fifa_points - 1370) / 510) * 100
    fifa_component = max(0, min(100, fifa_component))
    
    # Força final (média ponderada)
    strength = (
        0.10 * scored_component +
        0.10 * conceded_component +
        0.80 * fifa_component
    )
    
    return round(strength, 1)

def get_team_strength_stats(team_name):
    """
    Retorna estatísticas do time no formato esperado pelo modelo.
    """
    neon_data = NEON_STATS.get(team_name, {'scored': 1.66, 'conceded': 1.05, 'games': 50})
    fifa_ranking = FIFA_RANKING.get(team_name, 1500)
    strength = calculate_team_strength(team_name)
    
    return {
        'avg_goals_scored': neon_data['scored'],
        'avg_goals_conceded': neon_data['conceded'],
        'total_games': neon_data['games'],
        'fifa_ranking': fifa_ranking,
        'strength': strength  # Mantido para compatibilidade
    }

# Teste
if __name__ == '__main__':
    print("🎯 FORÇA DOS TIMES (DADOS REAIS)\n")
    print("Baseado em:")
    print("- Dados históricos Neon (2020-2026)")
    print("- Ranking FIFA (19 Jan 2026)\n")
    
    from copa_2026_structure import GRUPOS_COPA_2026
    
    all_teams = []
    for grupo, teams in GRUPOS_COPA_2026.items():
        all_teams.extend(teams)
    
    # Ordenar por força
    teams_strength = [(team, calculate_team_strength(team)) for team in all_teams]
    teams_strength.sort(key=lambda x: x[1], reverse=True)
    
    print("Top 10 mais fortes:")
    for i, (team, strength) in enumerate(teams_strength[:10], 1):
        neon = NEON_STATS[team]
        fifa = FIFA_RANKING[team]
        print(f"{i:2d}. {team:20s} - Força: {strength:5.1f} | Gols: {neon['scored']:.2f} | Sofre: {neon['conceded']:.2f} | FIFA: {fifa:.0f}")
    
    print("\nTop 10 mais fracos:")
    for i, (team, strength) in enumerate(teams_strength[-10:], 1):
        neon = NEON_STATS[team]
        fifa = FIFA_RANKING[team]
        print(f"{i:2d}. {team:20s} - Força: {strength:5.1f} | Gols: {neon['scored']:.2f} | Sofre: {neon['conceded']:.2f} | FIFA: {fifa:.0f}")
    
    print(f"\n📊 Distribuição:")
    print(f"  Força máxima: {teams_strength[0][1]:.1f} ({teams_strength[0][0]})")
    print(f"  Força mínima: {teams_strength[-1][1]:.1f} ({teams_strength[-1][0]})")
    print(f"  Diferença: {teams_strength[0][1] - teams_strength[-1][1]:.1f}")
