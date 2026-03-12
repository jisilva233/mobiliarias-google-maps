# Coding Standards — real-estate-maps

## Python
- PEP 8 compliance
- Type hints obrigatórios em funções públicas
- Docstrings em classes e funções públicas
- Modular: cada responsabilidade em arquivo separado

## Estrutura de Arquivos
- `scan_agencies.py` — CLI entry point
- `scraper/` — módulo de scraping Playwright
- `db/` — módulo Supabase
- `dashboard/` — módulo Streamlit

## Tratamento de Erros
- Usar try/except em operações de I/O e rede
- Logar erros com contexto suficiente
- Nunca suprimir exceções silenciosamente

## Dados
- Sempre validar dados antes de inserir no Supabase
- Campos opcionais como `None`, nunca string vazia
