# ⚽ Sistema de Análise e Previsão - Copa 2026

Sistema inteligente para análise de seleções e geração de palpites para o Bolão Copa do Mundo 2026.

## 🎯 Objetivo

Criar um sistema baseado em dados históricos e modelos estatísticos para gerar palpites otimizados para o Bolão Copa 2026, incluindo:

1. **Palpites de Placares** (128 jogos)
2. **Previsões de Classificação dos Grupos** (12 grupos)
3. **Previsão de Pódio** (Campeão, Vice, 3º Lugar)

## 🏗️ Arquitetura

O sistema é dividido em 4 camadas principais:

### 1. Camada de Coleta de Dados
- Integração com API-Football para dados de seleções
- Coleta automática de histórico de jogos
- Armazenamento em banco de dados SQLite
- Atualização em tempo real

### 2. Camada de Processamento
- Cálculo de métricas históricas (vitórias, empates, derrotas, gols)
- Análise de forma recente (últimos 10 jogos)
- Rankings FIFA/ELO
- Força relativa do adversário
- Preparação de features para modelos

### 3. Camada de Modelos
- **Modelo de Placares**: Previsão de gols usando distribuição de Poisson e regressão à média
- **Modelo de Grupos**: Simulação de fase de grupos com todos os confrontos
- **Modelo de Pódio**: Simulação de Monte Carlo do torneio completo

### 4. Camada de Apresentação
- Dashboard Streamlit interativo
- Visualizações de análises por seleção
- Previsões com intervalos de confiança
- Histórico de acertos/erros

## 📊 Metodologia

### Previsão de Placares

O modelo de previsão de placares utiliza:

1. **Regressão à Média**: Análise de tendências históricas de gols marcados/sofridos
2. **Forma Recente**: Ponderação maior para últimos 10 jogos (60%) vs. histórico geral (40%)
3. **Força Relativa**: Ajuste baseado na força calculada de cada seleção
4. **Distribuição de Poisson**: Modelagem probabilística de gols
5. **Simulação de Monte Carlo**: Cálculo de probabilidades de resultado

### Previsão de Grupos

O modelo de classificação dos grupos:

1. Simula todos os 6 jogos de cada grupo
2. Calcula pontos, saldo de gols e gols marcados
3. Aplica critérios de desempate da FIFA
4. Retorna classificação prevista (1º, 2º, 3º, 4º)

### Previsão de Pódio

O modelo de pódio:

1. Simula 1000+ torneios completos (Monte Carlo)
2. Considera chaveamento do mata-mata
3. Calcula probabilidade de cada seleção chegar ao pódio
4. Retorna top 3 mais prováveis

## 📁 Estrutura do Projeto

```
analise-copa-2026/
├── data/
│   ├── raw/                    # Dados brutos da API
│   ├── processed/              # Dados processados
│   └── database.db             # Banco de dados SQLite
├── src/
│   ├── config.py               # Configurações
│   ├── utils.py                # Funções auxiliares
│   ├── data_collection.py      # Coleta de dados via API
│   ├── data_processing.py      # Processamento e análise
│   └── model.py                # Modelos de previsão
├── app/
│   └── dashboard.py            # Dashboard Streamlit
├── notebooks/
│   └── exploratory.ipynb       # Análise exploratória
├── requirements.txt            # Dependências
├── .env                        # Variáveis de ambiente
└── README.md                   # Este arquivo
```

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar API Key

Crie um arquivo `.env` na raiz do projeto:

```
API_FOOTBALL_KEY=sua_chave_api_aqui
```

Para obter uma chave gratuita:
1. Acesse https://www.api-football.com/
2. Crie uma conta
3. Copie sua API key

### 3. Coletar Dados

```bash
python src/data_collection.py
```

Isso irá:
- Conectar à API-Football
- Coletar dados de todas as seleções
- Baixar histórico de jogos (últimos 5 anos)
- Armazenar no banco de dados

