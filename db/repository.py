import logging
import time
from typing import List

from supabase import Client

from models.agency import Agency

logger = logging.getLogger(__name__)

TABLE = "real_estate_agencies"
BATCH_SIZE = 50
MAX_RETRIES = 3


class AgencyRepository:
    def __init__(self, client: Client):
        self.client = client

    def upsert(self, agencies: List[Agency]) -> dict:
        """Upsert em lotes. Retorna relatório {inserted, updated, errors}."""
        if not agencies:
            return {"inserted": 0, "updated": 0, "errors": 0}

        # Deduplicar por (nome, cidade) — manter último registro
        seen = {}
        for a in agencies:
            seen[(a.nome, a.cidade)] = a
        agencies = list(seen.values())
        logger.info("%d registros após deduplicação", len(agencies))

        report = {"inserted": 0, "updated": 0, "errors": 0}
        batches = [
            agencies[i: i + BATCH_SIZE]
            for i in range(0, len(agencies), BATCH_SIZE)
        ]

        for idx, batch in enumerate(batches, 1):
            logger.info("Inserindo lote %d/%d (%d registros)...", idx, len(batches), len(batch))
            data = [a.to_dict() for a in batch]
            success = self._upsert_with_retry(data)
            if success:
                report["inserted"] += len(batch)
            else:
                report["errors"] += len(batch)

        return report

    def _upsert_with_retry(self, data: list) -> bool:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                self.client.table(TABLE).upsert(
                    data,
                    on_conflict="nome,cidade",
                ).execute()
                return True
            except Exception as exc:
                wait = 2 ** attempt
                logger.warning(
                    "Tentativa %d/%d falhou: %s. Aguardando %ds...",
                    attempt, MAX_RETRIES, exc, wait,
                )
                if attempt < MAX_RETRIES:
                    time.sleep(wait)

        logger.error("Falha após %d tentativas.", MAX_RETRIES)
        return False

    def fetch_all(self, cidade: str | None = None) -> list:
        """Retorna todos os registros, opcionalmente filtrado por cidade."""
        query = self.client.table(TABLE).select("*")
        if cidade:
            query = query.eq("cidade", cidade)
        response = query.order("rating", desc=True).execute()
        return response.data or []

    @staticmethod
    def get_create_sql() -> str:
        return """
CREATE TABLE IF NOT EXISTS real_estate_agencies (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nome        TEXT NOT NULL,
  endereco    TEXT,
  telefone    TEXT,
  website     TEXT,
  rating      FLOAT,
  reviews     INTEGER,
  cidade      TEXT NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(nome, cidade)
);

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_updated_at ON real_estate_agencies;
CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON real_estate_agencies
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
""".strip()
