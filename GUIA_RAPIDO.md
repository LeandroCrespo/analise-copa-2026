# 🚀 Guia Rápido de Uso

## Instalação e Configuração

### 1. Instalar Dependências

```bash
cd /home/ubuntu/analise-copa-2026
pip install -r requirements.txt
```

### 2. Configurar API Key

1. Acesse https://www.api-football.com/ e crie uma conta gratuita
2. Copie sua API key
3. Crie arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

4. Edite `.env` e adicione sua chave:

```
API_FOOTBALL_KEY=sua_chave_aqui
```

### 3. Coletar Dados Iniciais

```bash
cd src
python data_collection.py
```

Isso irá:
- Conectar à API-Football
- Coletar dados de todas as seleções da Copa 2026
- Baixar histórico de jogos (últimos 5 anos)
- Armazenar no banco de dados SQLite

**Tempo estimado:** 5-10 minutos (depende da API)

## Uso Diário

### Executar Dashboard

```bash
cd /home/ubuntu/analise-copa-2026
streamlit run app/dashboard.py
```

O dashboard abrirá automaticamente no navegador em `http://localhost:8501`

### Atualizar Resultados

#### Opção 1: Atualização Manual (Recomendado)

No dashboard, vá em **🔄 Atualizar Dados** e clique em:
- **"Atualizar Resultados de Hoje"** - Atualiza jogos do dia
- **"Verificar Jogos ao Vivo"** - Mostra jogos em andamento

#### Opção 2: Via Terminal

```bash
cd src
python live_updater.py
```

#### Opção 3: Monitoramento Contínuo

```bash
cd src
python live_updater.py monitor
```

Isso iniciará um loop que verifica resultados a cada 5 minutos.

## Fluxo de Trabalho Recomendado

### Antes da Copa (Preparação)

1. ✅ Coletar dados históricos
2. ✅ Testar previsões com confrontos hipotéticos
3. ✅ Analisar força de cada seleção
4. ✅ Gerar previsões iniciais de grupos e pódio

### Durante a Copa (Dia a Dia)

#### Manhã
1. Abrir dashboard
2. Atualizar resultados dos jogos de ontem
3. Verificar próximos jogos do dia

#### Antes de Cada Jogo
1. Gerar previsão do confronto
2. Registrar palpite no Bolão
3. Salvar previsão para comparação futura

#### Após Cada Rodada
1. Atualizar todos os resultados
2. Verificar classificação dos grupos (se fase de grupos)
3. Recalcular previsões de jogos futuros
4. Atualizar palpites se necessário

## Funcionalidades por Menu

### 🏠 Home
- **Visão geral** do sistema
- **Status** (seleções, jogos, resultados)
- **Próximos jogos** (7 dias)

### 📊 Análise de Seleções
- Selecionar qualquer seleção
- Ver **estatísticas completas**
- Comparar **histórico geral vs. forma recente**
- Consultar **histórico de jogos**

### 🎯 Previsão de Jogos
- Selecionar confronto
- Gerar **placar previsto**
- Ver **probabilidades** (vitória/empate/derrota)
- Consultar **intervalo de confiança**
- Verificar se é **previsão adaptativa**

### 🏆 Classificação dos Grupos
- Simular fase de grupos
- Ver **classificação prevista** (1º, 2º, 3º, 4º)
- Considerar **jogos já realizados**

### 🥇 Previsão de Pódio
- Simular torneio completo
- Ver **top 3 favoritos**
- Consultar **probabilidades de pódio**

### 🔄 Atualizar Dados
- Atualizar resultados manualmente
- Verificar jogos ao vivo
- Sincronizar todos os jogos

### 📈 Estatísticas
- **Ranking de força** das seleções
- **Comparações** entre seleções
- **Gráficos** e visualizações

## Dicas de Uso

### 1. Atualização Frequente
- Atualize resultados **após cada rodada de jogos**
- Quanto mais atualizado, mais precisas as previsões

### 2. Previsões Adaptativas
- Preste atenção no indicador **"✅ Previsão Adaptativa"**
- Indica que o sistema está usando dados da Copa 2026

### 3. Intervalo de Confiança
- Placares com **intervalo pequeno** = maior confiança
- Placares com **intervalo grande** = maior incerteza

### 4. Probabilidades
- Use para avaliar **risco vs. recompensa**
- Palpites com 70%+ de probabilidade são mais seguros

### 5. Forma Recente
- Dê mais peso para **forma recente** que histórico geral
- Seleções podem ter mudado muito nos últimos meses

## Troubleshooting

### Erro: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Erro: "API key inválida"
- Verifique se copiou a chave corretamente no `.env`
- Confirme que a chave está ativa em https://www.api-football.com/

### Erro: "Nenhuma seleção cadastrada"
```bash
cd src
python data_collection.py
```

### Dashboard não abre
```bash
streamlit run app/dashboard.py --server.port 8502
```

### Banco de dados corrompido
```bash
rm data/database.db
cd src
python data_collection.py
```

## Comandos Úteis

### Ver estrutura do banco de dados
```bash
sqlite3 data/database.db ".schema"
```

### Ver seleções cadastradas
```bash
sqlite3 data/database.db "SELECT * FROM teams LIMIT 10;"
```

### Ver jogos recentes
```bash
sqlite3 data/database.db "SELECT * FROM matches ORDER BY date DESC LIMIT 10;"
```

### Limpar cache do Streamlit
```bash
streamlit cache clear
```

## Atalhos do Dashboard

- **R** - Recarregar página
- **Ctrl + K** - Abrir menu de comandos
- **Ctrl + /** - Mostrar atalhos

## Próximos Passos

1. ✅ Familiarize-se com o dashboard
2. ✅ Teste previsões com confrontos conhecidos
3. ✅ Configure atualização automática
4. ✅ Comece a registrar palpites no Bolão
5. ✅ Acompanhe evolução das previsões

## Suporte

Para dúvidas ou problemas:
1. Consulte o README.md completo
2. Verifique o SISTEMA_ADAPTATIVO.md para detalhes técnicos
3. Revise os logs de erro no terminal

---

**Boa sorte no Bolão! 🏆⚽**
