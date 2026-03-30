# Como Hospedar o Bot no Render.com (GRÁTIS)

## ⚠️ Importante sobre o Plano Gratuito

- O bot **dorme após 15 minutos de inatividade**
- Quando você usar o comando `!buscar`, ele **acorda automaticamente** (demora 30-60 segundos)
- Você tem **750 horas grátis por mês** (suficiente para o mês todo)
- Não precisa cartão de crédito

## Passo 1: Preparar o Código

### 1.1 Criar conta no GitHub (se não tiver)
1. Acesse: https://github.com/signup
2. Crie sua conta gratuita

### 1.2 Criar um repositório
1. Acesse: https://github.com/new
2. Nome do repositório: `bot-eventos-sc`
3. Deixe como **Público**
4. Clique em **Create repository**

### 1.3 Subir o código para o GitHub

**⚠️ IMPORTANTE: Não suba o token!**

Abra o terminal na pasta do projeto e execute:

```bash
# Verificar se .env está no .gitignore
cat .gitignore | grep .env

# Se aparecer ".env", está seguro! Agora suba o código:
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/bot-eventos-sc.git
git push -u origin main
```

**Substitua `SEU_USUARIO` pelo seu nome de usuário do GitHub!**

**✅ O arquivo `.env` NÃO será enviado ao GitHub (está no .gitignore)**

## Passo 2: Configurar o Render.com

### 2.1 Criar conta no Render
1. Acesse: https://render.com/
2. Clique em **Get Started**
3. Faça login com sua conta do GitHub

### 2.2 Criar um novo Web Service
1. No dashboard do Render, clique em **New +**
2. Selecione **Web Service**
3. Conecte seu repositório do GitHub `bot-eventos-sc`
4. Clique em **Connect**

### 2.3 Configurar o serviço

Preencha os campos:

- **Name**: `bot-eventos-sc` (ou qualquer nome)
- **Region**: Escolha a mais próxima (ex: Oregon)
- **Branch**: `main`
- **Runtime**: `Docker`
- **Instance Type**: **Free** ⬅️ IMPORTANTE!

### 2.4 Variáveis de ambiente (IMPORTANTE!)

⚠️ **NUNCA coloque o token no código! Use variáveis de ambiente.**

Role para baixo até **Environment Variables** e adicione:

- **Key**: `BOT_TOKEN`
- **Value**: Cole aqui o token do seu bot Discord

Clique em **Add**

**Onde pegar o token?**
1. Acesse: https://discord.com/developers/applications/
2. Selecione seu bot
3. Vá em "Bot"
4. Clique em "Reset Token" e copie

### 2.5 Deploy

1. Role até o final e clique em **Create Web Service**
2. Aguarde o deploy (pode demorar 5-10 minutos na primeira vez)
3. Quando aparecer "Live", seu bot está online! ✅

## Passo 3: Usar o Bot

No Discord, digite:
- `!buscar` - Busca eventos
- `!eventos` - Mesma coisa
- `!ajuda` - Mostra comandos

**Primeira vez após 15min parado**: O bot vai demorar 30-60 segundos para acordar e responder.

## Verificar Logs

1. No Render, clique no seu serviço
2. Vá na aba **Logs**
3. Você verá: `✅ Bot conectado como EventosSC#3283`

## Problemas Comuns

### Bot não conecta
- Verifique se o `BOT_TOKEN` está correto nas variáveis de ambiente
- Verifique os logs no Render

### Bot demora para responder
- Normal no plano gratuito após 15min parado
- Ele acorda automaticamente, só aguardar

### Deploy falhou
- Verifique se todos os arquivos estão no GitHub:
  - `bot_discord.py`
  - `requirements.txt`
  - `Dockerfile`
  - `.dockerignore`

## Atualizar o Bot

Quando fizer mudanças no código:

```bash
git add .
git commit -m "Atualização"
git push
```

O Render vai fazer o deploy automaticamente!

## Alternativas se Render não funcionar

1. **Fly.io** - Não dorme, 100% grátis
2. **Railway** - $5 de crédito grátis/mês
3. **Oracle Cloud** - VM grátis para sempre (mais complexo)

## Custos

- **Render Free Tier**: $0/mês
- **Limitações**: 
  - Dorme após 15min
  - 750 horas/mês
  - 512MB RAM

Se precisar que o bot fique online 24/7 sem dormir, considere Fly.io ou Oracle Cloud.
