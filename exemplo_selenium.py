from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from discord_webhook import DiscordWebhook, DiscordEmbed
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Lista de cidades para pesquisar
cidades = ["Brusque", "Blumenau", "Balneário Camboriú", "Camboriú", "Itapema", "Porto Belo", "Itajaí"]

# CONFIGURAÇÃO DO DISCORD WEBHOOK
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def enviar_para_discord(nome, data, cidade, link_imagem):
    """Envia mensagem com embed para o Discord"""
    try:
        webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
        
        # Criar embed (mensagem formatada)
        embed = DiscordEmbed(
            title=f"🎭 {nome}",
            description=f"**📅 Data:** {data}\n**📍 Local:** {cidade}",
            color=0x5865F2  # Cor azul do Discord
        )
        
        # Adicionar imagem ao embed
        embed.set_image(url=link_imagem)
        embed.set_footer(text="Ingresso Nacional")
        
        webhook.add_embed(embed)
        
        # Enviar
        response = webhook.execute()
        
        if response.status_code == 200:
            return True
        return False
        
    except Exception as e:
        print(f"    ❌ Erro ao enviar para Discord: {e}")
        return False

# Configurar o driver do Chrome automaticamente
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    # Acessar o site
    driver.get("https://www.ingressonacional.com.br/balada")
    print("Site carregado!")
    
    # Aguardar a página carregar
    time.sleep(3)
    
    # Loop pelas cidades
    for cidade in cidades:
        print(f"\n{'='*60}")
        print(f"Pesquisando: {cidade}")
        print(f"{'='*60}")
        
        # Encontrar a barra de pesquisa usando o XPATH fornecido
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/div/div[2]/div/form/div/div/input"))
        )
        
        # Limpar o campo antes de digitar
        search_box.clear()
        
        # Digitar o nome da cidade
        search_box.send_keys(cidade)
        
        # Aguardar um pouco para ver a pesquisa
        time.sleep(2)
        
        # Pressionar Enter para pesquisar
        search_box.send_keys(Keys.RETURN)
        
        # Aguardar os resultados carregarem
        time.sleep(3)
        
        # Buscar a lista de eventos
        try:
            lista_eventos = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/div[3]/div[1]")
            
            # Encontrar todos os eventos dentro da lista
            eventos = lista_eventos.find_elements(By.XPATH, ".//div[contains(@class, 'event') or contains(@class, 'item')]")
            
            if not eventos:
                # Tentar buscar de forma mais genérica
                eventos = lista_eventos.find_elements(By.XPATH, "./div")
            
            print(f"\nEventos encontrados em {cidade}: {len(eventos)}")
            
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
                    
                    print(f"\n  Evento {i}:")
                    print(f"  📅 Data: {data}")
                    print(f"  🎭 Nome: {nome}")
                    print(f"  🖼️  Imagem: {link_imagem}")
                    
                    # Enviar para Discord
                    print(f"  📤 Enviando para Discord...", end=" ")
                    if enviar_para_discord(nome, data, cidade, link_imagem):
                        print("✅ Enviado!")
                    else:
                        print("❌ Falha ao enviar")
                    
                except Exception as e:
                    print(f"  ⚠️ Não foi possível extrair dados do evento {i}")
                    continue
            
        except Exception as e:
            print(f"⚠️ Nenhum evento encontrado para {cidade} ou erro ao buscar: {e}")
    
    print("\n✓ Todas as pesquisas foram realizadas!")
    
except Exception as e:
    print(f"Erro: {e}")
    
finally:
    # Fechar o navegador
    input("\nPressione Enter para fechar o navegador...")
    driver.quit()
