# The MIT License (MIT)
#
# Copyright (c) Frederic Guillot
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import asyncio
import unittest
from unittest import mock

import kanboard


class TestClient(unittest.TestCase):
    def setUp(self):
        self.url = "some api url"
        self.client = kanboard.Client(self.url, "username", "password")
        self.request, self.urlopen = self._create_mocks()

    def tearDown(self):
        self.client.close()

    def test_api_call(self):
        body = b'{"jsonrpc": "2.0", "result": true, "id": 123}'
        self.urlopen.return_value.read.return_value = body
        self.assertEqual(True, self.client.remote_procedure())
        self.request.assert_called_once_with(self.url, data=mock.ANY, headers=mock.ANY)

    def test_custom_auth_header(self):
        self.client._auth_header = "X-Auth-Header"
        body = b'{"jsonrpc": "2.0", "result": true, "id": 123}'
        self.urlopen.return_value.read.return_value = body
        self.assertEqual(True, self.client.remote_procedure())
        self.request.assert_called_once_with(self.url, data=mock.ANY, headers=mock.ANY)
        _, kwargs = self.request.call_args
        assert kwargs["headers"]["X-Auth-Header"] == "dXNlcm5hbWU6cGFzc3dvcmQ="

    def test_http_error(self):
        original = Exception("connection refused")
        self.urlopen.side_effect = original
        with self.assertRaises(kanboard.ClientError) as cm:
            self.client.remote_procedure()
        self.assertIs(cm.exception.__cause__, original)

    def test_empty_response_raises_client_error(self):
        self.urlopen.return_value.read.return_value = b""
        with self.assertRaises(kanboard.ClientError) as cm:
            self.client.remote_procedure()
        self.assertIn("Empty response", str(cm.exception))

    def test_json_parsing_failure(self):
        body = b"{invalid json}"
        self.urlopen.return_value.read.return_value = body
        with self.assertRaises(kanboard.ClientError) as cm:
            self.client.remote_procedure()
        self.assertIn("Failed to parse JSON response", str(cm.exception))
        self.assertIsInstance(cm.exception.__cause__, ValueError)

    def test_application_error(self):
        body = b'{"jsonrpc": "2.0", "error": {"code": -32603, "message": "Internal error"}, "id": 123}'
        self.urlopen.return_value.read.return_value = body

        with self.assertRaises(kanboard.ClientError, msg="Internal error"):
            self.client.remote_procedure()

    def test_application_error_non_dict(self):
        body = b'{"jsonrpc": "2.0", "error": "Something went wrong", "id": 123}'
        self.urlopen.return_value.read.return_value = body

        with self.assertRaises(kanboard.ClientError, msg="Something went wrong"):
            self.client.remote_procedure()

    def test_async_method_call_recognised(self):
        method_name = "some_method_async"
        result = self.client.is_async_method_name(method_name)
        self.assertTrue(result)

    def test_standard_method_call_recognised(self):
        method_name = "some_method"
        result = self.client.is_async_method_name(method_name)
        self.assertFalse(result)

    def test_method_name_extracted_from_async_name(self):
        expected_method_name = "some_method"
        async_method_name = expected_method_name + "_async"
        result = self.client.get_funcname_from_async_name(async_method_name)
        self.assertEqual(expected_method_name, result)

    def test_async_call_returns_result(self):
        body = b'{"jsonrpc": "2.0", "result": 42, "id": 123}'
        self.urlopen.return_value.read.return_value = body
        loop = self.client._event_loop
        result = loop.run_until_complete(self.client.my_method_async())
        self.assertEqual(42, result)

    def test_custom_event_loop(self):
        custom_loop = asyncio.new_event_loop()
        try:
            client = kanboard.Client(self.url, "username", "password", loop=custom_loop)
            self.assertIs(client._event_loop, custom_loop)
            self.assertFalse(client._owns_event_loop)
        finally:
            custom_loop.close()

    def test_close_owned_event_loop(self):
        client = kanboard.Client(self.url, "username", "password")
        if client._owns_event_loop:
            self.assertFalse(client._event_loop.is_closed())
            client.close()
            self.assertTrue(client._event_loop.is_closed())

    def test_close_does_not_close_external_loop(self):
        custom_loop = asyncio.new_event_loop()
        try:
            client = kanboard.Client(self.url, "username", "password", loop=custom_loop)
            client.close()
            self.assertFalse(custom_loop.is_closed())
        finally:
            custom_loop.close()

    def test_context_manager(self):
        with kanboard.Client(self.url, "username", "password") as client:
            self.assertIsNotNone(client._event_loop)

    def test_custom_user_agent(self):
        with kanboard.Client(self.url, "username", "password", user_agent="CustomAgent/1.0") as client:
            body = b'{"jsonrpc": "2.0", "result": true, "id": 123}'
            self.urlopen.return_value.read.return_value = body
            client.remote_procedure()
            _, kwargs = self.request.call_args
            self.assertEqual("CustomAgent/1.0", kwargs["headers"]["User-Agent"])

    def test_default_user_agent(self):
        body = b'{"jsonrpc": "2.0", "result": true, "id": 123}'
        self.urlopen.return_value.read.return_value = body
        self.client.remote_procedure()
        _, kwargs = self.request.call_args
        self.assertEqual("Kanboard Python API Client", kwargs["headers"]["User-Agent"])

    @mock.patch("ssl.create_default_context")
    def test_insecure_disables_ssl_verification(self, mock_ssl_context):
        with kanboard.Client(self.url, "username", "password", insecure=True) as client:
            ctx = mock_ssl_context.return_value
            body = b'{"jsonrpc": "2.0", "result": true, "id": 123}'
            self.urlopen.return_value.read.return_value = body
            client.remote_procedure()
            self.assertFalse(ctx.check_hostname)
            self.assertEqual(ctx.verify_mode, __import__("ssl").CERT_NONE)

    @mock.patch("ssl.create_default_context")
    def test_ignore_hostname_verification(self, mock_ssl_context):
        with kanboard.Client(self.url, "username", "password", ignore_hostname_verification=True) as client:
            ctx = mock_ssl_context.return_value
            body = b'{"jsonrpc": "2.0", "result": true, "id": 123}'
            self.urlopen.return_value.read.return_value = body
            client.remote_procedure()
            self.assertFalse(ctx.check_hostname)

    @mock.patch("ssl.create_default_context")
    def test_cafile_passed_to_ssl_context(self, mock_ssl_context):
        with kanboard.Client(self.url, "username", "password", cafile="/path/to/ca.pem") as client:
            body = b'{"jsonrpc": "2.0", "result": true, "id": 123}'
            self.urlopen.return_value.read.return_value = body
            client.remote_procedure()
            mock_ssl_context.assert_called_once_with(cafile="/path/to/ca.pem")

    @staticmethod
    def _create_mocks():
        request_patcher = mock.patch("urllib.request.Request")
        urlopen_patcher = mock.patch("urllib.request.urlopen")
        return request_patcher.start(), urlopen_patcher.start()
