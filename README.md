# Automação com Selenium

Ambiente Python configurado para automação web com Selenium.

## Como usar

### 1. Ativar o ambiente virtual

```bash
# Windows (PowerShell)
.\venv\Scripts\activate

# Windows (CMD)
venv\Scripts\activate.bat
```

### 2. Executar o exemplo

```bash
python exemplo_selenium.py
```

## Estrutura

- `venv/` - Ambiente virtual Python
- `exemplo_selenium.py` - Script de exemplo com Selenium
- `requirements.txt` - Dependências do projeto

## Pacotes instalados

- **selenium** - Framework de automação web
- **webdriver-manager** - Gerencia automaticamente os drivers dos navegadores

## Dicas

- O webdriver-manager baixa automaticamente o ChromeDriver na primeira execução
- Você pode usar outros navegadores (Firefox, Edge) alterando o driver
- Use `WebDriverWait` para esperar elementos carregarem antes de interagir
