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

import asynctest
import types
import warnings
import unittest
from unittest import mock

from kanboard import client
from kanboard import exceptions


class TestKanboard(unittest.TestCase):

    def setUp(self):
        self.url = 'http://someapiurl'
        self.client = client.Kanboard(self.url, 'username', 'password')

    # https://blog.sneawo.com/blog/2019/05/22/mock-aiohttp-request-in-unittests
    def set_post_mock_response(self, mock_post, status, json_data):
        mock_post.return_value.__aenter__.return_value.status = status
        mock_post.return_value.__aenter__.return_value.json = asynctest.CoroutineMock(return_value=json_data)

    def ignore_warnings(test_func):
        def do_test(self, *args, **kwargs):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                test_func(self, *args, **kwargs)
        return do_test

    @asynctest.patch("aiohttp.ClientSession.post")
    def test_api_call(self, mock_post):
        body = {"jsonrpc": "2.0", "result": True, "id": 123}
        self.set_post_mock_response(mock_post, 200, body)
        result = self.client.remote_procedure()
        self.assertEqual(True, result)
        mock_post.assert_called_once_with(self.url,
                                          data=mock.ANY,
                                          headers=mock.ANY,
                                          ssl=mock.ANY)

    @asynctest.patch("aiohttp.ClientSession.post")
    def test_custom_auth_header(self, mock_post):
        self.client._auth_header = 'X-Auth-Header'
        body = {"jsonrpc": "2.0", "result": True, "id": 123}
        self.set_post_mock_response(mock_post, 200, body)
        self.assertEqual(True, self.client.remote_procedure())
        mock_post.assert_called_once_with(self.url,
                                          data=mock.ANY,
                                          headers=mock.ANY,
                                          ssl=mock.ANY)
        _, kwargs = mock_post.call_args
        assert kwargs['headers']['X-Auth-Header'] == 'dXNlcm5hbWU6cGFzc3dvcmQ='

    @asynctest.patch("aiohttp.ClientSession.post")
    def test_http_error(self, mock_post):
        mock_post.side_effect = Exception()
        with self.assertRaises(exceptions.KanboardClientException):
            self.client.remote_procedure()

    @asynctest.patch("aiohttp.ClientSession.post")
    def test_application_error(self, mock_post):
        body = {"jsonrpc": "2.0", "error": {"code": -32603, "message": "Internal error"}, "id": 123}
        self.set_post_mock_response(mock_post, 200, body)

        with self.assertRaises(exceptions.KanboardClientException, msg='Internal error'):
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
