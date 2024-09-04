try:
    from httplib import BadStatusLine
except ImportError:
    from http.client import BadStatusLine

import unittest
import requests

from hamms import HammsServer, reactor

hs = HammsServer()


class TestHammsServer(unittest.TestCase):
    def test_custom_port(self):
        """ Should be able to specify a custom port to listen on """
        try:
            # XXX port find_unused_port method and use it
            port=14100
            hs.start(beginning_port=port)
            r = requests.get('http://127.0.0.1:{port}'.format(port=port+9))
            self.assertEqual(r.status_code, 200)

            with self.assertRaises(requests.exceptions.ConnectionError) as cm:
                r = requests.get('http://127.0.0.1:{port}'.format(port=port+3))
            self.assertIsInstance(cm.exception, requests.exceptions.ConnectionError)

        finally:
            # We can't stop the reactor in case other test files are going to run.
            # hs.stop()
            pass
