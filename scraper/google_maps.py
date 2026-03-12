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
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                locale="pt-BR",
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
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
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        # Aguarda o painel de resultados
        try:
            await page.wait_for_selector('div[role="feed"]', timeout=15000)
        except PlaywrightTimeout:
            logger.warning("Painel de resultados não encontrado — tentando continuar")

        # Scroll para carregar resultados
        await self._scroll_feed(page, max_results)

        # Coleta cards
        cards = await page.query_selector_all('[data-result-index]')
        logger.info("%d cards encontrados", len(cards))

        results = []
        for card in cards[:max_results]:
            raw = await self._extract_card(page, card)
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

            cards = await page.query_selector_all('[data-result-index]')
            loaded = len(cards)

            if loaded == prev_count:
                stall_count += 1
            else:
                stall_count = 0
                prev_count = loaded

            logger.debug("Scroll: %d cards carregados", loaded)

    async def _extract_card(self, page: Page, card) -> Optional[dict]:
        """Extrai dados de um card clicando nele para abrir o painel lateral."""
        try:
            await card.click()
            await asyncio.sleep(1.5)

            nome = await self._safe_text(page, 'h1.fontHeadlineLarge, h1[class*="fontHeadline"]')
            if not nome:
                nome = await self._safe_text(page, '[data-attrid="title"]')

            rating = await self._safe_attr(
                page,
                'span[aria-label*="estrelas"], span[aria-label*="stars"]',
                "aria-label",
            )

            reviews = await self._safe_attr(
                page,
                'span[aria-label*="avaliações"], span[aria-label*="reviews"]',
                "aria-label",
            )

            endereco = await self._safe_attr(
                page,
                'button[data-tooltip="Copiar endereço"], button[data-item-id="address"]',
                "aria-label",
            )
            if not endereco:
                endereco = await self._safe_text(
                    page,
                    '[data-item-id="address"] .fontBodyMedium',
                )

            telefone = await self._safe_attr(
                page,
                'button[data-tooltip="Copiar número de telefone"], button[data-item-id*="phone"]',
                "aria-label",
            )
            if not telefone:
                telefone = await self._safe_text(
                    page,
                    '[data-item-id*="phone"] .fontBodyMedium',
                )

            website = await self._safe_attr(
                page,
                'a[data-tooltip="Abrir site"], a[data-item-id="authority"]',
                "href",
            )

            return {
                "nome": nome,
                "endereco": endereco,
                "telefone": telefone,
                "website": website,
                "rating": rating,
                "reviews": reviews,
            }

        except PlaywrightTimeout:
            logger.warning("Timeout ao extrair card — pulando")
            return None
        except Exception as exc:
            logger.warning("Erro ao extrair card: %s", exc)
            return None

    async def _safe_text(self, page: Page, selector: str) -> Optional[str]:
        try:
            el = await page.query_selector(selector)
            if el:
                return await el.inner_text()
        except Exception:
            pass
        return None

    async def _safe_attr(self, page: Page, selector: str, attr: str) -> Optional[str]:
        try:
            el = await page.query_selector(selector)
            if el:
                return await el.get_attribute(attr)
        except Exception:
            pass
        return None
