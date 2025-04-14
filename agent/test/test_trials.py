import unittest
from urllib.parse import urlparse
import os
import sys
import io
from . import HasInternetConnection
#from ..src import trials
#from ..src.HttpsRequester import HttpsRequester
import trials
import HttpsRequester
import notebook_genai
import file_fetcher

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
      self.assertTrue(result['organization'])
      self.assertTrue(result['citations'])
      self.assertTrue(result['citations'][0]['pmid'])
      self.assertTrue(result['citations'][0]['citation'])

  def test_parse_req_parse_json(self):
    if HasInternetConnection.have_internet():
      disease = "prostate cancer"
      url_str = trials.get_trial_request_url(disease)
      req = HttpsRequester.HttpsRequester()
      content = req.send_req(url_str)
      results_list, nextPageToken = trials.parse_and_filter(content)
      self.assertIsNotNone(nextPageToken)
      self.assertIsNotNone(results_list)
      for result in results_list:
        self.assertTrue(result['briefTitle'])
        self.assertTrue(result['officialTitle'])
        self.assertTrue(result['organization'])
        self.assertTrue(result['citations'])
        self.assertTrue(result['citations'][0]['pmid'])
        self.assertTrue(result['citations'][0]['citation'])

  def test_get_clinical_trials_for_disease(self):
    if HasInternetConnection.have_internet():
      disease = "lung cancer"
      results_list = trials.get_clinical_trials_for_disease(disease)
      self.assertIsNotNone(results_list)
      for result in results_list:
        self.assertTrue(result['briefTitle'])
        self.assertTrue(result['officialTitle'])
        self.assertTrue(result['organization'])
        self.assertTrue(result['citations'])
        self.assertTrue(result['citations'][0]['pmid'])
        self.assertTrue(result['citations'][0]['citation'])

  def simulate_user_input(self):
    original_stdin = sys.stdin
    sys.stdin = io.StringIO("1\n")
    sys_stdin = original_stdin

  def test_user_list_index_input(self):
    content = self._read_json_response_1()
    trials_list, nextPageToken = trials.parse_and_filter(content)
    self.simulate_user_input()
    idx = notebook_genai.user_list_index_input(options_name="trial", \
                                         options_list=trials_list, format_func=trials.format_trials)
    self.assertEqual(1, idx)

  def _read_json_response_1(self):
    file_name ="clinical_trials_response_20250409.json"
    return file_fetcher.get_testresource(file_name=file_name)

if __name__ == '__main__':
  unittest.main()
