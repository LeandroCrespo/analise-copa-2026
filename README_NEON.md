# 🏆 Sistema de Análise e Previsão - Copa do Mundo 2026

Sistema completo de análise estatística e previsão de resultados para a Copa do Mundo 2026, com banco de dados Neon PostgreSQL e atualização incremental automática.

---

## 📊 Visão Geral

Este sistema foi desenvolvido para auxiliar na geração de palpites inteligentes para o Bolão Copa 2026, utilizando:

- ✅ **Análise estatística** de dados históricos reais
- ✅ **Modelos probabilísticos** (Distribuição de Poisson)
- ✅ **Banco de dados Neon PostgreSQL** (persistente e escalável)
- ✅ **Atualização incremental** (apenas dados novos)
- ✅ **Sistema adaptativo** (melhora durante a Copa)

---

## 🗄️ Banco de Dados Neon

### Configuração

```
Project ID: restless-glitter-71170845
Database: neondb
Região: US East (AWS)
Tipo: PostgreSQL (Serverless)
```

### Schema

**9 Tabelas Principais:**

1. `teams` - Seleções participantes
2. `matches` - Histórico de jogos
3. `team_stats` - Estatísticas gerais (cache)
4. `team_recent_form` - Forma recente (últimos 10 jogos)
5. `predictions` - Previsões geradas pelo modelo
6. `user_predictions` - Seus palpites para os jogos
7. `group_predictions` - Palpites de classificação dos grupos
8. `podium_prediction` - Palpite de pódio (1º, 2º, 3º)
9. `update_log` - Log de atualizações

---

## 🚀 Como Usar

### 1. Configuração Inicial

```bash
# Clonar repositório
git clone https://github.com/LeandroCrespo/analise-copa-2026.git
cd analise-copa-2026

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env e adicionar API_FOOTBALL_KEY
```

### 2. Importar Dados Históricos (Primeira Vez)

```bash
# Opção 1: Importar do Kaggle (recomendado - 3.000+ jogos)
python import_kaggle_to_neon.py

# Opção 2: Coletar da API-Football
python collect_full_data.py
```

### 3. Atualizar Dados (Diariamente)

```bash
# Busca apenas jogos novos/atualizados
python update_incremental.py
```

### 4. Gerar Previsões

```bash
# Executar dashboard
streamlit run app/dashboard.py

# Ou via Python
python -c "from src.model import MatchPredictor; p = MatchPredictor(); print(p.predict_match_score(6, 26))"
```

---

## 📁 Estrutura do Projeto

```
analise-copa-2026/
├── data/
│   ├── raw/                    # Dados brutos (CSV do Kaggle)
│   └── processed/              # Dados processados
├── src/
│   ├── config.py               # Configurações
│   ├── utils.py                # Utilidades
│   ├── data_collection.py      # Coleta via API
│   ├── data_processing.py      # Processamento
│   ├── model.py                # Modelo de previsão
│   ├── adaptive_model.py       # Modelo adaptativo
│   └── live_updater.py         # Atualização em tempo real
├── app/
│   └── dashboard.py            # Dashboard Streamlit
├── database_schema.sql         # Schema completo do banco
├── create_schema_neon.py       # Criar schema no Neon
├── import_kaggle_to_neon.py    # Importar dados do Kaggle
├── collect_full_data.py        # Coleta completa via API
├── update_incremental.py       # Atualização incremental
├── requirements.txt            # Dependências
├── .env.example                # Exemplo de variáveis
└── README_NEON.md              # Este arquivo
```

---

## 🔄 Sistema de Atualização Incremental

### Como Funciona

1. **Verifica última atualização** no `update_log`
2. **Busca apenas jogos novos** desde a última atualização
3. **Insere novos jogos** ou **atualiza existentes**
4. **Registra no log** para próxima execução

### Vantagens

- ✅ **Econômico**: Usa poucas requisições da API
- ✅ **Rápido**: Processa apenas o necessário
- ✅ **Inteligente**: Evita duplicação de dados
- ✅ **Automático**: Pode rodar via cron job

### Exemplo de Uso

```bash
# Executar manualmente
python update_incremental.py

# Ou configurar cron (Linux/Mac)
# Executar 2x por dia (8h e 20h)
0 8,20 * * * cd /path/to/analise-copa-2026 && python update_incremental.py
```

---

## 📊 Tipos de Palpites Gerados

### 1. Placares Exatos (128 jogos)

