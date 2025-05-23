import unittest
from urllib.parse import urlparse
from . import NIH_API_KEY
from . import HasInternetConnection
import article
import file_fetcher

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
    abstract = article.parse_and_filter_article(content)
    self.assertIsNotNone(abstract)

  def test_get_article_abstract_from_pubmed(self):
    if HasInternetConnection.have_internet():
      s_id = "123"
      q_id = 0
      pmid = 21976132
      API_KEY = NIH_API_KEY.get_NIH_API_KEY()
      abstract = article.get_article_abstract_from_pubmed(s_id, q_id, pmid, API_KEY);
      self.assertIsNotNone(abstract)

  def _read_xml_response_1(self):
    return file_fetcher.get_testresource(file_name="entrez_pubmed_response_20250409.xml")

if __name__ == '__main__':
  unittest.main()
