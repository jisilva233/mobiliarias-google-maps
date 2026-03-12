import asyncio
import logging
from typing import List, Optional
from urllib.parse import quote

from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout

from models.agency import Agency
from scraper.parser import transform_raw

logger = logging.getLogger(__name__)

SCROLL_PAUSE = 1.5  # segundos entre scrolls
ITEM_TIMEOUT = 5000  # ms para aguardar seletores


class GoogleMapsScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless

    async def scrape(self, city: str, max_results: int = 50) -> List[Agency]:
        """Scrapa imobiliárias de uma cidade no Google Maps."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            )
            context = await browser.new_context(
                locale="pt-BR",
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 800},
            )
            page = await context.new_page()

            try:
                results = await self._run(page, city, max_results)
            except Exception as exc:
                logger.error("Erro crítico no scraping: %s", exc)
                await page.screenshot(path="error_scraping.png")
                raise
            finally:
                await browser.close()

        agencies = []
        for raw in results:
            agency = transform_raw(raw, city)
            if agency:
                agencies.append(agency)

        logger.info(
            "Scraping concluído: %d/%d registros válidos para '%s'",
            len(agencies), len(results), city,
        )
        return agencies

    async def _run(self, page: Page, city: str, max_results: int) -> List[dict]:
        query = f"imobiliária em {city}"
        url = f"https://www.google.com/maps/search/{quote(query)}"

        logger.info("Navegando para: %s", url)
        # Google Maps nunca atinge "networkidle" — usar "load" + aguardo explícito
        await page.goto(url, wait_until="load", timeout=60000)
        await asyncio.sleep(3)

        # Aguarda o painel de resultados
        try:
            await page.wait_for_selector('div[role="feed"]', timeout=20000)
        except PlaywrightTimeout:
            logger.warning("Painel de resultados não encontrado — tentando continuar")

        # Scroll para carregar resultados
        await self._scroll_feed(page, max_results)

        # Coleta cards — seletor atual do Google Maps
        cards = await page.query_selector_all('.Nv2PK')
        logger.info("%d cards encontrados", len(cards))

        results = []
        for card in cards[:max_results]:
            raw = await self._extract_card(card)
            if raw:
                results.append(raw)

        return results

    async def _scroll_feed(self, page: Page, max_results: int) -> None:
        """Scroll incremental no feed para carregar mais resultados."""
        feed = await page.query_selector('div[role="feed"]')
        if not feed:
            return

        loaded = 0
        prev_count = 0
        stall_count = 0

        while loaded < max_results and stall_count < 3:
            await feed.evaluate("el => el.scrollBy(0, 800)")
            await asyncio.sleep(SCROLL_PAUSE)

            cards = await page.query_selector_all('.Nv2PK')
            loaded = len(cards)

            if loaded == prev_count:
                stall_count += 1
            else:
                stall_count = 0
                prev_count = loaded

            logger.debug("Scroll: %d cards carregados", loaded)

    async def _extract_card(self, card) -> Optional[dict]:
        """Extrai dados direto do card sem clicar (mais rápido e estável)."""
        import re
        try:
            # Nome
            nome_el = await card.query_selector('.qBF1Pd, .fontHeadlineSmall, [class*="fontHead"]')
            nome = (await nome_el.inner_text()).strip() if nome_el else None
            if not nome:
                return None

            # Rating
            rating_el = await card.query_selector('span[aria-label*="estrela"], span[aria-label*="star"]')
            rating = await rating_el.get_attribute("aria-label") if rating_el else None

            # Reviews — número entre parênteses ex: "(123)"
            reviews_el = await card.query_selector('span[aria-label*="avalia"], span[aria-label*="review"]')
            reviews = await reviews_el.get_attribute("aria-label") if reviews_el else None

            # Texto completo do card para extrair endereço e telefone
            text = await card.inner_text()
            lines = [l.strip() for l in text.split("\n") if l.strip()]

            # Telefone — padrão (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
            telefone = None
            for line in lines:
                if re.search(r'\(\d{2}\)\s*\d{4,5}[-\s]\d{4}', line):
                    telefone = re.search(r'\(\d{2}\)\s*\d{4,5}[-\s]\d{4}', line).group()
                    break

            # Endereço — linha após categoria (ex: "Imobiliária · endereço")
            endereco = None
            for line in lines:
                if "·" in line and re.search(r'\w{3,}', line.split("·")[-1].strip()):
                    endereco = line.split("·")[-1].strip()
                    break

            # Website
            website_el = await card.query_selector('a[data-value="Website"], a[href*="http"][data-value]')
            website = await website_el.get_attribute("href") if website_el else None

            return {
                "nome": nome,
                "endereco": endereco,
                "telefone": telefone,
                "website": website,
                "rating": rating,
                "reviews": reviews,
            }

        except Exception as exc:
            logger.warning("Erro ao extrair card: %s", exc)
            return None

