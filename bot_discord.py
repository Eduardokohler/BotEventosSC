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
import unicodedata

# CONFIGURAÇÕES - Usar variável de ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
CANAL_ID = int(os.getenv("CANAL_ID", "0"))  # ID do canal onde o bot vai responder

# Lista de cidades
cidades = ["Brusque", "Blumenau", "Balneário Camboriú", "Camboriú", "Itapema", "Porto Belo", "Itajaí"]

# Controle de execuções ativas: {user_id: asyncio.Event}
# O Event é usado como token de cancelamento — quando setado, sinaliza para parar
buscas_ativas: dict[int, asyncio.Event] = {}

# Configurar bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def parse_cidades(args: str) -> list[str]:
    """Parseia cidades informadas pelo usuário, separadas por ';'"""
    if not args or not args.strip():
        return []
    return [c.strip() for c in args.split(";") if c.strip()]

async def cancelavel_sleep(segundos: float, cancelar: asyncio.Event):
    """asyncio.sleep que respeita o token de cancelamento."""
    try:
        await asyncio.wait_for(cancelar.wait(), timeout=segundos)
    except asyncio.TimeoutError:
        pass  # Tempo esgotou normalmente, sem cancelamento


def criar_driver() -> webdriver.Chrome:
    """Cria e retorna uma instância do Chrome headless."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


async def _scrape_blueticket_categoria(canal, cidade: str, categoria: str, driver: webdriver.Chrome, cancelar: asyncio.Event) -> int:
    """Busca eventos na Blueticket para uma cidade e categoria específica."""
    import urllib.parse
    import re

    url = f"https://www.blueticket.com.br/search?q={urllib.parse.quote(cidade)}&category={urllib.parse.quote(categoria)}"
    driver.get(url)

    # Aguardar cards ou mensagem de "nenhum resultado" (SPA Vue.js)
    try:
        WebDriverWait(driver, 10).until(lambda d:
            d.find_elements(By.CSS_SELECTOR, "a.event-card") or
            d.find_elements(By.XPATH, "//*[contains(text(),'Nenhuma experiência')]")
        )
    except Exception:
        return 0

    await cancelavel_sleep(1, cancelar)
    if cancelar.is_set():
        return 0

    total = 0
    try:
        cards = driver.find_elements(By.CSS_SELECTOR, "a.event-card")
        for card in cards:
            if cancelar.is_set():
                return total
            try:
                href  = card.get_attribute("href") or ""
                nome  = card.find_element(By.CSS_SELECTOR, ".event-title").text.strip()
                local = card.find_element(By.CSS_SELECTOR, ".event-location").text.strip()
                data  = card.find_element(By.CSS_SELECTOR, ".event-date").text.strip()
                hora  = card.find_element(By.CSS_SELECTOR, ".event-hour").text.strip()

                link_imagem = None
                try:
                    bg = card.find_element(By.CSS_SELECTOR, ".v-image__image").get_attribute("style")
                    match = re.search(r'url\(["\']?(https?://[^"\')\s]+)["\']?\)', bg)
                    if match:
                        link_imagem = match.group(1)
                except Exception:
                    pass

                icone = "🪩"
                embed = discord.Embed(
                    title=f"{icone} {nome}",
                    description=f"**📅 Data:** {data} às {hora}\n**📍 Local:** {local}\n**🏷️ Categoria:** {categoria}",
                    color=0x1DA1F2,
                    url=href
                )
                if link_imagem:
                    embed.set_image(url=link_imagem)
                embed.add_field(name="🔗 Link", value=href, inline=False)
                embed.set_footer(text="Blueticket")

                await canal.send(embed=embed)
                total += 1
                await cancelavel_sleep(0.5, cancelar)

            except Exception:
                continue
    except Exception:
        pass

    return total


async def buscar_blueticket(canal, cidade: str, driver: webdriver.Chrome, cancelar: asyncio.Event) -> int:
    """Busca eventos na Blueticket para uma cidade."""
    await canal.send(f"🔵 **Blueticket** em **{cidade}**")
    encontrados = await _scrape_blueticket_categoria(canal, cidade, "Baladas", driver, cancelar)
    if encontrados == 0 and not cancelar.is_set():
        await canal.send(f"⚠️ Nenhum evento encontrado na Blueticket para {cidade}")
    return encontrados


def cidade_para_slug(cidade: str) -> str:
    """Converte nome de cidade para slug usado pelo Guichê Web.
    Ex: 'Balneário Camboriú' → 'balneario-camboriu'
    """
    slug = unicodedata.normalize("NFD", cidade)
    slug = "".join(c for c in slug if unicodedata.category(c) != "Mn")  # remove acentos
    slug = slug.lower().strip().replace(" ", "-")
    return slug


async def buscar_guicheweb(canal, cidade: str, driver: webdriver.Chrome, cancelar: asyncio.Event) -> int:
    """Busca eventos no Guichê Web para uma cidade via rota /pesquisa/{slug}."""
    slug = cidade_para_slug(cidade)
    url = f"https://www.guicheweb.com.br/pesquisa/{slug}"
    driver.get(url)

    # Site renderiza via SSR, mas aguarda um pouco para garantir
    try:
        WebDriverWait(driver, 8).until(lambda d:
            d.find_elements(By.CSS_SELECTOR, "a.text-reset .Card") or
            d.find_elements(By.XPATH, "//*[contains(text(),'NENHUM EVENTO')]")
        )
    except Exception:
        return 0

    await cancelavel_sleep(1, cancelar)
    if cancelar.is_set():
        return 0

    total = 0
    try:
        cards = driver.find_elements(By.CSS_SELECTOR, "a.text-reset")
        for card in cards:
            if cancelar.is_set():
                return total
            try:
                href   = card.get_attribute("href") or ""
                nome   = card.find_element(By.CSS_SELECTOR, "h6.Title").text.strip()
                cidade_card = card.find_element(By.CSS_SELECTOR, ".Cidade").text.strip()
                data   = card.find_element(By.CSS_SELECTOR, ".Data").text.strip()
                imagem = card.find_element(By.CSS_SELECTOR, "img.card-img-top").get_attribute("src")

                embed = discord.Embed(
                    title=f"🎟️ {nome}",
                    description=f"**📅 Data:** {data}\n**📍 Local:** {cidade_card}",
                    color=0xE8431A,
                    url=href
                )
                if imagem:
                    embed.set_image(url=imagem)
                embed.add_field(name="🔗 Link", value=href, inline=False)
                embed.set_footer(text="Guichê Web")

                await canal.send(embed=embed)
                total += 1
                await cancelavel_sleep(0.5, cancelar)

            except Exception:
                continue
    except Exception:
        pass

    return total


async def buscar_pensanoevento(canal, cidade: str, driver: webdriver.Chrome, cancelar: asyncio.Event) -> int:
    """Busca eventos no Pensa no Evento para uma cidade via parâmetro &cidade=."""
    import urllib.parse

    def normalizar(texto: str) -> str:
        """Remove acentos e converte para minúsculas para comparação."""
        texto = unicodedata.normalize("NFD", texto)
        texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
        return texto.lower().strip()

    def cidade_do_local(local: str) -> str:
        """Extrai a cidade do campo local no formato 'Nome do Local - Cidade/UF'."""
        # Pega a parte após o último " - "
        if " - " in local:
            cidade_uf = local.rsplit(" - ", 1)[-1]  # ex: "Blumenau/SC"
            return cidade_uf.split("/")[0].strip()   # ex: "Blumenau"
        return local

    # Mapa de normalização: nome usado no bot → data-name exato do site
    MAPA_CIDADES = {
        "brusque": "Brusque",
        "blumenau": "Blumenau",
        "balneário camboriú": "Balneário Camboriú",
        "balneario camboriu": "Balneário Camboriú",
        "camboriú": "Camboriú",
        "camboriu": "Camboriú",
        "itapema": "Itapema",
        "portobelo": "Porto Belo",  # não existe no site
        "itajaí": "Itajaí",
        "itajai": "Itajaí",
        "florianópolis": "Florianópolis",
        "florianopolis": "Florianópolis",
        "joinville": "Joinville",
        "jaraguá do sul": "Jaraguá do Sul",
        "jaragua do sul": "Jaraguá do Sul",
        "navegantes": "Navegantes",
        "penha": "Penha",
        "gaspar": "Gaspar",
        "biguaçu": "Biguaçu",
        "biguacu": "Biguaçu",
        "palhoça": "Palhoça",
        "palhoca": "Palhoça",
        "são josé": "São José",
        "sao jose": "São José",
        "criciúma": "Criciúma",
        "criciuma": "Criciúma",
        "laguna": "Laguna",
        "imbituba": "Imbituba",
        "tubarão": "Tubarão",
        "tubarao": "Tubarão",
    }

    cidade_normalizada = MAPA_CIDADES.get(cidade.lower().strip())
    if cidade_normalizada is None:
        cidade_normalizada = cidade.strip()

    # Versão normalizada da cidade buscada para validação
    cidade_busca_norm = normalizar(cidade_normalizada)

    cidade_encoded = urllib.parse.quote(cidade_normalizada)
    url = f"https://www.pensanoevento.com.br/sitev2/eventos/busca?tipo=Baladas&cidade={cidade_encoded}"
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(lambda d:
            d.find_elements(By.CSS_SELECTOR, "a.hotelsCard") or
            d.find_elements(By.XPATH, "//*[contains(text(),'Nenhum evento')]")
        )
    except Exception:
        return 0

    await cancelavel_sleep(1, cancelar)
    if cancelar.is_set():
        return 0

    total = 0
    ignorados = 0
    try:
        cards = driver.find_elements(By.CSS_SELECTOR, "a.hotelsCard")
        for card in cards:
            if cancelar.is_set():
                return total
            try:
                href  = card.get_attribute("href") or ""
                nome  = card.find_element(By.CSS_SELECTOR, "h4 span").text.strip()
                data  = card.find_element(By.CSS_SELECTOR, ".text-14.text-light-1").text.strip()
                local = card.find_element(By.CSS_SELECTOR, "p.text-light-1").text.strip()
                imagem = card.find_element(By.CSS_SELECTOR, "img").get_attribute("src")

                # Validar se o evento é realmente da cidade buscada
                cidade_evento = cidade_do_local(local)
                if normalizar(cidade_evento) != cidade_busca_norm:
                    ignorados += 1
                    continue

                embed = discord.Embed(
                    title=f"🎉 {nome}",
                    description=f"**📅 Data:** {data}\n**📍 Local:** {local}",
                    color=0xFF6B35,
                    url=href
                )
                if imagem:
                    embed.set_image(url=imagem)
                embed.add_field(name="🔗 Link", value=href, inline=False)
                embed.set_footer(text="Pensa no Evento")

                await canal.send(embed=embed)
                total += 1
                await cancelavel_sleep(0.5, cancelar)

            except Exception:
                continue

    except Exception:
        pass

    return total


async def buscar_eventos(canal, cidades_busca: list[str] = None, cancelar: asyncio.Event = None):
    """Função que executa a automação do Selenium com suporte a cancelamento."""
    lista = cidades_busca if cidades_busca else cidades

    await canal.send("🔍 Iniciando busca de eventos...")

    driver = criar_driver()

    try:
        total_eventos = 0

        # ── Ingresso Nacional ──────────────────────────────────────────────
        await canal.send("🎟️ **Ingresso Nacional**")
        driver.get("https://www.ingressonacional.com.br/balada")
        await cancelavel_sleep(3, cancelar)
        if cancelar.is_set():
            return

        for cidade in lista:
            if cancelar.is_set():
                return

            await canal.send(f"📍 Pesquisando em: **{cidade}**")

            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/div/div[2]/div/form/div/div/input"))
            )
            search_box.clear()
            search_box.send_keys(cidade)

            await cancelavel_sleep(2, cancelar)
            if cancelar.is_set():
                return

            search_box.send_keys(Keys.RETURN)

            await cancelavel_sleep(3, cancelar)
            if cancelar.is_set():
                return

            try:
                lista_eventos = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/div[3]/div[1]")
                eventos = lista_eventos.find_elements(By.XPATH, ".//div[contains(@class, 'event') or contains(@class, 'item')]")
                if not eventos:
                    eventos = lista_eventos.find_elements(By.XPATH, "./div")

                if not eventos:
                    await canal.send(f"⚠️ Nenhum evento encontrado em {cidade}")
                    continue

                for i in range(1, len(eventos) + 1):
                    if cancelar.is_set():
                        return
                    try:
                        data_xpath   = f"/html/body/div[1]/div[3]/div/div[3]/div[1]/div[{i}]/div[1]/div/div[1]/span"
                        nome_xpath   = f"/html/body/div[1]/div[3]/div/div[3]/div[1]/div[{i}]/div[2]/div[1]/h2"
                        imagem_xpath = f"/html/body/div[1]/div[3]/div/div[3]/div[1]/div[{i}]/a/div/img"

                        data = driver.find_element(By.XPATH, data_xpath).text
                        nome = driver.find_element(By.XPATH, nome_xpath).text
                        link_imagem = driver.find_element(By.XPATH, imagem_xpath).get_attribute("src")

                        embed = discord.Embed(
                            title=f"🎭 {nome}",
                            description=f"**📅 Data:** {data}\n**📍 Local:** {cidade}",
                            color=0x5865F2
                        )
                        embed.set_image(url=link_imagem)
                        embed.set_footer(text="Ingresso Nacional")

                        await canal.send(embed=embed)
                        total_eventos += 1
                        await cancelavel_sleep(1, cancelar)
                    except Exception:
                        continue

            except Exception:
                await canal.send(f"⚠️ Nenhum evento encontrado para {cidade} ou erro ao buscar")

        # ── Blueticket + Guichê Web ────────────────────────────────────────
        if not cancelar.is_set():
            for cidade in lista:
                if cancelar.is_set():
                    return
                bt_total = await buscar_blueticket(canal, cidade, driver, cancelar)
                total_eventos += bt_total

                if cancelar.is_set():
                    return
                await canal.send(f"🟠 **Guichê Web** em **{cidade}**")
                gw_total = await buscar_guicheweb(canal, cidade, driver, cancelar)
                if gw_total == 0 and not cancelar.is_set():
                    await canal.send(f"⚠️ Nenhum evento encontrado no Guichê Web para {cidade}")
                total_eventos += gw_total

                if cancelar.is_set():
                    return
                await canal.send(f"🎉 **Pensa no Evento** em **{cidade}**")
                pe_total = await buscar_pensanoevento(canal, cidade, driver, cancelar)
                if pe_total == 0 and not cancelar.is_set():
                    await canal.send(f"⚠️ Nenhum evento encontrado no Pensa no Evento para {cidade}")
                total_eventos += pe_total

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
      !buscar                    → cidades padrão
      !buscar Blumenau           → cidade específica
      !buscar Blumenau;Itajaí    → múltiplas cidades
    """
    user_id = ctx.author.id

    if user_id in buscas_ativas:
        await ctx.send("⚠️ Você já tem uma busca em andamento. Use `!parar` para cancelá-la antes de iniciar outra.")
        return

    cidades_busca = parse_cidades(args)

    if cidades_busca:
        await ctx.send(f"🚀 Buscando eventos em: **{', '.join(cidades_busca)}**")
    else:
        await ctx.send("🚀 Buscando eventos nas cidades padrão...")

    cancelar = asyncio.Event()
    buscas_ativas[user_id] = cancelar

    try:
        await buscar_eventos(ctx.channel, cidades_busca or None, cancelar)
    finally:
        buscas_ativas.pop(user_id, None)

    if cancelar.is_set():
        await ctx.send("🛑 Busca cancelada pelo usuário.")


@bot.command(name='parar', aliases=['cancelar'])
async def parar(ctx):
    """Cancela a busca em andamento do usuário."""
    user_id = ctx.author.id

    if user_id not in buscas_ativas:
        await ctx.send("ℹ️ Você não tem nenhuma busca em andamento.")
        return

    buscas_ativas[user_id].set()  # Sinaliza o cancelamento
    await ctx.send("🛑 Cancelamento solicitado. Aguarde a operação ser interrompida...")

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
    embed.add_field(name="!buscar <cidade1>;<cidade2>", value="Busca em múltiplas cidades\nEx: `!buscar Blumenau;Itajaí`", inline=False)
    embed.add_field(name="!eventos", value="Mesmo que !buscar", inline=False)
    embed.add_field(name="!parar", value="Cancela a busca em andamento (também: `!cancelar`)", inline=False)
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
