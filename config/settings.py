"""Configuração local; nunca utilize service_role em um cliente desktop."""
import os
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_API_KEY = os.environ.get("SUPABASE_KEY", "")
