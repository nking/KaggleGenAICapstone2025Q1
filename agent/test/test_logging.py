import unittest
import runpy
import os

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
    result['log_step'](agent_logger, session_id, msg)

    content = self._read_agent_logfile(result['agent_flpath'])
    self.assertIsNotNone(content)
    self.assertTrue(content.endswith(msg))

  def _read_agent_logfile(self, agent_flpath:str):
    try:
      with open(agent_flpath, 'r') as infile:
        return infile.read().strip()
    except FileNotFoundError:
      print(f"{agent_flpath} not found\n")
    except ValueError:
      print(f"Error: Invalid content in {agent_flpath}.\n")


if __name__ == '__main__':
  unittest.main()
