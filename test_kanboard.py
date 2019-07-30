# The MIT License (MIT)
#
# Copyright (c) 2016-2018 Frederic Guillot
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

import unittest
from unittest import mock
import types
import warnings

import kanboard


class TestClient(unittest.TestCase):

    def setUp(self):
        self.url = 'some api url'
        self.client = kanboard.Client(self.url, 'username', 'password')
        self.request, self.urlopen = self._create_mocks()

    def ignore_warnings(test_func):
        def do_test(self, *args, **kwargs):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                test_func(self, *args, **kwargs)
        return do_test

    def test_api_call(self):
        body = b'{"jsonrpc": "2.0", "result": true, "id": 123}'
        self.urlopen.return_value.read.return_value = body
        self.assertEqual(True, self.client.remote_procedure())
        self.request.assert_called_once_with(self.url,
                                             data=mock.ANY,
                                             headers=mock.ANY)

    def test_custom_auth_header(self):
        self.client._auth_header = 'X-Auth-Header'
        body = b'{"jsonrpc": "2.0", "result": true, "id": 123}'
        self.urlopen.return_value.read.return_value = body
        self.assertEqual(True, self.client.remote_procedure())
        self.request.assert_called_once_with(self.url,
                                             data=mock.ANY,
                                             headers=mock.ANY)
        _, kwargs = self.request.call_args
        assert kwargs['headers']['X-Auth-Header'] == 'dXNlcm5hbWU6cGFzc3dvcmQ='

    def test_http_error(self):
        self.urlopen.side_effect = Exception()
        with self.assertRaises(kanboard.ClientError):
            self.client.remote_procedure()

    def test_application_error(self):
        body = b'{"jsonrpc": "2.0", "error": {"code": -32603, "message": "Internal error"}, "id": 123}'
        self.urlopen.return_value.read.return_value = body

        with self.assertRaises(kanboard.ClientError, msg='Internal error'):
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

    # suppress a RuntimeWarning because coro is not awaited
    # this is done on purpose
    @ignore_warnings
    def test_async_call_generates_coro(self):
        method = self.client.my_method_async()
        self.assertIsInstance(method, types.CoroutineType)

    @staticmethod
    def _create_mocks():
        request_patcher = mock.patch('urllib.request.Request')
        urlopen_patcher = mock.patch('urllib.request.urlopen')
        return request_patcher.start(), urlopen_patcher.start()
