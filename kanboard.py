# The MIT License (MIT)
#
# Copyright (c) 2016-2019 Frederic Guillot
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

import json
import base64
import functools
import asyncio
from urllib import request as http


DEFAULT_AUTH_HEADER = 'Authorization'
ASYNC_FUNCNAME_MARKER = "_async"


class ClientError(Exception):
    pass


class Client:
    """
    Kanboard API client

    Example:

        from kanboard import Client

        kb = Client(url="http://localhost/jsonrpc.php",
                    username="jsonrpc",
                    password="your_api_token")

        project_id = kb.create_project(name="My project")

    """

    def __init__(self,
                 url,
                 username,
                 password,
                 auth_header=DEFAULT_AUTH_HEADER,
                 cafile=None,
                 loop=asyncio.get_event_loop()):
        """
        Constructor

        Args:
            url: API url endpoint
            username: API username or real username
            password: API token or user password
            auth_header: API HTTP header
            cafile: path to a custom CA certificate
            loop: an asyncio event loop. Default: asyncio.get_event_loop()
        """
        self._url = url
        self._username = username
        self._password = password
        self._auth_header = auth_header
        self._cafile = cafile
        self._event_loop = loop

    def __getattr__(self, name):
        if self.is_async_method_name(name):
            async def function(*args, **kwargs):
                return await self._event_loop.run_in_executor(
                    None,
                    functools.partial(
                        self.execute,
                        method=self._to_camel_case(self.get_funcname_from_async_name(name)), **kwargs))
            return function
        else:
            def function(*args, **kwargs):
                return self.execute(method=self._to_camel_case(name), **kwargs)
            return function

    @staticmethod
    def is_async_method_name(funcname):
        return funcname.endswith(ASYNC_FUNCNAME_MARKER)

    @staticmethod
    def get_funcname_from_async_name(funcname):
        return funcname[:len(funcname) - len(ASYNC_FUNCNAME_MARKER)]

    @staticmethod
    def _to_camel_case(snake_str):
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @staticmethod
    def _parse_response(response):
        try:
            body = json.loads(response.decode(errors='ignore'))

            if 'error' in body:
                message = body.get('error').get('message')
                raise ClientError(message)

            return body.get('result')
        except ValueError:
            return None

    def _do_request(self, headers, body):
        try:
            request = http.Request(self._url,
                                   headers=headers,
                                   data=json.dumps(body).encode())
            if self._cafile:
                response = http.urlopen(request, cafile=self._cafile).read()
            else:
                response = http.urlopen(request).read()
        except Exception as e:
            raise ClientError(str(e))
        return self._parse_response(response)

    def execute(self, method, **kwargs):
        """
        Call remote API procedure

        Args:
            method: Procedure name
            kwargs: Procedure named arguments

        Returns:
            Procedure result

        Raises:
            urllib.error.HTTPError: Any HTTP error (Python 3)
        """
        payload = {
            'id': 1,
            'jsonrpc': '2.0',
            'method': method,
            'params': kwargs
        }

        credentials = base64.b64encode('{}:{}'.format(self._username, self._password).encode())
        auth_header_prefix = 'Basic ' if self._auth_header == DEFAULT_AUTH_HEADER else ''
        headers = {
            self._auth_header: auth_header_prefix + credentials.decode(),
            'Content-Type': 'application/json',
        }

        return self._do_request(headers, payload)
