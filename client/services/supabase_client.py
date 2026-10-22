"""Cliente inicializado sob demanda, sem conexão durante o import."""
import os
from functools import lru_cache

@lru_cache(maxsize=1)
def get_supabase_client():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        raise ValueError("Configure SUPABASE_URL e SUPABASE_KEY (chave pública anon/publishable).")
    from supabase import create_client
    return create_client(url, key)
