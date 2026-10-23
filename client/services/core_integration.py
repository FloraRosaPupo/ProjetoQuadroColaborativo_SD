"""Consulta de participantes que desenharam; não representa presença online."""
from client.services.supabase_client import get_supabase_client

SHAPES_TABLE = "whiteboard_shapes"

def count_distinct_users(shapes):
    return len({shape["user_id"] for shape in shapes if shape.get("user_id")})

def get_active_users_count(session_id, client=None):
    try:
        client = client if client is not None else get_supabase_client()
        response = client.table(SHAPES_TABLE).select("user_id").eq("session_id", session_id).execute()
        error = getattr(response, "error", None)
        if error:
            raise RuntimeError(getattr(error, "message", str(error)))
        return {"session_id": session_id, "active_users_count": count_distinct_users(response.data or [])}
    except Exception as error:
        return {"error": f"Erro ao contar usuários na sessão {session_id}: {error}"}
