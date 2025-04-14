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

  def test_mask_API_KEY(self):
    req_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=30224019&retstart=0&retmax=1&retmode=xml&rettext=xml&api_key=02jPj"
    req = HttpsRequester.HttpsRequester()
    masked_url = req.mask_API_KEY(req_url)
    expected = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=30224019&retstart=0&retmax=1&retmode=xml&rettext=xml&"
    self.assertEqual(expected, masked_url)

if __name__ == '__main__':
  unittest.main()
