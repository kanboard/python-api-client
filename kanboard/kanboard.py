from __future__ import print_function

import base64
import json
import sys


try:
    import requests
except ImportError:
    print('kanboard-apy-python needs the requests library', file=sys.stderr)
    sys.exit(-1)

class Kanboard(object):
    """
    Kanboard API client

    Example:

        from kanboard import Kanboard

        kb = Kanboard("http://localhost/jsonrpc.php", "jsonrpc", "your_api_token")
        project_id = kb.create_project(name="My project")

    """

    def __init__(self, url, username, password, auth_header=None,
                 http_username=None, http_password=None, verify=True, proxies={}):
        """
        Constructor

        Args:
            url: API url endpoint
            username: API username or real username
            password: API token or user password
            auth_header: API HTTP Header
            http_username: Username for HTTP authentication
            http_password: Password for HTTP authentication
            proxies: Dictionary containing proxy settings
            verify: Whether to verify the SSL certificate

        """
        self.url = url
        self.username = username
        self.password = password
        self.auth_header = auth_header
        self.http_username = http_username
        self.http_password = http_password
        self.verify = verify
        self.proxies = proxies
        self.auth = None
        if self.http_username:
            self.auth = requests.auth.HTTPBasicAuth(self.http_username,
                                                    self.http_password)
        if not self.auth_header:
            self.auth = requests.auth.HTTPBasicAuth(self.username,
                                                    self.password)

    def __getattr__(self, name):
        """
        Call dynamically the API procedure

        Arg:
            name: method name
        """
        def function(*args, **kwargs):
            return self.call(method=self._to_camel_case(name), **kwargs)
        return function

    def _to_camel_case(self, snake_str):
        components = snake_str.split('_')
        return components[0] + "".join(x.title() for x in components[1:])

    def _parse_response(self, response):
        try:
            body = json.loads(response.read().decode('utf8'))
            return body.get("result")
        except:
            return False

    def call(self, method, **kwargs):
        """
        Call remote API procedure

        Args:
            method: Procedure name
            kwargs: Procedure named arguments

        Returns:
            Procedure result

        Raises:
            requests.exceptions.RequestException
        """
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": method,
            "params": kwargs
        }

        headers = None
        if self.auth_header:
            headers = {self.auth_header: base64.b64encode("{0}:{1}".format(self.username,
                                                                           self.password).encode())}
        if not self.verify:
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning)
        request = requests.post(self.url, headers=headers, json=payload, proxies=self.proxies,
                                verify=self.verify, auth=self.auth)
        if request.status_code == 200:
            return request.json()["result"]
        else:
            return None
