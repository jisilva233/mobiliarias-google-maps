#!/usr/bin/env python3
"""
CLI para escanear imobiliárias de uma cidade no Google Maps e salvar no Supabase.

Uso:
    python scan_agencies.py --city "Curitiba"
    python scan_agencies.py --city "São Paulo" --max-results 100
    python scan_agencies.py --city "Curitiba" --no-headless
    python scan_agencies.py --setup-db
"""

import argparse
import asyncio
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def cmd_setup_db():
    """Exibe o SQL para criar a tabela no Supabase."""
    from db.repository import AgencyRepository
    print("Execute o SQL abaixo no Supabase SQL Editor:\n")
    print(AgencyRepository.get_create_sql())


async def cmd_scan(city: str, max_results: int, headless: bool):
    """Executa o pipeline completo: scrape → transform → upsert."""
    from scraper.google_maps import GoogleMapsScraper
    from db.client import get_client
    from db.repository import AgencyRepository

    logger.info("Iniciando scan para: %s (max: %d)", city, max_results)

    # 1. Scrape
    scraper = GoogleMapsScraper(headless=headless)
    agencies = await scraper.scrape(city=city, max_results=max_results)

    if not agencies:
        logger.warning("Nenhuma imobiliária encontrada para '%s'.", city)
        return

    logger.info("%d imobiliárias extraídas.", len(agencies))

    # 2. Upsert no Supabase
    client = get_client()
    repo = AgencyRepository(client)
    report = repo.upsert(agencies)

    print(
        f"\n✅ Scan concluído para '{city}'\n"
        f"   Registros processados: {len(agencies)}\n"
        f"   Inseridos/Atualizados: {report['inserted']}\n"
        f"   Erros:                 {report['errors']}\n"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Mapeia imobiliárias no Google Maps e salva no Supabase."
    )
    parser.add_argument("--city", type=str, help="Nome da cidade a escanear")
    parser.add_argument(
        "--max-results", type=int, default=50,
        help="Máximo de resultados (default: 50)",
    )
    parser.add_argument(
        "--no-headless", action="store_true",
        help="Abrir browser visível (útil para debug)",
    )
    parser.add_argument(
        "--setup-db", action="store_true",
        help="Exibir SQL para criar a tabela no Supabase",
    )

    args = parser.parse_args()

    if args.setup_db:
        cmd_setup_db()
        sys.exit(0)

    if not args.city:
        parser.error("--city é obrigatório. Ex: --city 'Curitiba'")

    asyncio.run(
        cmd_scan(
            city=args.city,
            max_results=args.max_results,
            headless=not args.no_headless,
        )
    )


if __name__ == "__main__":
    main()
