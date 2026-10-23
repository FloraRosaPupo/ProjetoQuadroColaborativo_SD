import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from client.services.core_integration import count_distinct_users, get_active_users_count
from ws_client import send_data

class ServiceTests(unittest.TestCase):
    def test_distinct_users_and_missing_values(self):
        self.assertEqual(count_distinct_users([{"user_id":"a"},{"user_id":"a"},{"user_id":"b"},{}, {"user_id":None}]), 2)

    def test_empty_session(self):
        client = Mock()
        client.table.return_value.select.return_value.eq.return_value.execute.return_value = SimpleNamespace(data=[],error=None)
        self.assertEqual(get_active_users_count("room",client), {"session_id":"room","active_users_count":0})

    def test_backend_error_is_not_reported_as_empty_session(self):
        client = Mock()
        client.table.side_effect = ConnectionError("offline")
        self.assertIn("offline", get_active_users_count("room",client)["error"])

    def test_sender_survives_query_failure_and_stops(self):
        stop=threading.Event()
        def unavailable():
            stop.set()
            raise ConnectionError("offline")
        ws=Mock()
        with self.assertLogs("ws_client",level="ERROR"):
            send_data(ws,stop,client_factory=unavailable,interval=0)
        ws.send.assert_not_called()

    def test_sender_stops_after_send(self):
        stop=threading.Event(); ws=Mock(); ws.send.side_effect=lambda _:stop.set()
        client=Mock(); client.table.return_value.select.return_value.execute.return_value=SimpleNamespace(count=2)
        send_data(ws,stop,client_factory=lambda:client,interval=0)
        self.assertEqual(ws.send.call_count,1)

if __name__ == "__main__": unittest.main()
