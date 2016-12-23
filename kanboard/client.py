# The MIT License (MIT)
#
# Copyright (c) 2016 Frederic Guillot
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

from kanboard import exceptions

try:
    from urllib import request as http
except ImportError:
    import urllib2 as http


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

    def __init__(self, url, username, password, auth_header='Authorization'):
        """
        Constructor

        Args:
            url: API url endpoint
            username: API username or real username
            password: API token or user password
            auth_header: API HTTP header

        """
        self._url = url
        self._username = username
        self._password = password
        self._auth_header = auth_header

    def __getattr__(self, name):
        def function(*args, **kwargs):
            return self.execute(method=self._to_camel_case(name), **kwargs)
        return function

    @staticmethod
    def _to_camel_case(snake_str):
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @staticmethod
    def _parse_response(response):
        try:
            body = json.loads(response.decode())

            if 'error' in body:
                message = body.get('error').get('message')
                raise exceptions.KanboardClientException(message)

            return body.get('result')
        except ValueError:
            return None

    def _do_request(self, headers, body):
        try:
            request = http.Request(self._url,
                                   headers=headers,
                                   data=json.dumps(body).encode())

            response = http.urlopen(request).read()
        except Exception as e:
            raise exceptions.KanboardClientException(str(e))
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
        headers = {
            self._auth_header: 'Basic {}'.format(credentials.decode()),
            'Content-Type': 'application/json',
        }

        return self._do_request(headers, payload)
