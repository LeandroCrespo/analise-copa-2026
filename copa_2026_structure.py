"""
Estrutura Oficial dos Grupos da Copa do Mundo 2026
Fonte: FIFA/GE (05 dez 2025)
48 times divididos em 12 grupos de 4 times cada
"""

# Estrutura oficial dos grupos após sorteio de 05/12/2025
GRUPOS_COPA_2026 = {
    "A": ["Mexico", "South Africa", "Korea Republic", "Repescagem Europa D"],
    "B": ["Canada", "Repescagem Europa A", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Repescagem Europa C"],
    "E": ["Germany", "Curaçao", "Côte d'Ivoire", "Ecuador"],
    "F": ["Netherlands", "Japan", "Repescagem Europa B", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cabo Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Repescagem Intercontinental 2", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "Repescagem Intercontinental 1", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"]
}

# Repescagens pendentes (a serem definidas em março 2026)
REPESCAGENS = {
    "Europa A": ["Italy", "Northern Ireland", "Wales", "Bosnia and Herzegovina"],
    "Europa B": ["Ukraine", "Sweden", "Poland", "Albania"],
    "Europa C": ["Turkey", "Romania", "Slovakia", "Kosovo"],
    "Europa D": ["Czech Republic", "Republic of Ireland", "Denmark", "North Macedonia"],
    "Intercontinental 1": ["DR Congo", "Jamaica", "New Caledonia"],
    "Intercontinental 2": ["Bolivia", "Suriname", "Iraq"]
}

# Mapeamento de nomes para exibição
DISPLAY_NAMES = {
    "Korea Republic": "Coreia do Sul",
    "South Africa": "África do Sul",
    "United States": "Estados Unidos",
    "Côte d'Ivoire": "Costa do Marfim",
    "Saudi Arabia": "Arábia Saudita",
    "Cabo Verde": "Cabo Verde",
    "New Zealand": "Nova Zelândia",
    "Czech Republic": "República Tcheca",
    "Republic of Ireland": "Irlanda",
    "North Macedonia": "Macedônia do Norte",
    "Northern Ireland": "Irlanda do Norte",
    "Bosnia and Herzegovina": "Bósnia e Herzegovina",
    "DR Congo": "RD Congo",
    "New Caledonia": "Nova Caledônia",
    "Repescagem Europa A": "Repescagem Europa A",
    "Repescagem Europa B": "Repescagem Europa B",
    "Repescagem Europa C": "Repescagem Europa C",
    "Repescagem Europa D": "Repescagem Europa D",
    "Repescagem Intercontinental 1": "Repescagem Intercontinental 1",
    "Repescagem Intercontinental 2": "Repescagem Intercontinental 2"
}

def get_display_name(team_name):
    """Retorna nome para exibição"""
    return DISPLAY_NAMES.get(team_name, team_name)

def is_repescagem(team_name):
    """Verifica se é uma vaga de repescagem"""
    return team_name.startswith("Repescagem")

def get_repescagem_candidates(repescagem_name):
    """Retorna candidatos de uma repescagem"""
    # Extrair chave (ex: "Repescagem Europa A" -> "Europa A")
    key = repescagem_name.replace("Repescagem ", "")
    return REPESCAGENS.get(key, [])

def get_all_teams():
    """Retorna lista de todos os times (incluindo repescagens)"""
    teams = []
    for grupo_teams in GRUPOS_COPA_2026.values():
        teams.extend(grupo_teams)
    return sorted(set(teams))

def get_confirmed_teams():
    """Retorna apenas times confirmados (sem repescagens)"""
    all_teams = get_all_teams()
    return [t for t in all_teams if not is_repescagem(t)]

def get_grupo_info(grupo_letter):
    """Retorna informações de um grupo"""
    teams = GRUPOS_COPA_2026.get(grupo_letter, [])
    
    info = {
        'letter': grupo_letter,
        'teams': teams,
        'confirmed': [t for t in teams if not is_repescagem(t)],
        'pending': [t for t in teams if is_repescagem(t)]
    }
    
    return info

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
    - Oitavas: 16 jogos (1º vs 2º de outros grupos + 8 melhores 3º)
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

# Estatísticas
TOTAL_GROUPS = len(GRUPOS_COPA_2026)
TOTAL_TEAMS = 48
CONFIRMED_TEAMS = len(get_confirmed_teams())
PENDING_TEAMS = TOTAL_TEAMS - CONFIRMED_TEAMS

if __name__ == "__main__":
    print("=" * 80)
    print("ESTRUTURA DA COPA DO MUNDO 2026")
    print("=" * 80)
    
    print(f"\n📊 Estatísticas:")
    print(f"   Total de grupos: {TOTAL_GROUPS}")
    print(f"   Total de times: {TOTAL_TEAMS}")
    print(f"   Times confirmados: {CONFIRMED_TEAMS}")
    print(f"   Vagas pendentes: {PENDING_TEAMS}")
    
    print(f"\n🏆 Grupos:\n")
    
    for grupo, teams in sorted(GRUPOS_COPA_2026.items()):
        print(f"Grupo {grupo}:")
        for team in teams:
            if is_repescagem(team):
                candidates = get_repescagem_candidates(team)
                print(f"  ⏳ {team}")
                print(f"     Candidatos: {', '.join(candidates)}")
            else:
                print(f"  ✅ {team}")
        print()
    
    print("\n🎯 TOTAL DE JOGOS:")
    counts = count_total_matches()
    for fase, count in counts.items():
        print(f"  {fase.capitalize()}: {count}")
    
    print("\n" + "=" * 80)
    print("✅ Estrutura oficial após sorteio de 05/12/2025")
    print("⏳ Repescagens serão definidas em março 2026")
    print("=" * 80)
