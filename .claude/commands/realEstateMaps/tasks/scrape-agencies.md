---
task: Scrape Agencies from Google Maps
responsavel: "@scraper-agent"
atomic_layer: task
elicit: false
---

# scrape-agencies

Extrai dados de imobiliárias do Google Maps usando Playwright.

## Inputs
- `city`: Nome da cidade (ex: "Curitiba")
- `max_results`: Máximo de resultados (default: 50)
- `headless`: Modo headless (default: true)

## Outputs
- Lista de objetos `Agency` com: nome, endereço, telefone, website, rating, reviews

## Passos

### 1. Inicializar Playwright
```python
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=headless)
    page = await browser.new_page()
```

### 2. Navegar para Google Maps
```python
query = f"imobiliária em {city}"
url = f"https://www.google.com/maps/search/{quote(query)}"
await page.goto(url, wait_until="networkidle")
```

### 3. Scroll para carregar resultados
- Localizar painel de resultados: `div[role="feed"]`
- Scroll incremental até atingir `max_results` ou fim da lista
- Aguardar 1-2s entre scrolls (anti-bot)

### 4. Extrair dados de cada card
Para cada item `[data-result-index]`:
- **Nome**: `h3.fontHeadlineSmall` ou `div.fontBodyMedium > span`
- **Avaliação**: `span[aria-label*="estrelas"]` → float
- **Reviews**: `span[aria-label*="avaliações"]` → int
- **Endereço**: clicar no card → `button[data-tooltip="Copiar endereço"]`
- **Telefone**: `button[data-tooltip="Copiar número de telefone"]`
- **Website**: `a[data-tooltip="Abrir site"]` → href

### 5. Retornar lista de Agency
```python
return [Agency(nome=..., endereco=..., telefone=..., ...) for item in results]
```

## Tratamento de Erros
- Seletor não encontrado → campo como `None`
- Timeout → log warning, continuar próximo item
- Screenshot em erro crítico: `page.screenshot(path="error.png")`

## Notas
- Google Maps muda seletores periodicamente — manter `data/selectors.yaml` atualizado
- Rate limit: máx 100 resultados por sessão para evitar bloqueio
