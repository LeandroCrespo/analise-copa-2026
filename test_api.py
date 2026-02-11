"""
Testar API-Football para verificar dados disponíveis
"""

import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"

print("=" * 80)
print("TESTE DA API-FOOTBALL")
print("=" * 80)

print(f"\n🔑 API Key: {API_KEY[:10]}...")

headers = {
    'x-rapidapi-host': 'v3.football.api-sports.io',
    'x-rapidapi-key': API_KEY
}

# Teste 1: Status da API
print("\n" + "=" * 80)
print("TESTE 1: STATUS DA API")
print("=" * 80)

try:
    response = requests.get(f"{BASE_URL}/status", headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ API Funcionando!")
        print(f"\nInformações da conta:")
        print(json.dumps(data, indent=2))
    else:
        print(f"\n❌ Erro: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"\n❌ Erro: {e}")

# Teste 2: Buscar seleções (teams)
print("\n" + "=" * 80)
print("TESTE 2: BUSCAR SELEÇÕES")
print("=" * 80)

print("\n🔍 Buscando 'Brazil'...")

try:
    response = requests.get(
        f"{BASE_URL}/teams",
        headers=headers,
        params={"search": "Brazil"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Resposta recebida!")
        print(f"\nTotal de resultados: {data.get('results', 0)}")
        
        if data.get('response'):
            print(f"\nPrimeiros 5 resultados:")
            for team in data['response'][:5]:
                print(f"  - ID: {team['team']['id']}, Nome: {team['team']['name']}, País: {team['team'].get('country', 'N/A')}")
        else:
            print("\n⚠️ Nenhum resultado encontrado")
    else:
        print(f"\n❌ Erro: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"\n❌ Erro: {e}")

# Teste 3: Buscar jogos do Brasil
print("\n" + "=" * 80)
print("TESTE 3: BUSCAR JOGOS DO BRASIL")
print("=" * 80)

print("\n🔍 Buscando jogos do Brasil (team ID: 6)...")

try:
    response = requests.get(
        f"{BASE_URL}/fixtures",
        headers=headers,
        params={
            "team": 6,
            "last": 10
        }
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Resposta recebida!")
        print(f"\nTotal de resultados: {data.get('results', 0)}")
        
        if data.get('response'):
            print(f"\nÚltimos 5 jogos:")
            for match in data['response'][:5]:
                fixture = match['fixture']
                teams = match['teams']
                goals = match['goals']
                print(f"  - {fixture['date'][:10]}: {teams['home']['name']} {goals['home']} x {goals['away']} {teams['away']['name']}")
        else:
            print("\n⚠️ Nenhum jogo encontrado")
    else:
        print(f"\n❌ Erro: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"\n❌ Erro: {e}")

# Teste 4: Listar ligas/competições
print("\n" + "=" * 80)
print("TESTE 4: LISTAR COMPETIÇÕES INTERNACIONAIS")
print("=" * 80)

print("\n🔍 Buscando competições internacionais...")

try:
    response = requests.get(
        f"{BASE_URL}/leagues",
        headers=headers,
        params={
            "type": "cup",
            "current": "true"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Resposta recebida!")
        print(f"\nTotal de resultados: {data.get('results', 0)}")
        
        if data.get('response'):
            print(f"\nPrimeiras 10 competições:")
            for league in data['response'][:10]:
                print(f"  - ID: {league['league']['id']}, Nome: {league['league']['name']}, País: {league.get('country', {}).get('name', 'Internacional')}")
        else:
            print("\n⚠️ Nenhuma competição encontrada")
    else:
        print(f"\n❌ Erro: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"\n❌ Erro: {e}")

# Teste 5: Buscar Copa do Mundo
print("\n" + "=" * 80)
print("TESTE 5: BUSCAR COPA DO MUNDO")
print("=" * 80)

print("\n🔍 Buscando 'World Cup'...")

try:
    response = requests.get(
        f"{BASE_URL}/leagues",
        headers=headers,
        params={"search": "World Cup"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Resposta recebida!")
        print(f"\nTotal de resultados: {data.get('results', 0)}")
        
        if data.get('response'):
            print(f"\nResultados:")
            for league in data['response']:
                print(f"  - ID: {league['league']['id']}, Nome: {league['league']['name']}")
        else:
            print("\n⚠️ Nenhuma competição encontrada")
    else:
        print(f"\n❌ Erro: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"\n❌ Erro: {e}")

print("\n" + "=" * 80)
print("CONCLUSÃO")
print("=" * 80)

print("""
✅ Testes concluídos!

💡 Próximos passos:
  1. Verificar se a API retornou dados
  2. Identificar IDs corretos das seleções
  3. Ajustar código de coleta se necessário
  4. Re-executar coleta de dados
""")

print("=" * 80)
