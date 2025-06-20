# -*- coding: utf-8 -*-
"""Módulo de autenticação usando Supabase."""

from client.services.supabase_client import get_supabase_client
from PySide6.QtWidgets import QMessageBox

# Variável global para armazenar informações do usuário logado
current_user = None

def login(email, password):
    """Tenta autenticar um usuário com email e senha via Supabase."""
    global current_user
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            current_user = response.user
            print(f"Usuário {email} logado com sucesso. ID: {current_user.id}")
            return True
        else:
            print(f"Falha no login para {email}: Usuário ou senha inválidos.")
            return False
    except Exception as e:
        print(f"Erro durante o login Supabase para {email}: {e}")
        error_message = str(e)
        if "Invalid login credentials" in error_message:
            QMessageBox.warning(None, "Erro de Login", "Email ou senha inválidos.")
        else:
            QMessageBox.critical(None, "Erro de Login", f"Ocorreu um erro inesperado: {error_message}")
        return False

def signup(email, password):
    """Registra um novo usuário com email e senha via Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            print(f"Usuário {email} registrado com sucesso. Verifique seu email para confirmação.")
            QMessageBox.information(None, "Registro Concluído",
                                    "Registro realizado com sucesso! Verifique seu email para confirmar a conta antes de fazer login.")
            return True
        elif response.error:
             print(f"Falha no registro para {email}: {response.error.message}")
             QMessageBox.warning(None, "Erro de Registro", f"Não foi possível registrar: {response.error.message}")
             return False
        else:
            print(f"Falha no registro para {email}: Resposta inesperada do Supabase.")
            QMessageBox.warning(None, "Erro de Registro", "Ocorreu um erro inesperado durante o registro.")
            return False
    except Exception as e:
        print(f"Erro durante o signup Supabase para {email}: {e}")
        QMessageBox.critical(None, "Erro de Registro", f"Ocorreu um erro inesperado: {e}")
        return False

def get_current_user():
    """Retorna o objeto do usuário atualmente logado."""
    return current_user

def logout():
    """Desloga o usuário atual."""
    global current_user
    current_user = get_current_user()
    try:
        supabase = get_supabase_client()
         # Deleta todas as formas dessa sessão
        supabase.table("whiteboard_shapes").delete().eq("user_id", current_user.id).execute()
        print("✅ Dados apagados do Supabase.")
        # Opcional: também remove o registro da sessão
        supabase.table("whiteboard_sessions").delete().eq("id", current_user.id).execute()
        supabase.auth.sign_out()
        current_user = None
        print("Usuário deslogado com sucesso.")
        return True
    except Exception as e:
        print(f"Erro durante o logout Supabase: {e}")
        return False