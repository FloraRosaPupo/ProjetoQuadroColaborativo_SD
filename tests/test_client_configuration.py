import base64
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from client.services.supabase_client import get_supabase_client


def example_jwt(role):
    payload = base64.urlsafe_b64encode(json.dumps({'role': role}).encode()).decode().rstrip('=')
    return 'header.' + payload + '.example-signature'


class ClientConfigurationTests(unittest.TestCase):
    def setUp(self):
        get_supabase_client.cache_clear()
        self.addCleanup(get_supabase_client.cache_clear)

    def test_privileged_or_invalid_keys_never_reach_sdk(self):
        for key in [example_jwt('service_role'), 'sb_secret_example', example_jwt('authenticated'), 'invalid', 'x.@@@.y']:
            with self.subTest(key_type=key.split('.')[0]):
                create = Mock()
                with patch.dict('os.environ', {'SUPABASE_URL': 'https://example.supabase.co', 'SUPABASE_KEY': key}), patch.dict('sys.modules', {'supabase': SimpleNamespace(create_client=create)}):
                    with self.assertRaises(ValueError) as error:
                        get_supabase_client()
                    self.assertNotIn(key, str(error.exception))
                    create.assert_not_called()

    def test_public_keys_are_passed_to_sdk_and_client_is_cached(self):
        for key in [example_jwt('anon'), 'sb_publishable_example']:
            get_supabase_client.cache_clear()
            create = Mock()
            with patch.dict('os.environ', {'SUPABASE_URL': 'https://example.supabase.co', 'SUPABASE_KEY': key}), patch.dict('sys.modules', {'supabase': SimpleNamespace(create_client=create)}):
                self.assertIs(get_supabase_client(), get_supabase_client())
                create.assert_called_once_with('https://example.supabase.co', key)

    def test_missing_configuration_does_not_create_client(self):
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError):
                get_supabase_client()
