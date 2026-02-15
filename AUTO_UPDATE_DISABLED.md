# ⚠️ Scripts de Atualização Automática DESATIVADOS

**Data:** 12 de Fevereiro de 2026  
**Status:** DESATIVADO por solicitação do usuário

## Scripts Desativados

Os seguintes scripts de atualização automática foram **desativados** e renomeados para `.disabled`:

1. **auto_update.py.disabled**
   - Atualização automática do banco Neon
   - Baixa CSV do GitHub e insere jogos novos
   - **NÃO EXECUTAR** sem autorização

2. **update_incremental.py.disabled**
   - Atualização incremental de dados
   - **NÃO EXECUTAR** sem autorização

3. **src/live_updater.py**
   - Módulo de atualização em tempo real
   - Apenas código, não está em execução

## Como Reativar

Para reativar os scripts de atualização automática:

1. Renomear os arquivos removendo `.disabled`:
   ```bash
   mv auto_update.py.disabled auto_update.py
   mv update_incremental.py.disabled update_incremental.py
   ```

2. Executar manualmente quando necessário:
   ```bash
   cd /home/ubuntu/analise-copa-2026
   python3 auto_update.py
   ```

3. OU configurar cron job (atualização diária às 03:00):
   ```bash
   crontab -e
   # Adicionar linha:
   0 3 * * * cd /home/ubuntu/analise-copa-2026 && python3 auto_update.py
   ```

## Motivo da Desativação

Usuário solicitou desativação dos scripts de atualização automática para manter controle manual sobre quando os dados são atualizados.

## Última Execução

- **Data:** 12/02/2026
- **Jogos inseridos:** Verificar `auto_update.log`
- **Status:** Sucesso

---

**IMPORTANTE:** NÃO reativar sem autorização explícita do usuário!
