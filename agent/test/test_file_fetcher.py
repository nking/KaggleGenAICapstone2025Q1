import unittest
import file_fetcher

class TestArticle(unittest.TestCase):
  def test_fetch_base_dir(self):
    base_dir = file_fetcher.get_base_dir()
    self.assertTrue(base_dir.endswith("KaggleGenAICapstone2025Q1"))
    #result.query

  def test_get_testresource(self):
    file_name = "entrez_pubmed_response_20250409.xml"
    content = file_fetcher.get_testresource(file_name)
    self.assertIsNotNone(content)

  def test_get_resource(self):
    content = file_fetcher.get_resource(file_name="eval_instruction.txt", asset_type="text",\
        version="V1.0", language="en")
    self.assertIsNotNone(content)

if __name__ == '__main__':
  unittest.main()
