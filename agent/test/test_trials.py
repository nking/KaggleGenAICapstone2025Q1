import unittest
from urllib.parse import urlparse
import os
from ..src import trials
from ..src.HttpsRequester import HttpsRequester

class TestTrials(unittest.TestCase):
  def test_create_url(self):
    disease = "lung cancer"
    req = trials.get_trial_request_url(disease)
    result = urlparse(req)
    self.assertIsNotNone(result)
    self.assertIsNotNone(result.scheme)
    self.assertEqual(result.scheme, "https")
    self.assertIsNotNone(result.netloc)
    self.assertTrue(result.netloc.startswith("clinicaltrials.gov"))
    self.assertEqual(result.netloc, "clinicaltrials.gov")
    self.assertEqual(result.path, "/api/v2/studies")
    #result.query

  def test_parse_json(self):
    content = self._read_json_response_1()
    results_list, nextPageToken = trials.parse_and_filter(content)
    self.assertIsNotNone(nextPageToken)
    for result in results_list:
      self.assertTrue(result['briefTitle'])
      self.assertTrue(result['officialTitle'])
      self.assertTrue(result['citations'])
      self.assertTrue(result['citations'][0]['pmid'])
      self.assertTrue(result['citations'][0]['citation'])

  def test_parse_req_parse_json(self):
    disease = "prostate cancer"
    url_str = trials.get_trial_request_url(disease)
    req = HttpsRequester()
    content = req.send_req(url_str)
    results_list, nextPageToken = trials.parse_and_filter(content)
    self.assertIsNotNone(nextPageToken)
    for result in results_list:
      self.assertTrue(result['briefTitle'])
      self.assertTrue(result['officialTitle'])
      self.assertTrue(result['citations'])
      self.assertTrue(result['citations'][0]['pmid'])
      self.assertTrue(result['citations'][0]['citation'])

  def _read_json_response_1(self):
    working_dir = os.environ.get('PWD')
    if working_dir.endswith("test"):
      working_dir += "/../../"
    flpath = working_dir + "/agent/testresources/clinical_trials_response_20250409.json"
    try:
      with open(flpath, 'r') as infile:
        return infile.read().strip()
    except FileNotFoundError:
      print(f"{flpath} not found\n")
    except ValueError:
      print(f"Error: Invalid content in {flpath}.\n")

if __name__ == '__main__':
  unittest.main()
