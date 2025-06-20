# ws_client.py
from client.services.supabase_client import get_supabase_client
import websocket
import threading
import json
import time

WS_URL = "wss://whiteboard-core.onrender.com"

def send_data(ws):
    supabase = get_supabase_client()
    while True:
        resposta = supabase.table("whiteboard_sessions").select("*", count="exact").execute()
        userCount = resposta.count
        data = {
            "serverId": "main-server-x",
            "name": "Servidor Grupo 11",
            "roomCount": 1,
            "userCount": userCount,
            "status": "online"
        }
        try:
            ws.send(json.dumps(data))
            print("[→] Dados enviados:", data)
        except Exception as e:
            print("[x] Falha ao enviar:", e)
        time.sleep(10)

def on_open(ws):
    print("[✓] Conectado ao whiteboard-core")
    threading.Thread(target=send_data, args=(ws,), daemon=True).start()

def on_error(ws, error):
    print("[x] Erro WebSocket:", error)

def on_close(ws, close_status_code, close_msg):
    print("[!] Conexão fechada:", close_status_code, close_msg)

def start_ws_client():
    def _run():
        while True:
            ws = websocket.WebSocketApp(
                WS_URL,
                on_open=on_open,
                on_close=on_close,
                on_error=on_error
            )
            ws.run_forever()
            print("[!] Tentando reconectar em 30s...")
            time.sleep(30)
    threading.Thread(target=_run, daemon=True).start()
