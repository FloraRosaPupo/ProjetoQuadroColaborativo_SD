# -*- coding: utf-8 -*-
"""Módulo para gerenciamento de sessões de desenho colaborativo."""

from client.services.supabase_client import get_supabase_client
from PySide6.QtWidgets import QMessageBox
import uuid # Para gerar IDs de sessão, embora o Supabase possa fazer isso

# Define os nomes corretos das tabelas
SESSIONS_TABLE = "whiteboard_sessions"
SHAPES_TABLE = "whiteboard_shapes"

def create_session(user_id, name="Nova Sessão"):
    """Cria uma nova sessão de desenho no Supabase.

    Ajustado para usar a tabela 'whiteboard_sessions' e remover 'created_by'
    conforme schema do usuário.
    """
    try:
        supabase = get_supabase_client()
        session_data = {
            'name': name,
            # 'created_by': str(user_id) # Removido, coluna não existe na tabela do usuário
            # A coluna 'amount_users' não será preenchida aqui, talvez por trigger ou outra lógica
        }
        # Usa o nome correto da tabela
        response = supabase.table(SESSIONS_TABLE).insert(session_data).execute()

        if response.data:
            new_session = response.data[0]
            print(f"Sessão álbum '{new_session.get('name')}' criada com ID: {new_session.get('id')}")
            return new_session # Retorna os dados da sessão criada
        elif hasattr(response, 'error') and response.error:
             raise Exception(response.error.message)
        else:
            raise Exception("Resposta inesperada ao criar sessão.")

    except Exception as e:
        print(f"Erro ao criar sessão no Supabase: {e}")
        QMessageBox.critical(None, "Erro ao Criar Sessão", f"Não foi possível criar a sessão.\nErro: {e}")
        return None

def list_sessions():
    """Lista todas as sessões de desenho disponíveis.

    Ajustado para usar 'whiteboard_sessions' e remover 'created_by' da seleção.
    """
    try:
        supabase = get_supabase_client()
        # Usa o nome correto da tabela e ajusta colunas selecionadas
        response = supabase.table(SESSIONS_TABLE).select("id, name, created_at, amount_users").order("created_at", desc=True).execute()

        if response.data:
            # print("Sessões encontradas:", response.data)
            return response.data
        elif hasattr(response, 'error') and response.error:
             raise Exception(response.error.message)
        else:
            # Pode não haver sessões, o que não é um erro
            print("Nenhuma sessão encontrada.")
            return []

    except Exception as e:
        print(f"Erro ao listar sessões do Supabase: {e}")
        QMessageBox.critical(None, "Erro ao Listar Sessões", f"Não foi possível buscar as sessões.\nErro: {e}")
        return []

def get_session_shapes(session_id):
    """Busca todas as formas associadas a uma sessão específica.

    Ajustado para usar 'whiteboard_shapes'.
    """
    try:
        supabase = get_supabase_client()
        # Usa o nome correto da tabela
        response = supabase.table(SHAPES_TABLE)\
                           .select("*")\
                           .eq("session_id", session_id)\
                           .order("created_at", desc=False)\
                           .execute()

        if response.data:
            # print(f"Formas encontradas para a sessão {session_id}:", len(response.data))
            return response.data
        elif hasattr(response, 'error') and response.error:
            raise Exception(response.error.message)
        else:
            # Nenhuma forma encontrada para esta sessão
            return []

    except Exception as e:
        print(f"Erro ao buscar formas da sessão {session_id}: {e}")
        QMessageBox.critical(None, "Erro ao Carregar Desenhos", f"Não foi possível carregar os desenhos da sessão.\nErro: {e}")
        return []

# Adicionar funções para adicionar/remover usuários de sessões pode ser necessário
# dependendo da lógica de permissão e colaboração.

