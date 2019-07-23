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

import json
import base64
import aiohttp
import asyncio
import ssl

from kanboard import exceptions


DEFAULT_AUTH_HEADER = 'Authorization'
ASYNC_FUNCNAME_MARKER = "_async"


class Kanboard(object):
    """
    Kanboard API client

    Example:

        from kanboard import Kanboard

        kb = Kanboard(url="http://localhost/jsonrpc.php",
                      username="jsonrpc",
                      password="your_api_token")

        project_id = kb.create_project(name="My project")

    """

    def __init__(self, url, username, password, auth_header=DEFAULT_AUTH_HEADER, cafile=None, loop=asyncio.get_event_loop()):
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
        if(self.is_async_method_name(name)):
            async def function(*args, **kwargs):
                return await self.execute(method=self._to_camel_case(self.get_funcname_from_async_name(name)), **kwargs)
            return function
        else:
            def function(*args, **kwargs):
                return self._event_loop.run_until_complete(self.execute(method=self._to_camel_case(name), **kwargs))
            return function

    @staticmethod
    def is_async_method_name(funcname):
        return funcname.endswith(ASYNC_FUNCNAME_MARKER)

    @staticmethod
    def get_funcname_from_async_name(funcname):
        return funcname[:len(funcname)-len(ASYNC_FUNCNAME_MARKER)]

    @staticmethod
    def _to_camel_case(snake_str):
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @staticmethod
    def _parse_response(response):
        try:
            body = response

            if 'error' in body:
                message = body.get('error').get('message')
                raise exceptions.KanboardClientException(message)

            return body.get('result')
        except ValueError:
            return None

    async def _do_request(self, headers, body):
        try:
            ssl_context = ssl.create_default_context(cafile=self._cafile)
            # This creates a per-request ClientSession,
            # against the recommendations of the aiohttp authors.
            # It's a pragmatic choice wrt how the code was before introducing
            # asynchronous calls, in that it doesn't make performance worse.
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        self._url,
                        headers=headers,
                        data=json.dumps(body).encode(),
                        ssl=ssl_context) as response:
                    return self._parse_response(await response.json())
        except Exception as e:
            raise exceptions.KanboardClientException(str(e))

    async def execute(self, method, **kwargs):
        """
        Call remote API procedure

        Args:
            method: Procedure name
            kwargs: Procedure named arguments

        Returns:
            Procedure result

        Raises:
            urllib2.HTTPError: Any HTTP error (Python 2)
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

        return await self._do_request(headers, payload)
