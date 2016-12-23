import mock
import sys
import unittest

from kanboard import client
from kanboard import exceptions


class TestKanboard(unittest.TestCase):

    def setUp(self):
        self.url = 'some api url'
        self.client = client.Kanboard(self.url, 'username', 'password')
        self.request, self.urlopen = self._create_mocks()

    def test_api_call(self):
        body = b'{"jsonrpc": "2.0", "result": true, "id": 123}'
        self.urlopen.return_value.read.return_value = body
        self.assertEquals(True, self.client.remote_procedure())
        self.request.assert_called_once_with(self.url,
                                             data=mock.ANY,
                                             headers=mock.ANY)

    def test_http_error(self):
        self.urlopen.side_effect = Exception()
        with self.assertRaises(exceptions.KanboardClientException):
            self.client.remote_procedure()

    def test_application_error(self):
        body = b'{"jsonrpc": "2.0", "error": {"code": -32603, "message": "Internal error"}, "id": 123}'
        self.urlopen.return_value.read.return_value = body

        with self.assertRaises(exceptions.KanboardClientException, msg='Internal error'):
            self.client.remote_procedure()

    @staticmethod
    def _create_mocks():
        if sys.version_info[0] < 3:
            urlopen_patcher = mock.patch('urllib2.urlopen')
            request_patcher = mock.patch('urllib2.Request')
        else:
            request_patcher = mock.patch('urllib.request.Request')
            urlopen_patcher = mock.patch('urllib.request.urlopen')

        return request_patcher.start(), urlopen_patcher.start()
