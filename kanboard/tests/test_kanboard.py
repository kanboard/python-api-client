import mock
import sys
import unittest

from kanboard import kanboard


class TestKanboard(unittest.TestCase):

    def setUp(self):
        self.url = 'some api url'
        self.client = kanboard.Kanboard(self.url, 'username', 'password')
        self.request, self.urlopen = self._create_mocks()

    def test_api_call(self):
        body = b'{"jsonrpc": "2.0", "result": true, "id": 123}'
        self.urlopen.return_value.read.return_value = body
        self.assertEquals(True, self.client.remote_procedure())
        self.request.assert_called_once_with(self.url,
                                             data=mock.ANY,
                                             headers=mock.ANY)

    @staticmethod
    def _create_mocks():
        if sys.version_info[0] < 3:
            urlopen_patcher = mock.patch('urllib2.urlopen')
            request_patcher = mock.patch('urllib2.Request')
        else:
            request_patcher = mock.patch('urllib.request.Request')
            urlopen_patcher = mock.patch('urllib.request.urlopen')

        return request_patcher.start(), urlopen_patcher.start()
