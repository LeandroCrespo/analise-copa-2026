# Análise Completa dos Palpites Necessários - Bolão Copa 2026

## Resumo Executivo

O sistema de análise precisa gerar **3 tipos de palpites** para o Bolão Copa 2026:

## 1. Palpites de Jogos (128 jogos)

### Descrição
Prever o **placar exato** de cada jogo da Copa 2026.

### Quantidade
- **128 jogos** no total
- Distribuídos em:
  - **Fase de Grupos**: 12 grupos × 6 jogos = 72 jogos
  - **Oitavas de Final (32 times)**: 16 jogos
  - **Oitavas de Final (16 times)**: 8 jogos
  - **Quartas de Final**: 4 jogos
  - **Semifinais**: 2 jogos
  - **Disputa 3º Lugar**: 1 jogo
  - **Final**: 1 jogo

### Formato do Palpite
- **Placar exato**: Ex: Brasil 2 x 1 Argentina

### Sistema de Pontuação
| Acerto | Pontos |
|--------|--------|
| Placar exato | 20 pts |
| Resultado + gols de um time | 15 pts |
| Apenas resultado (vencedor/empate) | 10 pts |
| Apenas gols de um time | 5 pts |
| Errou tudo | 0 pts |

### Prazo
- Podem ser alterados até o horário de início de cada partida

### O que o Sistema Precisa Prever
✅ **Placar exato de cada jogo** (ex: 2x1, 1x0, 3x2)
✅ **Probabilidade de cada resultado** (vitória mandante, empate, vitória visitante)
✅ **Intervalo de confiança** da previsão

---

## 2. Palpites de Classificação dos Grupos (12 grupos)

### Descrição
Prever quais serão o **1º e 2º colocados** de cada grupo.

### Quantidade
- **12 grupos** (A até L)
- **4 seleções** por grupo
- Total: **48 seleções**

### Formato do Palpite
- **1º lugar do Grupo A**: Brasil
- **2º lugar do Grupo A**: Argentina

### Sistema de Pontuação
| Acerto | Pontos |
|--------|--------|
| Acertou 1º e 2º na ordem correta | 20 pts |
| Acertou os 2 classificados (ordem invertida) | 10 pts |
| Acertou 1 classificado (posição errada) | 5 pts |

### Prazo
- Podem ser feitos/alterados a qualquer momento antes do fim da fase de grupos

### O que o Sistema Precisa Prever
✅ **Ranking completo de cada grupo** (1º, 2º, 3º, 4º)
✅ **Probabilidade de classificação** de cada seleção
✅ **Análise de força relativa** dentro do grupo

---

## 3. Palpites de Pódio (Campeão, Vice, 3º Lugar)

### Descrição
Prever o **pódio final** da Copa 2026.

### Quantidade
- **1 palpite** com 3 posições:
  - Campeão
  - Vice-Campeão
  - 3º Lugar

### Formato do Palpite
- **Campeão**: Brasil
- **Vice-Campeão**: Argentina
- **3º Lugar**: França

### Sistema de Pontuação
| Acerto | Pontos |
|--------|--------|
| Pódio completo na ordem exata | 150 pts |
| Acertar o Campeão | 100 pts |
| Acertar o Vice-Campeão | 50 pts |
| Acertar o 3º Lugar | 30 pts |
| Pódio fora de ordem | 20 pts |

### Prazo
- Podem ser alterados até a **data de início da Copa** (11/06/2026 13:00)

### O que o Sistema Precisa Prever
✅ **Top 3 seleções mais fortes** do torneio
✅ **Probabilidade de cada seleção chegar ao pódio**
✅ **Análise de caminho até a final** (chaveamento)

---

## Resumo das Funcionalidades Necessárias no Sistema

### 1. Previsão de Placares (128 jogos)
- Modelo de regressão para prever gols de cada time
- Análise de confronto direto
- Forma recente (últimos 10 jogos)
- Força relativa das seleções
- Histórico de gols marcados/sofridos

### 2. Previsão de Classificação dos Grupos (12 grupos)
- Simulação de todos os jogos do grupo
- Cálculo de pontos esperados por seleção
- Ranking probabilístico de classificação
- Análise de cenários (melhor/pior caso)

### 3. Previsão de Pódio (Top 3)
- Simulação completa do torneio (Monte Carlo)
- Análise de chaveamento (caminho até a final)
- Força global das seleções
- Probabilidade de chegar a cada fase
- Ranking de favoritos ao título

---

## Priorização para Implementação

### Fase 1: Previsão de Placares ✅
**Mais importante** - Base para todas as outras previsões

### Fase 2: Previsão de Classificação dos Grupos
Depende da Fase 1 (simular jogos da fase de grupos)

### Fase 3: Previsão de Pódio
Depende das Fases 1 e 2 (simular todo o torneio)

---

## Dados Necessários para Cada Tipo de Palpite

### Para Placares
- Histórico de jogos de cada seleção
- Gols marcados/sofridos
- Confrontos diretos
- Forma recente
- Rankings FIFA/ELO

### Para Grupos
- Previsões de placares dos jogos do grupo
- Força relativa das seleções
- Critérios de desempate da FIFA

### Para Pódio
- Previsões de todos os jogos
- Chaveamento do mata-mata
- Força global das seleções
- Probabilidade de avançar em cada fase
