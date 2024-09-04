import errno
try:
    from httplib import BadStatusLine, LineTooLong, RemoteDisconnected
except ImportError:
    from http.client import BadStatusLine, LineTooLong, RemoteDisconnected

import unittest
import requests

from hamms import HammsServer, BASE_PORT, reactor
from hamms import __version__ as version

hs = HammsServer()
if not reactor.running:
    hs.start()

class TestEndpoints(unittest.TestCase):

    def test_5500(self):
        with self.assertRaises(requests.ConnectionError) as cm:
            requests.get('http://127.0.0.1:{port}'.format(port=BASE_PORT))
        self.assertIsInstance(cm.exception, requests.exceptions.ConnectionError)

    def test_5501(self):
        with self.assertRaises(requests.exceptions.ReadTimeout) as cm:
            url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+1)
            requests.get(url, timeout=0.001)

    def test_5502(self):
        with self.assertRaises(requests.exceptions.ConnectionError) as cm:
            url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+2)
            r = requests.get(url)

        self.assertIsInstance(cm.exception, requests.exceptions.ConnectionError)


    def test_5503(self):
        with self.assertRaises(requests.exceptions.ConnectionError) as cm:
            url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+3)
            requests.get(url)
        self.assertIsInstance(cm.exception, requests.exceptions.ConnectionError)


    def test_5504(self):
        url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+4)
        with self.assertRaises(requests.exceptions.ConnectionError) as cm:
            r = requests.get(url)
        self.assertIsInstance(cm.exception, requests.exceptions.ConnectionError)

    def test_5505(self):
        url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+4)
        with self.assertRaises(requests.exceptions.ConnectionError) as cm:
            r = requests.get(url)
        self.assertIsInstance(cm.exception, requests.exceptions.ConnectionError)


    def test_5506(self):
        with self.assertRaises(requests.exceptions.ReadTimeout) as cm:
            # Would need to wait 5 seconds to assert anything about this.
            url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+6)
            requests.get(url, timeout=0.001)

    def test_5507(self):
        # Would need to wait a few minutes to assert anything useful about this.
        # I'm sure Twisted has methods for advancing time, will have to read about
        # them later.
        with self.assertRaises(requests.exceptions.ReadTimeout) as cm:
            url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+7)
            requests.get(url, timeout=0.001)

    def test_5508(self):
        with self.assertRaises(requests.exceptions.ReadTimeout) as cm:
            url = 'http://127.0.0.1:{port}?sleep=0.002'.format(port=BASE_PORT+8)
            requests.get(url, timeout=0.001)

        url = 'http://127.0.0.1:{port}?sleep=0.001'.format(port=BASE_PORT+8)
        r = requests.get(url, timeout=0.02)
        self.assertEqual(r.status_code, 200)

    def test_5509(self):
        url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+9)
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)

        url = 'http://127.0.0.1:{port}?status=418'.format(port=BASE_PORT+9)
        r = requests.get(url)
        self.assertEqual(r.status_code, 418)

        url = 'http://127.0.0.1:{port}?status=503'.format(port=BASE_PORT+9)
        r = requests.get(url)
        self.assertEqual(r.status_code, 503)

    def test_5510(self):
        # Would need to wait 5 seconds to assert anything about this.
        url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+10)
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1)
        s.mount('http://', a)
        r = s.get(url)
        self.assertEqual(r.content, b'aaa')
        self.assertEqual(r.headers['Content-Length'], '3')

        r = s.get(url)
        self.assertEqual(r.content, b'aaa')
        self.assertEqual(r.headers['Content-Length'], '3')

    def test_5511(self):
        # Would need to wait 5 seconds to assert anything about this.
        with self.assertRaises(requests.ConnectionError) as cm:
            url = 'http://127.0.0.1:{port}?size={size}'.format(port=BASE_PORT+11,
                                                            size=1024*64)
            r = requests.get(url)
        self.assertIsInstance(cm.exception, requests.exceptions.ConnectionError)

        url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+11)
        r = requests.get(url)
        self.assertEqual(len(r.headers['Cookie']), 1024*63)

    def test_5512(self):
        url = 'http://127.0.0.1:{port}?tries=foo'.format(port=BASE_PORT+12)
        r = requests.get(url)
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.assertTrue('integer' in d['error'])

        url = 'http://127.0.0.1:{port}?key=hamms-test'.format(port=BASE_PORT+12)
        r = requests.get(url)
        self.assertEqual(r.status_code, 500)
        d = r.json()
        self.assertEqual(d['tries_remaining'], 2)
        self.assertEqual(d['key'], 'hamms-test')

        r = requests.get(url)
        self.assertEqual(r.status_code, 500)
        d = r.json()
        self.assertEqual(d['tries_remaining'], 1)

        otherkey_url = 'http://127.0.0.1:{port}?key=other-key'.format(port=BASE_PORT+12)
        r = requests.get(otherkey_url)
        self.assertEqual(r.status_code, 500)
        d = r.json()
        self.assertEqual(d['tries_remaining'], 2)

        url = 'http://127.0.0.1:{port}?key=hamms-test'.format(port=BASE_PORT+12)
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d['tries_remaining'], 0)

        url = 'http://127.0.0.1:{port}/counters?key=hamms-test&tries=7'.format(port=BASE_PORT+12)
        r = requests.post(url)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d['key'], 'hamms-test')
        self.assertEqual(d['tries_remaining'], 7)

        url = 'http://127.0.0.1:{port}/counters'.format(port=BASE_PORT+12)
        r = requests.post(url, data={'key': 'hamms-test', 'tries': 7})
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d['key'], 'hamms-test')
        self.assertEqual(d['tries_remaining'], 7)

        url = 'http://127.0.0.1:{port}?key=hamms-test'.format(port=BASE_PORT+12)
        r = requests.get(url)
        self.assertEqual(r.status_code, 500)
        d = r.json()
        self.assertEqual(d['tries_remaining'], 6)

        url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+12)
        r = requests.get(url)
        self.assertEqual(r.status_code, 500)
        d = r.json()
        self.assertEqual(d['key'], 'default')

        url = 'http://127.0.0.1:{port}?key=foo&tries=1'.format(port=BASE_PORT+12)
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d['key'], 'foo')

    def test_5513(self):
        url = 'http://127.0.0.1:{port}?failrate=1'.format(port=BASE_PORT+13)
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)

        success_url = 'http://127.0.0.1:{port}?failrate=0'.format(port=BASE_PORT+13)
        r = requests.get(success_url)
        self.assertEqual(r.status_code, 200)

    def test_5514(self):
        url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+14)
        r = requests.get(url, headers={'Accept': 'text/morse'})
        self.assertEqual(r.headers['content-type'], 'application/json')

        r = requests.get(url, headers={'Accept': 'application/json;q=0.3,text/morse;q=0.5'})
        self.assertEqual(r.headers['content-type'], 'text/html')

        r = requests.get(url, headers={'Accept': 'application/json;q=0.3;'})
        self.assertEqual(r.headers['content-type'], 'text/morse')

        r = requests.get(url, headers={'Accept': '*/*;q=0.3,'})
        self.assertEqual(r.headers['content-type'], 'text/morse')

        r = requests.get(url, headers={'Accept': 'text/*;q=0.3,'})
        self.assertEqual(r.headers['content-type'], 'application/json')

        r = requests.get(url, headers={'Accept': 'application/*;q=0.3,text/morse;q=0.5'})
        self.assertEqual(r.headers['content-type'], 'text/csv')

    def test_5515(self):
        url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+15)
        with self.assertRaises(requests.exceptions.ConnectionError) as cm:
            r = requests.get(url, timeout=0.005)

    def test_5516(self):
        url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+16)
        with self.assertRaises(requests.exceptions.ChunkedEncodingError) as cm:
            r = requests.get(url)

    def test_headers(self):
        url = 'http://127.0.0.1:{port}'.format(port=BASE_PORT+9)
        r = requests.get(url)
        self.assertEqual(r.headers['Server'], 'Hamms/{version}'.format(version=version))


if __name__ == '__main__':
    unittest.main()