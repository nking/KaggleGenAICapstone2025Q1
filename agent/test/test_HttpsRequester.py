import unittest
from urllib.parse import urlparse
import os
from ..src.HttpsRequester import HttpsRequester

class TestTrials(unittest.TestCase):
  def test_script_execution(self):
    url_Str = "http://www.example.com"
    req = HttpsRequester()
    res = req.send_req(url_Str)
    self.assertIsNotNone(res)
    #result.query

if __name__ == '__main__':
  unittest.main()
