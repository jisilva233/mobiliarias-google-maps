#!/usr/bin/env python3
"""
CLI para escanear imobiliarias de uma ou mais cidades no Google Maps e salvar no Supabase.

Uso:
    python scan_agencies.py --city "Curitiba"
    python scan_agencies.py --city "Curitiba" --city "Florianopolis" --city "Sao Paulo"
    python scan_agencies.py --city "Curitiba" --max-results 100 --geocode
    python scan_agencies.py --city "Curitiba" --no-headless
    python scan_agencies.py --setup-db
    python scan_agencies.py --geocode-existing  # geocodifica registros sem coordenadas
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
    from db.repository import AgencyRepository
    print("Execute o SQL abaixo no Supabase SQL Editor:\n")
    print(AgencyRepository.get_create_sql())


def cmd_geocode_existing():
    """Geocodifica registros existentes no Supabase que nao tem lat/lon."""
    from db.client import get_client
    from db.repository import AgencyRepository
    from scraper.geocoder import geocode_address

    client = get_client()
    repo = AgencyRepository(client)

    records = repo.fetch_all()
    sem_coords = [r for r in records if not r.get("latitude")]
    logger.info("%d registros sem coordenadas para geocodificar", len(sem_coords))

    updated = 0
    for rec in sem_coords:
        lat, lon = geocode_address(rec.get("endereco"), rec.get("cidade", ""))
        if lat:
            client.table("real_estate_agencies").update(
                {"latitude": lat, "longitude": lon}
            ).eq("id", rec["id"]).execute()
            updated += 1
            logger.info("  Atualizado: %s -> (%.4f, %.4f)", rec["nome"], lat, lon)
        else:
            logger.warning("  Sem coords: %s", rec["nome"])

    print(f"\nGeocodificacao concluida: {updated}/{len(sem_coords)} atualizados")


async def cmd_scan(cities: list, max_results: int, headless: bool, geocode: bool):
    from scraper.google_maps import GoogleMapsScraper
    from db.client import get_client
    from db.repository import AgencyRepository

    client = get_client()
    repo = AgencyRepository(client)
    total_report = {"processed": 0, "inserted": 0, "errors": 0}

    for city in cities:
        print(f"\n--- Escaneando: {city} ---")
        logger.info("Iniciando scan para: %s (max: %d)", city, max_results)

        # 1. Scrape
        scraper = GoogleMapsScraper(headless=headless)
        agencies = await scraper.scrape(city=city, max_results=max_results)

        if not agencies:
            logger.warning("Nenhuma imobiliaria encontrada para '%s'.", city)
            continue

        logger.info("%d imobiliarias extraidas.", len(agencies))

        # 2. Geocoding (opcional)
        if geocode:
            logger.info("Geocodificando enderecos (pode demorar ~%ds)...", len(agencies))
            from scraper.geocoder import geocode_agencies
            agencies = geocode_agencies(agencies, city)

        # 3. Upsert no Supabase
        report = repo.upsert(agencies)
        total_report["processed"] += len(agencies)
        total_report["inserted"] += report["inserted"]
        total_report["errors"] += report["errors"]

        print(
            f"  Processados: {len(agencies)}"
            f" | Salvos: {report['inserted']}"
            f" | Erros: {report['errors']}"
        )

    print(
        f"\nResumo total ({len(cities)} cidade(s)):"
        f"\n  Processados: {total_report['processed']}"
        f"\n  Salvos:      {total_report['inserted']}"
        f"\n  Erros:       {total_report['errors']}\n"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Mapeia imobiliarias no Google Maps e salva no Supabase.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python scan_agencies.py --city "Curitiba"
  python scan_agencies.py --city "Curitiba" --city "Florianopolis"
  python scan_agencies.py --city "Sao Paulo" --max-results 100 --geocode
  python scan_agencies.py --geocode-existing
  python scan_agencies.py --setup-db
        """,
    )
    parser.add_argument(
        "--city", type=str, action="append", dest="cities",
        metavar="CIDADE",
        help="Cidade a escanear (repita para multiplas cidades)",
    )
    parser.add_argument(
        "--max-results", type=int, default=50,
        help="Maximo de resultados por cidade (default: 50)",
    )
    parser.add_argument(
        "--no-headless", action="store_true",
        help="Abrir browser visivel (util para debug)",
    )
    parser.add_argument(
        "--geocode", action="store_true",
        help="Geocodificar enderecos apos scraping (Nominatim/OSM, gratuito)",
    )
    parser.add_argument(
        "--geocode-existing", action="store_true",
        help="Geocodificar registros existentes no Supabase sem coordenadas",
    )
    parser.add_argument(
        "--setup-db", action="store_true",
        help="Exibir SQL para criar/atualizar tabela no Supabase",
    )

    args = parser.parse_args()

    if args.setup_db:
        cmd_setup_db()
        sys.exit(0)

    if args.geocode_existing:
        cmd_geocode_existing()
        sys.exit(0)

    if not args.cities:
        parser.error("--city e obrigatorio. Ex: --city 'Curitiba'")

    asyncio.run(
        cmd_scan(
            cities=args.cities,
            max_results=args.max_results,
            headless=not args.no_headless,
            geocode=args.geocode,
        )
    )


if __name__ == "__main__":
    main()
