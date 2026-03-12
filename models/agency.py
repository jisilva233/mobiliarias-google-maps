from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Agency:
    nome: str
    cidade: str
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items()}
