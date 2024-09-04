import unittest
from hamms import get_header

req = "\r\n".join(["GET / HTTP/1.0",
                "User-Agent: my-user-agent",
                "Accept: */*", "\r\n"])

noreq = "\r\n".join(["GET / HTTP/1.0",
                    "Accept: */*", "\r\n"])

class TestUtils(unittest.TestCase):
    def test_user_agent(self):
        self.assertEqual("my-user-agent", get_header("user-agent", req))
        self.assertEqual("", get_header("user-agent", noreq))
