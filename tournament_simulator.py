"""
Simulador de Torneio - Copa do Mundo 2026
Usa Monte Carlo para simular todo o torneio e gerar previsões
"""

import numpy as np
from copa_2026_structure import GRUPOS_COPA_2026, get_all_group_matches
from model_optimized import predict_match_optimized

def simulate_match(team1_stats, team2_stats):
    """
    Simula um jogo e retorna o resultado
    """
    prediction = predict_match_optimized(team1_stats, team2_stats)
    return prediction['home_goals'], prediction['away_goals']

def simulate_group_stage(team_stats_dict):
    """
    Simula toda a fase de grupos
    Retorna classificação de cada grupo
    """
    group_results = {}
    
    for grupo, teams in GRUPOS_COPA_2026.items():
        # Inicializar tabela do grupo
        standings = {team: {'points': 0, 'gf': 0, 'ga': 0, 'gd': 0, 'wins': 0} for team in teams}
        
        # Simular todos os jogos do grupo
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                home = teams[i]
                away = teams[j]
                
                # Obter estatísticas dos times
                home_stats = team_stats_dict.get(home, get_default_stats())
                away_stats = team_stats_dict.get(away, get_default_stats())
                
                # Simular jogo
                home_goals, away_goals = simulate_match(home_stats, away_stats)
                
                # Atualizar tabela
                standings[home]['gf'] += home_goals
                standings[home]['ga'] += away_goals
                standings[away]['gf'] += away_goals
                standings[away]['ga'] += home_goals
                
                if home_goals > away_goals:
                    standings[home]['points'] += 3
                    standings[home]['wins'] += 1
                elif away_goals > home_goals:
                    standings[away]['points'] += 3
                    standings[away]['wins'] += 1
                else:
                    standings[home]['points'] += 1
                    standings[away]['points'] += 1
        
        # Calcular saldo de gols
        for team in standings:
            standings[team]['gd'] = standings[team]['gf'] - standings[team]['ga']
        
        # Ordenar por pontos, saldo de gols, gols feitos
        sorted_teams = sorted(
            standings.items(),
            key=lambda x: (x[1]['points'], x[1]['gd'], x[1]['gf'], x[1]['wins']),
            reverse=True
        )
        
        group_results[grupo] = {
            'standings': sorted_teams,
            'first': sorted_teams[0][0],
            'second': sorted_teams[1][0],
            'third': sorted_teams[2][0],
            'fourth': sorted_teams[3][0]
        }
    
    return group_results

def get_default_stats():
    """Retorna estatísticas padrão para times sem dados"""
    # Esta função é mantida para compatibilidade
    # Use get_team_strength_stats() do módulo team_strength para resultados melhores
    return {
        'avg_goals_scored': 1.3,
        'avg_goals_conceded': 1.3,
        'strength': 50,
        'recent_form': 0.5,
        'total_games': 50
    }

