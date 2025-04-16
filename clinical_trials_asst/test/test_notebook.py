import unittest
from urllib.parse import urlparse
import os
import notebook_genai
import session_id
import prompts
import setup_logging
from . import HasInternetConnection
from . import AI_Studio_API_KEY
import sys
import io
import time

class TestTrials(unittest.TestCase):

  def test_simple_list_format(self):
    a_list = ["rating 1", "rating 2", "rating 3"]
    fmted = notebook_genai.simple_list_format(a_list)
    self.assertIsNotNone(fmted)

  def test_user_feedback(self):
    s_id = session_id.get_session_id()
    original_stdin = sys.stdin
    # sys.stdin = original_stdin

    sys.stdin = io.StringIO("y\n")
    confirmed = notebook_genai.user_response_to_feedback_query()
    self.assertTrue(confirmed)

    sys.stdin = io.StringIO("n\n")
    confirmed = notebook_genai.user_response_to_feedback_query()
    self.assertFalse(confirmed)

    #after True from user_response_to_feedback_query
    n_lines = self._count_feedback_log_lines()
    q_id = 0
    sys.stdin = io.StringIO("0\n")
    resp = notebook_genai.store_feedback_rating(session_id = s_id, query_number = q_id)
    self.assertEqual(-1, resp.lower().find("bad"))
    n_lines_2 = self._count_feedback_log_lines()
    self.assertTrue(n_lines_2 > n_lines)

    q_id += 1
    sys.stdin = io.StringIO("3\n")
    resp = notebook_genai.store_feedback_rating(session_id=s_id, query_number=q_id)
    self.assertTrue(resp.lower().find("bad") > -1)
    n_lines_3 = self._count_feedback_log_lines()
    self.assertTrue(n_lines_3 > n_lines_2)

    q_id += 1
    sys.stdin = io.StringIO("3\n")
    notebook_genai.store_feedback_reason(session_id=s_id, query_number=q_id)
    n_lines_4 = self._count_feedback_log_lines()
    self.assertTrue(n_lines_4 > n_lines_3)

  def test_summarization(self):
    if not HasInternetConnection.have_internet():
      return

    s_id = session_id.get_session_id()

    # the gemma model has a  128K context window
    models=['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemma-3-27b-it']

    eval_model_name = models[2]

    key = AI_Studio_API_KEY.get_AI_Studio_API_KEY()

    abstract_str = self.get_test_abstract_01()

    # the unit tests by default run sequentially, so should be fine to assert number of lines in log file
    # before and after a logged function
    n_lines_agent = self._count_agent_log_lines()
    if n_lines_agent is None:
      n_lines_agent = 0
    n_lines_agent_expected = 3 * len(models)

    # evaulate the summary
    n_lines_eval = self._count_eval_log_lines()
    if n_lines_eval is None:
      n_lines_eval = 0
    n_lines_eval_expected = 1 * len(models)

    verbosity = 1

    for q_id in range(len(models)):

      client = notebook_genai.get_genAI_client(key)

      model_name = models[q_id]

      summary = notebook_genai.summarize_abstract(s_id, q_id, client, \
        prompt = prompts.get_summarization_prompt(), abstract=abstract_str,\
        model_name= model_name,  verbose=verbosity)

      self.assertIsNotNone(summary)

      text_eval, struct_eval = notebook_genai.evaluate_the_summary(session_id = s_id, query_number = q_id, \
        client = client, prompt = [prompts.get_summarization_prompt(), abstract_str], \
        summary = summary, model_name= eval_model_name, verbose=verbosity)

      self.assertIsNotNone(text_eval)
      self.assertIsNotNone(summary)
      if verbosity > 0:
        print(f'LLM={model_name}, eval={struct_eval}\n')

    n_lines_agent_2 = self._count_agent_log_lines()
    n_lines_eval_2 = self._count_eval_log_lines()
    # clinical_trials_asst logs should have 3 more lines, but there is buffered
    self.assertTrue(n_lines_agent_2 - n_lines_agent > 0)
    self.assertTrue(n_lines_eval_2 - n_lines_eval > 0)

  def _read_file_last_line(self, flpath: str):
    try:
      with open(flpath, 'r') as infile:
        return infile.readlines()[-1].strip()
    except FileNotFoundError:
      print(f"{flpath} not found\n")
    except ValueError:
      print(f"Error: Invalid content in {flpath}.\n")

  def _count_agent_log_lines(self):
    flpath = setup_logging.agent_flpath
    try:
      with open(flpath, 'r') as infile:
        return len(infile.readlines())
    except FileNotFoundError:
      print(f"{flpath} not found\n")
    except ValueError:
      print(f"Error: Invalid content in {flpath}.\n")

  def _count_feedback_log_lines(self):
    flpath = setup_logging.feedback_flpath
    try:
      with open(flpath, 'r') as infile:
        return len(infile.readlines())
    except FileNotFoundError:
      print(f"{flpath} not found\n")
    except ValueError:
      print(f"Error: Invalid content in {flpath}.\n")

  def _count_eval_log_lines(self):
    flpath = setup_logging.llm_eval_flpath
    try:
      with open(flpath, 'r') as infile:
        return len(infile.readlines())
    except FileNotFoundError:
      print(f"{flpath} not found\n")
    except ValueError:
      print(f"Error: Invalid content in {flpath}.\n")

  def get_test_abstract_01(self):
    return """\
Men taking antioxidant vitamin E supplements 
have increased prostate cancer (PC) risk. However, whether 
pro-oxidants protect from PC remained unclear. In this work, 
we show that a pro-oxidant vitamin K precursor 
[menadione sodium bisulfite (MSB)] suppresses PC progression in mice, 
killing cells through an oxidative cell death: MSB antagonizes 
the essential class III phosphatidylinositol (PI) 3-kinase VPS34-the 
regulator of endosome identity and sorting-through oxidation of 
key cysteines, pointing to a redox checkpoint in sorting. 
Testing MSB in a myotubular myopathy model that is driven by 
loss of MTM1-the phosphatase antagonist of VPS34-we show that 
dietary MSB improved muscle histology and function and extended 
life span. These findings enhance our understanding of pro-oxidant 
selectivity and show how definition of the pathways they impinge 
on can give rise to unexpected therapeutic opportunities."""

if __name__ == '__main__':
  unittest.main()
