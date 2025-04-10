import unittest
from urllib.parse import urlparse
import os
#from ..src.HttpsRequester import HttpsRequester
import HttpsRequester
from . import HasInternetConnection

class TestTrials(unittest.TestCase):
  def test_sedn_request(self):
    if HasInternetConnection.have_internet():
      url_Str = "http://www.example.com"
      req = HttpsRequester.HttpsRequester()
      res = req.send_req(url_Str)
      self.assertIsNotNone(res)
      #result.query

if __name__ == '__main__':
  unittest.main()
