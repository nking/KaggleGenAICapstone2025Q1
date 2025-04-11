import unittest
import runpy
import os
import random

class TestSessionId(unittest.TestCase):
  def test_script_execution(self):
    script_path = os.path.join(os.path.dirname(__file__), '../src', 'setup_logging.py')
    result = runpy.run_path(script_path)

    agent_logger = result['get_agent_logger']()
    self.assertIsNotNone(agent_logger)

    # session_id in practice, should be gotten from session_id script
    session_id = result['get_timestamp']()
    self.assertTrue(isinstance(session_id, int))

    msg = "abstract=asdfghj"
    result['log_agent'](session_id, msg)
    content = self._read_file_last_line(result['agent_flpath'])
    self.assertIsNotNone(content)
    self.assertTrue(content.endswith(msg))

    logger = result['get_agent_logger']()
    msg = "abstract=lduyw"
    result['log_agent'](session_id, msg, logger)
    content = self._read_file_last_line(result['agent_flpath'])
    self.assertIsNotNone(content)
    self.assertTrue(content.endswith(msg))

    msg = str(random.randint(0, 100))
    result['log_llm_eval'](session_id, msg)
    content = self._read_file_last_line(result['llm_eval_flpath'])
    self.assertIsNotNone(content)
    self.assertTrue(content.endswith(msg))

    msg = str(random.randint(0, 100))
    result['log_user_feedback'](session_id, msg)
    content = self._read_file_last_line(result['feedback_flpath'])
    self.assertIsNotNone(content)
    self.assertTrue(content.endswith(msg))

    msg = str(random.randint(0, 100))
    result['log_error'](session_id, msg)
    content = self._read_file_last_line(result['error_flpath'])
    self.assertIsNotNone(content)
    self.assertTrue(content.endswith(msg))

  def _read_file_last_line(self, flpath:str):
    try:
      with open(flpath, 'r') as infile:
        return infile.readlines()[-1].strip()
    except FileNotFoundError:
      print(f"{flpath} not found\n")
    except ValueError:
      print(f"Error: Invalid content in {flpath}.\n")


if __name__ == '__main__':
  unittest.main()