```python
from src.model import MatchPredictor

predictor = MatchPredictor()
prediction = predictor.predict_match_score(
    home_team_id=6,   # Brasil
    away_team_id=26   # Argentina
)

print(f"Placar: {prediction['predicted_home_goals']} x {prediction['predicted_away_goals']}")
print(f"Probabilidades: {prediction['prob_home_win']:.1%} / {prediction['prob_draw']:.1%} / {prediction['prob_away_win']:.1%}")
```

### 2. Classificação dos Grupos (12 grupos)

```python
from src.adaptive_model import GroupStagePredictor

group_predictor = GroupStagePredictor()
standings = group_predictor.predict_group_standings('A')

print(f"1º: {standings[0]['team']}")
print(f"2º: {standings[1]['team']}")
```

### 3. Pódio (Campeão, Vice, 3º)

```python
from src.adaptive_model import TournamentSimulator

simulator = TournamentSimulator()
podium = simulator.simulate_tournament(n_simulations=1000)

print(f"Campeão: {podium['champion']}")
print(f"Vice: {podium['runner_up']}")
print(f"3º Lugar: {podium['third_place']}")
```

---

## 🧠 Como o Modelo Funciona

### Metodologia

1. **Coleta de Dados Históricos**
   - Jogos das seleções nos últimos 10 anos
   - Fonte: Kaggle + API-Football

2. **Análise Estatística**
   - Taxa de vitórias
   - Média de gols (marcados/sofridos)
   - Forma recente (últimos 10 jogos)
   - Saldo de gols

3. **Cálculo de Força** (0-100)
   ```
   Força = (Taxa Vitória × 40%) + 
           (Saldo Gols × 30%) + 
           (Forma Recente × 30%)
   ```

4. **Previsão de Gols** (Distribuição de Poisson)
   ```
   Gols Esperados = Média Histórica + 
                    Ajuste por Adversário +
                    Vantagem de Casa (+0.3)
   ```

5. **Cálculo de Probabilidades**
   - Simula milhares de cenários
   - Gera probabilidades de vitória/empate/derrota
   - Calcula intervalo de confiança

### Precisão Esperada

| Métrica | Taxa Esperada |
|---------|---------------|
| Placar Exato | 10-15% |
| Resultado Correto | 50-60% |
| Gols de um Time | 30-40% |
| Pontos Médios | 10-12 pts/jogo |

---

## 🔧 Manutenção

### Verificar Status do Banco

```bash
# Via MCP
manus-mcp-cli tool call run_sql --server neon --input '{
  "projectId": "restless-glitter-71170845",
  "databaseName": "neondb",
  "sql": "SELECT COUNT(*) FROM matches"
}'
```

### Limpar Dados Antigos

```sql
-- Remover jogos muito antigos (opcional)
DELETE FROM matches WHERE date < '2015-01-01';
```

### Recalcular Estatísticas

```bash
python -c "from src.data_processing import DataProcessor; p = DataProcessor(); p.calculate_all_stats()"
```

---

## 📈 Roadmap

- [x] Banco de dados Neon PostgreSQL
- [x] Schema completo
- [x] Importação de dados históricos
- [x] Sistema de atualização incremental
- [x] Modelo de previsão de placares
- [ ] Modelo de classificação de grupos
- [ ] Modelo de simulação de pódio
- [ ] Dashboard Streamlit completo
- [ ] API REST para previsões
- [ ] Deploy automático via GitHub Actions

---

## 🆘 Troubleshooting

### Erro: "API key inválida"
```bash
# Verificar .env
cat .env | grep API_FOOTBALL_KEY

# Testar API
python test_api.py
```

### Erro: "Conexão com Neon falhou"
```bash
# Verificar projeto
manus-mcp-cli tool call list_projects --server neon --input '{}'
```

### Importação muito lenta
```bash
# Usar batch inserts (em desenvolvimento)
# Ou aguardar - importação única demora ~10-15 min
```

---

## 📚 Documentação Adicional

- [Como Funciona o Modelo](COMO_FUNCIONA_O_MODELO.md)
- [Palpites Necessários](PALPITES_NECESSARIOS.md)
- [Sistema Adaptativo](SISTEMA_ADAPTATIVO.md)
- [Guia Rápido](GUIA_RAPIDO.md)

---

## 🤝 Contribuindo

Este é um projeto pessoal para o Bolão Copa 2026, mas sugestões são bem-vindas!

---

## 📄 Licença

Uso pessoal - Bolão Copa 2026

---

## ✨ Créditos

- **Dados**: Kaggle (martj42/international_results)
- **API**: API-Football
- **Banco**: Neon PostgreSQL
- **Metodologia**: Distribuição de Poisson, Regressão à Média, Monte Carlo

---

**Desenvolvido para dominar o Bolão Copa 2026! 🏆⚽**
