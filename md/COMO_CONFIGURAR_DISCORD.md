# Como Configurar o Webhook do Discord

## Passo a Passo

### 1. Criar um Webhook no Discord

1. Abra o Discord e vá para o servidor onde quer receber as mensagens
2. Clique com botão direito no canal desejado
3. Selecione **Editar Canal**
4. Vá na aba **Integrações**
5. Clique em **Webhooks** → **Novo Webhook**
6. Dê um nome ao webhook (ex: "Bot Eventos")
7. Clique em **Copiar URL do Webhook**

### 2. Configurar no Script

1. Abra o arquivo `exemplo_selenium.py`
2. Encontre a linha:
   ```python
   DISCORD_WEBHOOK_URL = "COLE_SEU_WEBHOOK_AQUI"
   ```
3. Cole a URL do webhook entre as aspas:
   ```python
   DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/123456789/abcdefg..."
   ```

### 3. Executar

```bash
.\venv\Scripts\activate
python exemplo_selenium.py
```

## O que o bot faz

Para cada evento encontrado, o bot envia uma mensagem no Discord com:
- 🎭 Nome do evento
- 📅 Data do evento
- 📍 Cidade
- 🖼️ Imagem do evento

## Exemplo de Mensagem

```
🎭 Funk on the Beach
📅 Data: 15/04/2026
📍 Local: Balneário Camboriú
[Imagem do evento]
```

## Dicas

- Você pode criar webhooks em diferentes canais para organizar por cidade
- O Discord permite até 30 mensagens por minuto por webhook
- As mensagens aparecem com embeds formatados (visual bonito)
