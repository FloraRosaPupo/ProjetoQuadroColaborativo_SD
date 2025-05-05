# -*- coding: utf-8 -*-
"""Funções para integração com o sistema 'core' centralizador."""

from client.services.supabase_client import get_supabase_client
# list_sessions já foi corrigido para usar a tabela correta
from client.services.session_manager import list_sessions
from PySide6.QtWidgets import QMessageBox

# Define o nome correto da tabela
SHAPES_TABLE = "whiteboard_shapes"

def get_all_sessions_info():
    """Retorna informações sobre todas as sessões existentes.

    Esta função busca no banco de dados (via session_manager) e retorna
    uma lista de dicionários, cada um representando uma sessão.
    Formato esperado pelo Core: Lista de {id, name, created_at, amount_users}.
    """
    print("Core Integration: Buscando informações de todas as sessões...")
    try:
        # list_sessions já usa a tabela correta e retorna as colunas disponíveis
        sessions = list_sessions()
        # print(f"Core Integration: {len(sessions)} sessões encontradas.")
        return sessions
    except Exception as e:
        print(f"Core Integration: Erro ao buscar sessões: {e}")
        return {"error": f"Erro ao buscar sessões: {e}"}

def get_active_users_count(session_id):
    """Estima ou retorna a contagem de usuários ativos em uma sessão.

    Implementação atual (estimativa):
    Conta usuários distintos que desenharam algo na sessão.
    """
    print(f"Core Integration: Estimando contagem de usuários para sessão {session_id}...")
    try:
        supabase = get_supabase_client()

        # Usa o nome correto da tabela
        response_users = supabase.table(SHAPES_TABLE)\
                                .select("user_id")\
                                .eq("session_id", session_id)\
                                .execute()

        if response_users.data:
            distinct_users = set(item['user_id'] for item in response_users.data if item.get('user_id'))
            count = len(distinct_users)
            # print(f"Core Integration: {count} usuários distintos encontrados na sessão {session_id}.")
            return {"session_id": session_id, "active_users_count": count}
        elif hasattr(response_users, 'error') and response_users.error:
            raise Exception(response_users.error.message)
        else:
            # Nenhuma forma na sessão, logo 0 usuários ativos (por esta métrica)
            # print(f"Core Integration: Nenhuma forma (e usuário) encontrada na sessão {session_id}.")
            return {"session_id": session_id, "active_users_count": 0}

    except Exception as e:
        print(f"Core Integration: Erro ao contar usuários na sessão {session_id}: {e}")
        return {"error": f"Erro ao contar usuários na sessão {session_id}: {e}"}