### 4. Executar Dashboard

```bash
streamlit run app/dashboard.py
```

## 📈 Funcionalidades do Dashboard

### Análise de Seleções
- Estatísticas gerais (vitórias, empates, derrotas)
- Forma recente (últimos 10 jogos)
- Média de gols marcados/sofridos
- Score de força (0-100)
- Ranking comparativo

### Previsões de Jogos
- Placar previsto
- Probabilidades de resultado (vitória/empate/derrota)
- Intervalo de confiança
- Análise de confronto direto

### Previsões de Grupos
- Classificação prevista de cada grupo
- Pontos esperados por seleção
- Probabilidade de classificação

### Previsões de Pódio
- Top 3 favoritos ao título
- Probabilidade de cada seleção chegar ao pódio
- Análise de caminho até a final

## 🔧 Configurações Avançadas

### Ajustar Janela de Forma Recente

Em `src/config.py`:

```python
RECENT_MATCHES_WINDOW = 10  # Número de jogos recentes
```

### Ajustar Ponderação Forma Recente vs. Histórico

Em `src/model.py` (método `predict_goals`):

```python
# Ponderação: 60% forma recente, 40% histórico geral
expected_goals_attack = 0.6 * avg_goals_recent + 0.4 * avg_goals_overall
```

### Ajustar Número de Simulações (Monte Carlo)

Em `src/model.py` (método `predict_podium`):

```python
n_simulations = 1000  # Aumentar para mais precisão
```

## 📊 Métricas e Validação

O sistema calcula as seguintes métricas:

- **Acurácia de Placares**: % de placares exatos acertados
- **Acurácia de Resultados**: % de resultados (vitória/empate/derrota) acertados
- **Erro Médio de Gols**: Diferença média entre gols previstos e reais
- **Calibração de Probabilidades**: Comparação entre probabilidades previstas e frequências reais

## 🎓 Conceitos Utilizados

### Regressão à Média
Fenômeno estatístico onde valores extremos tendem a retornar à média ao longo do tempo. O modelo ajusta previsões considerando que performances excepcionais (muito boas ou ruins) tendem a normalizar.

### Distribuição de Poisson
Distribuição de probabilidade que modela eventos raros e independentes. Ideal para modelar gols em futebol, pois:
- Gols são eventos relativamente raros
- Cada gol é independente do anterior
- Taxa média de gols é relativamente constante

### Simulação de Monte Carlo
Método computacional que usa amostragem aleatória repetida para obter resultados numéricos. Usado para:
- Calcular probabilidades de resultados complexos
- Simular torneios completos
- Estimar incertezas

### Intervalo de Confiança
Faixa de valores que provavelmente contém o valor real com um nível de confiança especificado (95% no sistema). Indica a incerteza da previsão.

## 🔄 Atualização de Dados

Para manter os dados atualizados:

```bash
# Atualização manual
python src/data_collection.py

# Ou configurar atualização automática (cron/scheduler)
```

## ⚠️ Limitações

- **Dependência de dados históricos**: Seleções com poucos jogos recentes terão previsões menos precisas
- **Fatores não considerados**: Lesões, suspensões, motivação, condições climáticas
- **Aleatoriedade do futebol**: Mesmo com boas previsões, resultados inesperados acontecem
- **Limite de API**: Plano gratuito tem limite de requisições por dia

## 🎯 Próximas Melhorias

- [ ] Integração com rankings ELO em tempo real
- [ ] Análise de jogadores-chave (artilheiros, assistências)
- [ ] Consideração de lesões/suspensões
- [ ] Análise de desempenho por tipo de competição
- [ ] Machine Learning avançado (XGBoost, Neural Networks)
- [ ] Backtesting com Copas anteriores
- [ ] API REST para integração com outros sistemas

## 📞 Suporte

Para dúvidas ou sugestões, entre em contato.

---

**Bons palpites e boa sorte no Bolão! 🏆⚽**
