"""
Estrutura da Copa do Mundo 2026
48 seleções, 12 grupos de 4 times cada
"""

# Grupos da Copa 2026 (baseado no sorteio oficial)
GRUPOS_COPA_2026 = {
    'A': ['United States', 'Wales', 'Panama', 'Trinidad and Tobago'],
    'B': ['Mexico', 'Jamaica', 'Costa Rica', 'Honduras'],
    'C': ['Canada', 'Peru', 'Chile', 'Paraguay'],
    'D': ['Brazil', 'Colombia', 'Ecuador', 'Venezuela'],
    'E': ['Argentina', 'Uruguay', 'Bolivia', 'Haiti'],
    'F': ['England', 'Scotland', 'Republic of Ireland', 'Northern Ireland'],
    'G': ['Spain', 'Portugal', 'Morocco', 'Egypt'],
    'H': ['France', 'Netherlands', 'Belgium', 'Denmark'],
    'I': ['Germany', 'Italy', 'Switzerland', 'Austria'],
    'J': ['Croatia', 'Poland', 'Serbia', 'Ukraine'],
    'K': ['Japan', 'South Korea', 'Australia', 'Iran'],
    'L': ['Senegal', 'Nigeria', 'Cameroon', 'Ghana']
}

# Mapeamento de nomes alternativos
NOME_ALTERNATIVO = {
    'USA': 'United States',
    'US': 'United States',
    'Korea Republic': 'South Korea',
    'IR Iran': 'Iran',
    'Ireland': 'Republic of Ireland'
}

def get_group_matches(grupo, teams):
    """
    Gera todos os jogos de um grupo (cada time joga contra todos)
    6 jogos por grupo (combinação de 4 times, 2 a 2)
    """
    matches = []
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            matches.append({
                'group': grupo,
                'home': teams[i],
                'away': teams[j],
                'phase': 'Grupos'
            })
    return matches

def get_all_group_matches():
    """Retorna todos os 72 jogos da fase de grupos"""
    all_matches = []
    for grupo, teams in GRUPOS_COPA_2026.items():
        matches = get_group_matches(grupo, teams)
        all_matches.extend(matches)
    return all_matches

def get_knockout_structure():
    """
    Estrutura do mata-mata
    - Oitavas: 16 jogos (1º vs 2º de outros grupos)
    - Quartas: 8 jogos
    - Semi: 4 jogos
    - 3º lugar: 1 jogo
    - Final: 1 jogo
    Total: 30 jogos
    """
    knockout = {
        'oitavas': [
            {'match': 1, 'team1': '1A', 'team2': '2B'},
            {'match': 2, 'team1': '1C', 'team2': '2D'},
            {'match': 3, 'team1': '1E', 'team2': '2F'},
            {'match': 4, 'team1': '1G', 'team2': '2H'},
            {'match': 5, 'team1': '1I', 'team2': '2J'},
            {'match': 6, 'team1': '1K', 'team2': '2L'},
            {'match': 7, 'team1': '1B', 'team2': '2A'},
            {'match': 8, 'team1': '1D', 'team2': '2C'},
            {'match': 9, 'team1': '1F', 'team2': '2E'},
            {'match': 10, 'team1': '1H', 'team2': '2G'},
            {'match': 11, 'team1': '1J', 'team2': '2I'},
            {'match': 12, 'team1': '1L', 'team2': '2K'},
            {'match': 13, 'team1': '2º melhor 3º', 'team2': '3º melhor 3º'},
            {'match': 14, 'team1': '1º melhor 3º', 'team2': '4º melhor 3º'},
            {'match': 15, 'team1': '5º melhor 3º', 'team2': '6º melhor 3º'},
            {'match': 16, 'team1': '7º melhor 3º', 'team2': '8º melhor 3º'},
        ],
        'quartas': [
            {'match': 1, 'team1': 'V Oitava 1', 'team2': 'V Oitava 2'},
            {'match': 2, 'team1': 'V Oitava 3', 'team2': 'V Oitava 4'},
            {'match': 3, 'team1': 'V Oitava 5', 'team2': 'V Oitava 6'},
            {'match': 4, 'team1': 'V Oitava 7', 'team2': 'V Oitava 8'},
            {'match': 5, 'team1': 'V Oitava 9', 'team2': 'V Oitava 10'},
            {'match': 6, 'team1': 'V Oitava 11', 'team2': 'V Oitava 12'},
            {'match': 7, 'team1': 'V Oitava 13', 'team2': 'V Oitava 14'},
            {'match': 8, 'team1': 'V Oitava 15', 'team2': 'V Oitava 16'},
        ],
        'semi': [
            {'match': 1, 'team1': 'V Quarta 1', 'team2': 'V Quarta 2'},
            {'match': 2, 'team1': 'V Quarta 3', 'team2': 'V Quarta 4'},
            {'match': 3, 'team1': 'V Quarta 5', 'team2': 'V Quarta 6'},
            {'match': 4, 'team1': 'V Quarta 7', 'team2': 'V Quarta 8'},
        ],
        'terceiro': [
            {'match': 1, 'team1': 'P Semi 1', 'team2': 'P Semi 2'},
            {'match': 2, 'team1': 'P Semi 3', 'team2': 'P Semi 4'},
        ],
        'final': [
            {'match': 1, 'team1': 'V Semi 1', 'team2': 'V Semi 2'},
            {'match': 2, 'team1': 'V Semi 3', 'team2': 'V Semi 4'},
        ]
    }
    return knockout

def count_total_matches():
    """Conta total de jogos"""
    grupos = len(get_all_group_matches())  # 72
    knockout = get_knockout_structure()
    oitavas = len(knockout['oitavas'])  # 16
    quartas = len(knockout['quartas'])  # 8
    semi = len(knockout['semi'])  # 4
    terceiro = len(knockout['terceiro'])  # 2
    final = len(knockout['final'])  # 2
    
    total = grupos + oitavas + quartas + semi + terceiro + final
    
    return {
        'grupos': grupos,
        'oitavas': oitavas,
        'quartas': quartas,
        'semi': semi,
        'terceiro': terceiro,
        'final': final,
        'total': total
    }

if __name__ == "__main__":
    print("=" * 80)
    print("ESTRUTURA DA COPA DO MUNDO 2026")
    print("=" * 80)
    
    print("\n📊 GRUPOS:")
    for grupo, teams in GRUPOS_COPA_2026.items():
        print(f"\nGrupo {grupo}:")
        for team in teams:
            print(f"  - {team}")
    
    print("\n\n🎯 TOTAL DE JOGOS:")
    counts = count_total_matches()
    for fase, count in counts.items():
        print(f"  {fase.capitalize()}: {count}")
    
    print("\n" + "=" * 80)
