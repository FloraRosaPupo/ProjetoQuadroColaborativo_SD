"""Um emissor por conexão, com parada cooperativa e reconexão."""
import json
import logging
import os
import threading
from client.services.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)
WS_URL = os.environ.get("WHITEBOARD_WS_URL", "wss://whiteboard-core-oxk7.onrender.com")

def send_data(ws, stop, client_factory=get_supabase_client, interval=10):
    while not stop.is_set():
        try:
            response = client_factory().table("whiteboard_sessions").select("*", count="exact").execute()
            if stop.is_set():
                return
            ws.send(json.dumps({"serverId": "main-server-x", "name": "Servidor Grupo 11",
                                "roomCount": 1, "userCount": response.count, "status": "online"}))
        except Exception:
            logger.exception("Falha ao consultar ou enviar métricas do quadro")
        stop.wait(interval)

class WebSocketWorker:
    def __init__(self, url=WS_URL):
        self.url = url
        self.stopped = threading.Event()
        self.connection = None
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()
        return self

    def stop(self):
        self.stopped.set()
        if self.connection is not None:
            self.connection.close()

    def _run(self):
        import websocket
        while not self.stopped.is_set():
            connection_stop = threading.Event()
            sender = None

            def on_open(ws):
                nonlocal sender
                if self.stopped.is_set():
                    ws.close()
                    return
                sender = threading.Thread(target=send_data, args=(ws, connection_stop), daemon=True)
                sender.start()

            self.connection = websocket.WebSocketApp(
                self.url, on_open=on_open,
                on_close=lambda *_: connection_stop.set(),
                on_error=lambda _ws, error: logger.warning("Erro WebSocket: %s", error))
            try:
                if not self.stopped.is_set():
                    self.connection.run_forever()
            except Exception:
                logger.exception("Conexão WebSocket interrompida")
            finally:
                connection_stop.set()
                if sender is not None:
                    sender.join()
                self.connection = None
            self.stopped.wait(30)

def start_ws_client():
    return WebSocketWorker().start()
