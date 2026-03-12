# real-estate-maps Squad

**Versão:** 1.0.0 | **Autor:** jisilva233 | **Licença:** MIT

Squad para mapear imobiliárias via Google Maps com Playwright, armazenar no Supabase e visualizar em dashboard Streamlit.

## Agentes

| Agente | Ícone | Responsabilidade |
|--------|-------|-----------------|
| `@realEstateMaps:scraper-agent` | 🔍 Scout | Scraping Playwright no Google Maps |
| `@realEstateMaps:pipeline-agent` | 🔄 Pipe | ETL, Supabase e Dashboard Streamlit |

## Tasks

| Task | Agente | Descrição |
|------|--------|-----------|
| `scrape-agencies.md` | Scout | Extração do Google Maps |
| `transform-data.md` | Pipe | Limpeza e normalização |
| `load-to-supabase.md` | Pipe | Persistência no Supabase |

## Workflow

```
python scan_agencies.py --city "Curitiba"
    ↓
scrape-agencies (Playwright)
    ↓
transform-data (limpeza + validação)
    ↓
load-to-supabase (upsert idempotente)
```

## Stack

- **Scraping:** Playwright (Python)
- **Banco:** Supabase (PostgreSQL)
- **Dashboard:** Streamlit + Pydeck

## Estrutura do Projeto

Ver `config/source-tree.md` para estrutura completa de arquivos.

## Próximos Passos

1. Ativar `@realEstateMaps:scraper-agent` para implementar o scraper
2. Ativar `@realEstateMaps:pipeline-agent` para setup do Supabase
3. Rodar: `python scan_agencies.py --city "Curitiba"`
4. Dashboard: `streamlit run dashboard.py`
