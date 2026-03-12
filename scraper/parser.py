import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def parse_nome(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    return raw.strip().title()


def parse_endereco(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    return raw.strip()


def parse_telefone(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    if not digits:
        return None
    # Normalizar: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return digits


def parse_website(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    url = raw.strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return None


def parse_rating(raw: Optional[str]) -> Optional[float]:
    if not raw:
        return None
    try:
        cleaned = raw.replace(",", ".").strip()
        value = float(re.search(r"[\d.]+", cleaned).group())
        return value if 0.0 <= value <= 5.0 else None
    except (ValueError, AttributeError):
        return None


def parse_reviews(raw: Optional[str]) -> Optional[int]:
    if not raw:
        return None
    try:
        digits = re.search(r"\d[\d.,]*", raw)
        if not digits:
            return None
        return int(digits.group().replace(".", "").replace(",", ""))
    except (ValueError, AttributeError):
        return None


def transform_raw(raw: dict, cidade: str):
    """Transforma dict bruto em Agency validada. Retorna None se inválido."""
    from models.agency import Agency

    nome = parse_nome(raw.get("nome"))
    if not nome:
        logger.warning("Registro descartado: nome ausente. Raw: %s", raw)
        return None

    return Agency(
        nome=nome,
        cidade=cidade,
        endereco=parse_endereco(raw.get("endereco")),
        telefone=parse_telefone(raw.get("telefone")),
        website=parse_website(raw.get("website")),
        rating=parse_rating(raw.get("rating")),
        reviews=parse_reviews(raw.get("reviews")),
    )
