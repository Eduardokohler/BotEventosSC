# 🎭 Bot Eventos SC

Automação inteligente para agregação e distribuição de eventos em Santa Catarina via Discord. O bot realiza web scraping em tempo real de plataformas de ingressos e envia notificações formatadas para canais Discord.

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.7.1-7289DA?logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![Selenium](https://img.shields.io/badge/Selenium-4.41.0-green?logo=selenium&logoColor=white)](https://www.selenium.dev/)

## 📋 Sobre

Bot Discord que automatiza a busca de eventos em cidades de Santa Catarina (Brusque, Blumenau, Balneário Camboriú, Camboriú, Itapema, Porto Belo e Itajaí) através de web scraping com Selenium e envia as informações formatadas em embeds para canais Discord.

**Funcionalidades:**
- 🔍 Web scraping automático de eventos
- 📤 Integração com Discord via bot e webhooks
- 🖼️ Embeds formatados com imagens dos eventos
- 📅 Extração de datas e informações dos eventos
- 🐳 Suporte a containerização com Docker
- ☁️ Deploy pronto para Render

## 🚀 Quick Start

### Pré-requisitos

- Python 3.8+
- Git
- Conta Discord com permissões para criar bots
- Token do bot Discord
- Webhook URL do Discord (opcional)

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/Eduardokohler/BotEventosSC.git
cd BotEventosSC
```

2. Crie um ambiente virtual:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env com suas credenciais
# BOT_TOKEN=seu_token_aqui
# CANAL_ID=seu_canal_id_aqui
# DISCORD_WEBHOOK_URL=sua_webhook_url_aqui
```

5. Execute o bot:
```bash
python bot_discord.py
```

## 📖 Uso

### Comandos do Bot

| Comando | Descrição |
|---------|-----------|
| `!buscar` | Inicia a busca de eventos em todas as cidades |
| `!eventos` | Alias para `!buscar` |
| `!ajuda` | Exibe a lista de comandos disponíveis |

### Exemplo de Uso

```
User: !buscar
Bot: 🚀 Iniciando automação...
Bot: 🔍 Iniciando busca de eventos...
Bot: 📍 Pesquisando em: Blumenau
Bot: [Embed com evento encontrado]
Bot: ✅ Busca concluída! Total de eventos encontrados: 15
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```env
# Token do bot Discord
BOT_TOKEN=seu_token_discord_aqui

# ID do canal onde o bot vai responder
CANAL_ID=seu_canal_id_aqui

# URL do webhook Discord (para exemplo_selenium.py)
DISCORD_WEBHOOK_URL=sua_webhook_url_aqui
```

### Criar um Bot Discord

1. Acesse [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique em "New Application"
3. Vá para "Bot" e clique em "Add Bot"
4. Copie o token em "TOKEN"
5. Em "OAuth2" → "URL Generator", selecione:
   - Scopes: `bot`
   - Permissions: `Send Messages`, `Embed Links`, `Read Message History`
6. Use a URL gerada para adicionar o bot ao seu servidor

Veja [COMO_CRIAR_BOT_DISCORD.md](md/COMO_CRIAR_BOT_DISCORD.md) para instruções detalhadas.

## 🐳 Docker

### Build da imagem

```bash
docker build -t bot-eventos-sc .
```

### Executar container

```bash
docker run -d \
  --name bot-eventos \
  -e BOT_TOKEN=seu_token_aqui \
  -e CANAL_ID=seu_canal_id_aqui \
  -e DISCORD_WEBHOOK_URL=sua_webhook_url_aqui \
  bot-eventos-sc
```

## ☁️ Deploy

### Render

O projeto está configurado para deploy automático no Render. Veja [DEPLOY_RENDER.md](md/DEPLOY_RENDER.md) para instruções completas.

**Passos rápidos:**
1. Faça push do código para o GitHub
2. Conecte seu repositório no Render
3. Configure as variáveis de ambiente
4. Deploy automático será iniciado

## 📁 Estrutura do Projeto

```
BotEventosSC/
├── bot_discord.py              # Bot principal com comandos Discord
├── requirements.txt            # Dependências Python
├── Dockerfile                  # Configuração Docker
├── .env.example               # Template de variáveis de ambiente
├── .gitignore                 # Arquivos ignorados pelo Git
├── README.md                  # Este arquivo
└── md/
    ├── COMO_CRIAR_BOT_DISCORD.md
    ├── COMO_CONFIGURAR_DISCORD.md
    └── DEPLOY_RENDER.md
```

## 📦 Dependências

- **discord.py** (2.7.1) - Biblioteca para interagir com Discord API
- **selenium** (4.41.0) - Framework de automação web
- **webdriver-manager** (4.0.2) - Gerenciamento automático de drivers
- **discord-webhook** (1.4.1) - Integração com webhooks Discord
- **python-dotenv** (1.0.0) - Carregamento de variáveis de ambiente

## 🔐 Segurança

- ✅ Credenciais armazenadas em `.env` (não commitadas)
- ✅ Tokens não expostos no código
- ✅ `.env` incluído no `.gitignore`
- ✅ Validação de configuração antes de executar

## 🐛 Troubleshooting

### Bot não conecta
- Verifique se o `BOT_TOKEN` está correto no `.env`
- Confirme que o bot tem permissões no servidor Discord
- Verifique a conexão com a internet

### Eventos não encontrados
- O site pode ter mudado sua estrutura HTML
- Verifique os XPaths em `bot_discord.py`
- Tente executar `exemplo_selenium.py` para debug

### Erro de WebDriver
- Execute `pip install --upgrade webdriver-manager`
- Limpe o cache: `rm -rf ~/.wdm/` (Linux/macOS) ou `rmdir %USERPROFILE%\.wdm` (Windows)

### Eventos não encontrados ao executar
- O site pode ter mudado sua estrutura HTML
- Verifique os XPaths no código
- Teste a conexão com o site manualmente

## 📝 Logs

Os logs são exibidos no console durante a execução. Para persistência, considere adicionar logging a arquivo:

```python
import logging
logging.basicConfig(filename='bot.log', level=logging.INFO)
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 👨‍💻 Autor

**Eduardo Kohler**
- GitHub: [@Eduardokohler](https://github.com/Eduardokohler)

## 📞 Suporte

Para dúvidas ou problemas, abra uma [Issue](https://github.com/Eduardokohler/BotEventosSC/issues) no repositório.

---

**Última atualização:** Março 2026

---
**Futuras Atualizações**

- Funcionalidade nova: Adicionar lista de cidades, sendo totalmente dinâmico e personalizável.
- Sites a ser integrados no sistema: Blueticket.com.br, Eventim.com.br, guicheweb.com.br, ingresso.com e ingresse.com