def simulate_knockout_stage(group_results, team_stats_dict):
    """
    Simula fase de mata-mata
    """
    # Oitavas de final (32 times -> 16 times)
    round_of_16 = []
    
    # Pegar os 2 primeiros de cada grupo (24 times)
    # + 8 melhores terceiros colocados
    qualified = []
    for grupo in sorted(group_results.keys()):
        qualified.append(group_results[grupo]['first'])
        qualified.append(group_results[grupo]['second'])
    
    # Adicionar melhores terceiros (simplificado - pegar 8 primeiros)
    thirds = []
    for grupo in sorted(group_results.keys()):
        third_team = group_results[grupo]['third']
        third_stats = group_results[grupo]['standings'][2][1]
        thirds.append((third_team, third_stats))
    
    # Ordenar terceiros por pontos, saldo, gols
    thirds_sorted = sorted(
        thirds,
        key=lambda x: (x[1]['points'], x[1]['gd'], x[1]['gf']),
        reverse=True
    )[:8]
    
    for team, _ in thirds_sorted:
        qualified.append(team)
    
    # Simular oitavas (32 times -> 16)
    quarters = []
    for i in range(0, len(qualified), 2):
        if i + 1 < len(qualified):
            team1 = qualified[i]
            team2 = qualified[i + 1]
            
            stats1 = team_stats_dict.get(team1, get_default_stats())
            stats2 = team_stats_dict.get(team2, get_default_stats())
            
            goals1, goals2 = simulate_match(stats1, stats2)
            
            # Em caso de empate, vence quem tem melhor ranking
            if goals1 > goals2:
                quarters.append(team1)
            elif goals2 > goals1:
                quarters.append(team2)
            else:
                # Empate - usar força do time
                if stats1['strength'] >= stats2['strength']:
                    quarters.append(team1)
                else:
                    quarters.append(team2)
    
    # Simular quartas (16 -> 8)
    semis = []
    for i in range(0, len(quarters), 2):
        if i + 1 < len(quarters):
            team1 = quarters[i]
            team2 = quarters[i + 1]
            
            stats1 = team_stats_dict.get(team1, get_default_stats())
            stats2 = team_stats_dict.get(team2, get_default_stats())
            
            goals1, goals2 = simulate_match(stats1, stats2)
            
            if goals1 > goals2:
                semis.append(team1)
            elif goals2 > goals1:
                semis.append(team2)
            else:
                if stats1['strength'] >= stats2['strength']:
                    semis.append(team1)
                else:
                    semis.append(team2)
    
    # Simular semifinais (8 -> 4)
    finals = []
    third_place_match = []
    for i in range(0, len(semis), 2):
        if i + 1 < len(semis):
            team1 = semis[i]
            team2 = semis[i + 1]
            
            stats1 = team_stats_dict.get(team1, get_default_stats())
            stats2 = team_stats_dict.get(team2, get_default_stats())
            
            goals1, goals2 = simulate_match(stats1, stats2)
            
            if goals1 > goals2:
                finals.append(team1)
                third_place_match.append(team2)
            elif goals2 > goals1:
                finals.append(team2)
                third_place_match.append(team1)
            else:
                if stats1['strength'] >= stats2['strength']:
                    finals.append(team1)
                    third_place_match.append(team2)
                else:
                    finals.append(team2)
                    third_place_match.append(team1)
    
    # Simular disputa de 3º lugar
    if len(third_place_match) >= 2:
        team1 = third_place_match[0]
        team2 = third_place_match[1]
        
        stats1 = team_stats_dict.get(team1, get_default_stats())
        stats2 = team_stats_dict.get(team2, get_default_stats())
        
        goals1, goals2 = simulate_match(stats1, stats2)
        
        if goals1 > goals2:
            third_place = team1
        elif goals2 > goals1:
            third_place = team2
        else:
            third_place = team1 if stats1['strength'] >= stats2['strength'] else team2
    else:
        third_place = None
    
    # Simular final
    if len(finals) >= 2:
        team1 = finals[0]
        team2 = finals[1]
        
        stats1 = team_stats_dict.get(team1, get_default_stats())
        stats2 = team_stats_dict.get(team2, get_default_stats())
        
        goals1, goals2 = simulate_match(stats1, stats2)
        
        if goals1 > goals2:
            champion = team1
            runner_up = team2
        elif goals2 > goals1:
            champion = team2
            runner_up = team1
        else:
            if stats1['strength'] >= stats2['strength']:
                champion = team1
                runner_up = team2
            else:
                champion = team2
                runner_up = team1
    else:
        champion = None
        runner_up = None
    
    return {
        'champion': champion,
        'runner_up': runner_up,
        'third_place': third_place,
        'semi_finalists': semis,
        'quarter_finalists': quarters,
        'round_of_16': qualified
    }

def simulate_full_tournament(team_stats_dict, n_simulations=1000):
    """
    Simula o torneio completo N vezes e retorna probabilidades
    """
    champions_count = {}
    podium_count = {}
    
    for _ in range(n_simulations):
        # Simular fase de grupos
        group_results = simulate_group_stage(team_stats_dict)
        
        # Simular mata-mata
        knockout_results = simulate_knockout_stage(group_results, team_stats_dict)
        
        # Contar campeão
        champion = knockout_results['champion']
        if champion:
            champions_count[champion] = champions_count.get(champion, 0) + 1
        
        # Contar pódio
        for team in [knockout_results['champion'], knockout_results['runner_up'], knockout_results['third_place']]:
            if team:
                podium_count[team] = podium_count.get(team, 0) + 1
    
    # Calcular probabilidades
    champion_probs = {team: count / n_simulations for team, count in champions_count.items()}
    podium_probs = {team: count / n_simulations for team, count in podium_count.items()}
    
    # Ordenar por probabilidade
    champion_probs = dict(sorted(champion_probs.items(), key=lambda x: x[1], reverse=True))
    podium_probs = dict(sorted(podium_probs.items(), key=lambda x: x[1], reverse=True))
    
    return {
        'champion_probabilities': champion_probs,
        'podium_probabilities': podium_probs
    }

if __name__ == "__main__":
    print("Simulador de Torneio - Copa 2026")
    print("Teste básico com estatísticas padrão...")
    
    # Criar dicionário de estatísticas padrão
    team_stats = {}
    for grupo, teams in GRUPOS_COPA_2026.items():
        for team in teams:
            team_stats[team] = get_default_stats()
    
    # Simular fase de grupos
    group_results = simulate_group_stage(team_stats)
    
    print("\n📊 CLASSIFICAÇÃO DOS GRUPOS:")
    for grupo in sorted(group_results.keys()):
        print(f"\nGrupo {grupo}:")
        print(f"  1º: {group_results[grupo]['first']}")
        print(f"  2º: {group_results[grupo]['second']}")
    
    print("\n✅ Simulador funcionando!")
