# -*- coding: utf-8 -*-
"""Configurações e inicialização do cliente Supabase."""

import os
from supabase import create_client, Client

# Carrega as variáveis de ambiente ou usa os valores do settings.py
# É mais seguro usar variáveis de ambiente em produção.
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://igtwulxvnbukoojlrbao.supabase.co")
# A chave fornecida parece ser a service_role key, que não deve ser usada no front-end.
# É necessário usar a anon_key (chave pública anônima) para operações do lado do cliente.
# Vou usar a chave fornecida por enquanto, mas isso PRECISA ser corrigido.
# Idealmente, a autenticação e operações de escrita deveriam passar por um backend seguro.
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlndHd1bHh2bmJ1a29vamxyYmFvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDU5MTI2NSwiZXhwIjoyMDYwMTY3MjY1fQ.BEjxPUlvYa4ilWMVd5z9yxFjQy8T6r12IFMKgZo-fIw")

supabase: Client | None = None
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Cliente Supabase inicializado com sucesso.")
except Exception as e:
    print(f"Erro ao inicializar o cliente Supabase: {e}")

def get_supabase_client() -> Client:
    """Retorna a instância do cliente Supabase."""
    if supabase is None:
        raise ConnectionError("Cliente Supabase não inicializado.")
    return supabase

