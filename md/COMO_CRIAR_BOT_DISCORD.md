# Como Criar e Configurar o Bot Discord

## Passo 1: Criar o Bot no Discord Developer Portal

1. Acesse: https://discord.com/developers/applications
2. Clique em **New Application**
3. Dê um nome ao bot (ex: "Bot Eventos")
4. Vá na aba **Bot** (menu lateral esquerdo)
5. Clique em **Add Bot** → **Yes, do it!**
6. Em **Privileged Gateway Intents**, ative:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT (opcional)
7. Clique em **Reset Token** e copie o token (guarde bem!)

## Passo 2: Adicionar o Bot ao Servidor

1. Ainda no Developer Portal, vá na aba **OAuth2** → **URL Generator**
2. Em **SCOPES**, marque:
   - ✅ bot
3. Em **BOT PERMISSIONS**, marque:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Attach Files
   - ✅ Read Message History
   - ✅ Use Slash Commands
4. Copie a URL gerada no final da página
5. Cole no navegador e adicione o bot ao seu servidor

## Passo 3: Configurar o Código

1. Abra o arquivo `bot_discord.py`
2. Cole o token do bot:
   ```python
   BOT_TOKEN = "seu_token_aqui"
   ```

## Passo 4: Executar o Bot

```bash
.\venv\Scripts\activate
python bot_discord.py
```

Quando aparecer "✅ Bot conectado", ele está online!

## Como Usar

No Discord, digite os comandos:

- `!buscar` - Inicia a busca de eventos em todas as cidades
- `!eventos` - Mesmo que !buscar
- `!ajuda` - Mostra os comandos disponíveis

## Exemplo de Uso

```
Você: !buscar
Bot: 🚀 Iniciando automação...
Bot: 🔍 Iniciando busca de eventos...
Bot: 📍 Pesquisando em: Brusque
Bot: [Embed com evento 1]
Bot: [Embed com evento 2]
...
Bot: ✅ Busca concluída! Total de eventos encontrados: 15
```

## Dicas

- O bot roda em modo headless (Chrome não abre janela)
- Mantenha o terminal aberto enquanto quiser que o bot fique online
- Para parar o bot, pressione Ctrl+C no terminal
- O bot só responde em canais onde tem permissão

## Manter o Bot Online 24/7

Para deixar o bot rodando sempre, você pode:
- Usar um VPS (servidor na nuvem)
- Usar serviços como Railway, Heroku, ou Replit
- Deixar rodando em um computador que fica sempre ligado
