import json
import base64

try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen


class Kanboard(object):
    """
    Kanboard API client

    Example:

        from kanboard import Kanboard

        kb = Kanboard("http://localhost/jsonrpc.php", "jsonrpc", "your_api_token")
        project_id = kb.create_project(name="My project")

    """

    def __init__(self, url, username, password, auth_header="Authorization"):
        """
        Constructor

        Args:
            url: API url endpoint
            username: API username or real username
            password: API token or user password
            auth_header: API HTTP header

        """
        self.url = url
        self.username = username
        self.password = password
        self.auth_header = auth_header

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
            urllib2.HTTPError: Any HTTP error (Python 2)
            urllib.error.HTTPError: Any HTTP error (Python 3)
        """
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": method,
            "params": kwargs
        }

        credentials = "{0}:{1}".format(self.username, self.password).encode()
        headers = {
            self.auth_header: b"Basic " + base64.b64encode(credentials),
            "Content-Type": 'application/json'
        }

        request = Request(self.url, headers=headers, data=json.dumps(payload).encode("utf8"))
        return self._parse_response(urlopen(request))
