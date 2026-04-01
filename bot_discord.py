import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import asyncio
import os

# CONFIGURAÇÕES - Usar variável de ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
CANAL_ID = int(os.getenv("CANAL_ID", "0"))  # ID do canal onde o bot vai responder

# Lista de cidades
cidades = ["Brusque", "Blumenau", "Balneário Camboriú", "Camboriú", "Itapema", "Porto Belo", "Itajaí"]

# Configurar bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def parse_cidades(args: str) -> list[str]:
    """Parseia cidades informadas pelo usuário, separadas por ';'"""
    if not args or not args.strip():
        return []
    return [c.strip() for c in args.split(";") if c.strip()]

async def buscar_eventos(canal, cidades_busca: list[str] = None):
    """Função que executa a automação do Selenium"""
    lista = cidades_busca if cidades_busca else cidades

    await canal.send("🔍 Iniciando busca de eventos...")
    
    # Configurar Chrome para ambiente Docker/Cloud
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Modo headless para servidor
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Acessar o site (URL CORRETA)
        driver.get("https://www.ingressonacional.com.br/balada")
        await asyncio.sleep(3)
        
        total_eventos = 0
        
        for cidade in lista:
            await canal.send(f"📍 Pesquisando em: **{cidade}**")
            
            # Encontrar a barra de pesquisa usando o XPATH fornecido
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/div/div[2]/div/form/div/div/input"))
            )
            
            # Limpar o campo antes de digitar
            search_box.clear()
            
            # Digitar o nome da cidade
            search_box.send_keys(cidade)
            
            # Aguardar um pouco para ver a pesquisa
            await asyncio.sleep(2)
            
            # Pressionar Enter para pesquisar
            search_box.send_keys(Keys.RETURN)
            
            # Aguardar os resultados carregarem
            await asyncio.sleep(3)
            
            # Buscar a lista de eventos
            try:
                lista_eventos = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/div[3]/div[1]")
                
                # Encontrar todos os eventos dentro da lista
                eventos = lista_eventos.find_elements(By.XPATH, ".//div[contains(@class, 'event') or contains(@class, 'item')]")
                
                if not eventos:
                    # Tentar buscar de forma mais genérica
                    eventos = lista_eventos.find_elements(By.XPATH, "./div")
                
                if not eventos or len(eventos) == 0:
                    await canal.send(f"⚠️ Nenhum evento encontrado em {cidade}")
                    continue
                
                # Percorrer cada evento
                for i in range(1, len(eventos) + 1):
                    try:
                        # XPath para data do evento
                        data_xpath = f"/html/body/div[1]/div[3]/div/div[3]/div[1]/div[{i}]/div[1]/div/div[1]/span"
                        # XPath para nome do evento
                        nome_xpath = f"/html/body/div[1]/div[3]/div/div[3]/div[1]/div[{i}]/div[2]/div[1]/h2"
                        # XPath para imagem do evento
                        imagem_xpath = f"/html/body/div[1]/div[3]/div/div[3]/div[1]/div[{i}]/a/div/img"
                        
                        data = driver.find_element(By.XPATH, data_xpath).text
                        nome = driver.find_element(By.XPATH, nome_xpath).text
                        imagem_element = driver.find_element(By.XPATH, imagem_xpath)
                        
                        # Pegar o atributo src da imagem
                        link_imagem = imagem_element.get_attribute("src")
                        
                        # Criar embed
                        embed = discord.Embed(
                            title=f"🎭 {nome}",
                            description=f"**📅 Data:** {data}\n**📍 Local:** {cidade}",
                            color=0x5865F2
                        )
                        embed.set_image(url=link_imagem)
                        embed.set_footer(text="Ingresso Nacional")
                        
                        await canal.send(embed=embed)
                        total_eventos += 1
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        continue
                        
            except Exception as e:
                await canal.send(f"⚠️ Nenhum evento encontrado para {cidade} ou erro ao buscar")
        
        await canal.send(f"✅ Busca concluída! Total de eventos encontrados: **{total_eventos}**")
        
    except Exception as e:
        await canal.send(f"❌ Erro na automação: {str(e)}")
    finally:
        driver.quit()

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    print(f'ID: {bot.user.id}')
    print('------')

@bot.command(name='buscar')
async def buscar(ctx, *, args: str = None):
    """Comando para iniciar a busca de eventos.
    
    Uso:
      !buscar                          → cidades padrão
      !buscar São Paulo                → apenas São Paulo
      !buscar São Paulo;Rio de Janeiro → múltiplas cidades
    """
    cidades_busca = parse_cidades(args)

    if cidades_busca:
        await ctx.send(f"🚀 Buscando eventos em: **{', '.join(cidades_busca)}**")
    else:
        await ctx.send("🚀 Iniciando automação nas cidades padrão...")

    await buscar_eventos(ctx.channel, cidades_busca or None)

@bot.command(name='eventos')
async def eventos(ctx, *, args: str = None):
    """Alias para o comando buscar"""
    await buscar(ctx, args=args)

@bot.command(name='ajuda')
async def ajuda(ctx):
    """Mostra os comandos disponíveis"""
    embed = discord.Embed(
        title="📋 Comandos Disponíveis",
        description="Lista de comandos do bot de eventos",
        color=0x00ff00
    )
    embed.add_field(name="!buscar", value="Busca eventos nas cidades padrão", inline=False)
    embed.add_field(name="!buscar <cidade>", value="Busca em uma cidade específica\nEx: `!buscar Florianópolis`", inline=False)
    embed.add_field(name="!buscar <cidade1>;<cidade2>", value="Busca em múltiplas cidades\nEx: `!buscar São Paulo;Curitiba`", inline=False)
    embed.add_field(name="!eventos", value="Mesmo que !buscar", inline=False)
    embed.add_field(name="!ajuda", value="Mostra esta mensagem", inline=False)
    await ctx.send(embed=embed)

# Iniciar bot
if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ Configure o BOT_TOKEN no arquivo .env antes de executar!")
        print("💡 Copie o .env.example para .env e adicione suas credenciais")
    elif CANAL_ID == 0:
        print("⚠️ CANAL_ID não configurado no .env, mas o bot vai iniciar")
        bot.run(BOT_TOKEN)
    else:
        bot.run(BOT_TOKEN)
