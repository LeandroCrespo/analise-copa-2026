# 🚀 Deploy no Streamlit Cloud - Guia Completo

## ✅ Arquivos Preparados

Todos os arquivos necessários foram criados e estão prontos para deploy!

---

## 📋 Pré-requisitos

1. ✅ Conta no GitHub (já tem)
2. ✅ Repositório criado: `LeandroCrespo/analise-copa-2026`
3. ✅ Conta no Streamlit Cloud (criar se não tiver)
4. ✅ Connection string do Neon PostgreSQL

---

## 🔑 Passo 1: Obter Connection String do Neon

### 1.1 Acessar Console do Neon

1. Acesse: https://console.neon.tech/
2. Faça login
3. Selecione o projeto: `analise-copa-2026`

### 1.2 Copiar Connection String

1. No painel do projeto, clique em **"Connection Details"**
2. Copie a **"Connection string"**
3. Deve ser algo como:
   ```
   postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

**IMPORTANTE:** Guarde essa string, você vai precisar!

---

## 🚀 Passo 2: Deploy no Streamlit Cloud

### 2.1 Acessar Streamlit Cloud

1. Acesse: https://share.streamlit.io/
2. Faça login com sua conta GitHub
3. Clique em **"New app"**

### 2.2 Configurar App

**Repository:** `LeandroCrespo/analise-copa-2026`
**Branch:** `master`
**Main file path:** `streamlit_app.py`

### 2.3 Configurar Secrets

Antes de fazer deploy, clique em **"Advanced settings"** → **"Secrets"**

Cole o seguinte (substitua com sua connection string):

```toml
[neon]
project_id = "restless-glitter-71170845"
database_name = "neondb"
connection_string = "postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require"
```

**IMPORTANTE:** Substitua `connection_string` pela string que você copiou do Neon!

### 2.4 Deploy

1. Clique em **"Deploy!"**
2. Aguarde 2-3 minutos
3. Seu app estará no ar! 🎉

---

## 🌐 Passo 3: Acessar Seu App

Após o deploy, você receberá uma URL como:

```
https://leandrocrespo-analise-copa-2026-streamlit-app-xxxxx.streamlit.app
```

**Salve essa URL!** É o link público do seu dashboard.

---

## 🔧 Configuração Adicional (Opcional)

### Custom Domain

Se quiser um domínio personalizado:

1. No Streamlit Cloud, vá em **Settings**
2. Clique em **"Custom domain"**
3. Siga as instruções

### Senha de Acesso

Para proteger com senha:

1. Adicione em `secrets.toml`:
   ```toml
   [passwords]
   admin = "sua_senha_aqui"
   ```

2. Adicione verificação no `streamlit_app.py`

---

## 📊 Arquivos Criados

### Configuração do Streamlit

1. **`streamlit_app.py`** ⭐
   - Dashboard principal
   - Otimizado para Streamlit Cloud
   - Usa secrets para conexão

2. **`requirements_streamlit.txt`**
   - Dependências necessárias
   - Versões específicas

3. **`.streamlit/config.toml`**
   - Configuração de tema
   - Configuração de servidor

4. **`.streamlit/secrets.toml.example`**
   - Exemplo de secrets
   - Não fazer commit deste arquivo!

---

## 🎯 Funcionalidades do Dashboard

### 🏠 Home
- Métricas principais
- Estratégia de placares
- Status da atualização

### 🎯 Previsões
- Selecionar times
- Gerar previsão de placar
- Ver probabilidades
- Detalhes da análise

### 📊 Estatísticas
- Ver estatísticas de cada seleção
- Gols por jogo
- Taxa de vitória
- Força do time

### ℹ️ Sobre
- Informações do sistema
- Metodologia
- Links úteis

---

## 🔄 Atualização do App

### Automática

Sempre que você fizer push no GitHub, o Streamlit Cloud atualiza automaticamente!

```bash
cd /home/ubuntu/analise-copa-2026
git add .
git commit -m "Atualização do dashboard"
git push
```

Aguarde 1-2 minutos e o app será atualizado.

### Manual

No Streamlit Cloud:
1. Acesse seu app
2. Clique em **"Manage app"**
3. Clique em **"Reboot app"**

---

## 🚨 Troubleshooting

### Erro: "Connection refused"

**Problema:** Connection string do Neon incorreta

**Solução:**
1. Verifique a connection string no Neon Console
2. Atualize em **Settings** → **Secrets** no Streamlit Cloud
3. Reboot o app

### Erro: "Module not found"

**Problema:** Falta dependência

**Solução:**
1. Adicione em `requirements_streamlit.txt`
2. Commit e push
3. Aguarde rebuild automático

### App muito lento

**Problema:** Muitas consultas ao banco

**Solução:**
- O cache já está configurado (`@st.cache_data`)
- Considere aumentar TTL do cache

### Erro: "No module named 'model_optimized'"

**Problema:** Arquivo não está no repositório

**Solução:**
```bash
cd /home/ubuntu/analise-copa-2026
git add model_optimized.py
git commit -m "Add model_optimized"
git push
```

---

## 📱 Uso no Celular

O dashboard é **responsivo**! Funciona perfeitamente em:
- 📱 Celular
- 💻 Tablet
- 🖥️ Desktop

---

## 🔒 Segurança

### Secrets

✅ **NUNCA** faça commit de `secrets.toml`!

O arquivo `.gitignore` já está configurado para ignorar:
- `secrets.toml`
- `.env`
- Arquivos sensíveis

### Connection String

✅ Sempre use **Secrets** do Streamlit Cloud
❌ Nunca coloque no código

---

## 📈 Monitoramento

### Logs

No Streamlit Cloud:
1. Acesse seu app
2. Clique em **"Manage app"**
3. Veja **"Logs"**

### Métricas

- Visualizações
- Tempo de resposta
- Erros

---

## 💰 Custos

### Streamlit Cloud

**Plano Gratuito:**
- ✅ 1 app privado
- ✅ 3 apps públicos
- ✅ Recursos limitados
- ✅ Suficiente para este projeto!

**Plano Pago:**
- Mais recursos
- Mais apps
- Prioridade no suporte

### Neon PostgreSQL

**Plano Atual:**
- Você tem dados suficientes
- Sem custos adicionais esperados

---

## ✅ Checklist Final

Antes de fazer deploy, verifique:

- [ ] Connection string do Neon copiada
- [ ] Conta no Streamlit Cloud criada
- [ ] Repositório GitHub atualizado
- [ ] `model_optimized.py` no repositório
- [ ] `requirements_streamlit.txt` correto
- [ ] Secrets configurados no Streamlit Cloud

---

## 🎉 Pronto!

Após seguir estes passos, você terá:

✅ Dashboard público acessível de qualquer lugar
✅ Atualização automática via GitHub
✅ Conexão segura com Neon PostgreSQL
✅ Interface responsiva (celular/desktop)

---

## 🔗 Links Úteis

- **Streamlit Cloud:** https://share.streamlit.io/
- **Neon Console:** https://console.neon.tech/
- **Seu Repositório:** https://github.com/LeandroCrespo/analise-copa-2026
- **Documentação Streamlit:** https://docs.streamlit.io/

---

**Qualquer dúvida, consulte a documentação ou os logs do Streamlit Cloud! 🚀**
