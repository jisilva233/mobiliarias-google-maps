import os
from functools import lru_cache

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def get_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise EnvironmentError(
            "SUPABASE_URL e SUPABASE_KEY devem estar definidos no .env"
        )

    return create_client(url, key)
