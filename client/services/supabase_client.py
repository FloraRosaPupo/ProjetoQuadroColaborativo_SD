"""Cliente inicializado sob demanda, sem conexão durante o import."""
import os
import base64
import json
from functools import lru_cache


def validate_public_key(key):
    """Reject server credentials before the desktop client opens a connection.

    JWT payload inspection only identifies key type; Supabase verifies the key.
    """
    message = "SUPABASE_KEY deve ser pública (anon/publishable), nunca service_role/secret."
    if key.startswith("sb_publishable_") and len(key) > len("sb_publishable_"):
        return
    if key.startswith("sb_secret_"):
        raise ValueError(message)
    try:
        parts = key.split(".")
        if len(parts) != 3:
            raise ValueError(message)
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload))
        if not isinstance(claims, dict) or claims.get("role") != "anon":
            raise ValueError(message)
    except (ValueError, UnicodeError, TypeError):
        raise ValueError(message) from None


@lru_cache(maxsize=1)
def get_supabase_client():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        raise ValueError("Configure SUPABASE_URL e SUPABASE_KEY (chave pública anon/publishable).")
    validate_public_key(key)
    from supabase import create_client
    return create_client(url, key)
