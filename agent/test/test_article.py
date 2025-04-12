import unittest
from urllib.parse import urlparse
import os
#from ..src import article
#from ..src.HttpsRequester import HttpsRequester
from . import NIH_API_KEY
from . import HasInternetConnection
import article
import HttpsRequester

class TestArticle(unittest.TestCase):
  def test_create_url(self):
    pmid = 21976132
    API_KEY = NIH_API_KEY.get_NIH_API_KEY()
    req = article.get_pubmed_request_url(pmid, API_KEY)
    result = urlparse(req)
    self.assertIsNotNone(result)
    self.assertIsNotNone(result.scheme)
    self.assertEqual(result.scheme, "https")
    self.assertIsNotNone(result.netloc)
    self.assertTrue(result.netloc.startswith("eutils.ncbi.nlm.nih.gov"))
    self.assertEqual(result.netloc, "eutils.ncbi.nlm.nih.gov")
    self.assertIsNotNone(result.path)
    #result.query

  def test_parse_xml(self):
    content = self._read_xml_response_1()
    abstract = article.parse_and_filter(content)
    self.assertIsNotNone(abstract)

  def test_parse_req_parse_xml(self):
    if HasInternetConnection.have_internet():
      pmid = 21976132
      API_KEY = NIH_API_KEY.get_NIH_API_KEY()
      url_str = article.get_pubmed_request_url(pmid, API_KEY)
      req = HttpsRequester.HttpsRequester()
      content = req.send_req(url_str)
      abstract = article.parse_and_filter(content)
      self.assertIsNotNone(abstract)

  def _read_xml_response_1(self):
    working_dir = os.environ.get('PWD')
    if working_dir.endswith("test"):
      working_dir += "/../../"
    flpath = working_dir + "/agent/testresources/entrez_pubmed_response_20250409.xml"
    try:
      with open(flpath, 'r') as infile:
        return infile.read().strip()
    except FileNotFoundError:
      print(f"{flpath} not found\n")
    except ValueError:
      print(f"Error: Invalid content in {flpath}.\n")

if __name__ == '__main__':
  unittest.main()
