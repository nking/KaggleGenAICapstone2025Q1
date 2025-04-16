import unittest
import os
import session_id

class TestSessionId(unittest.TestCase):
  def test_script_execution(self):
    s_id = session_id.get_session_id()
    self.assertIsNotNone(s_id)
    self.assertTrue(isinstance(s_id, int))
    content = self._read_session_file(session_id.get_session_filepath())
    self.assertEqual(s_id, int(content))

  def _read_session_file(self, flpath: str):
    try:
      with open(flpath, 'r') as infile:
        return infile.read().strip()
    except FileNotFoundError:
      print(f"{flpath} not found\n")
    except ValueError:
      print(f"Error: Invalid content in {flpath}.\n")

if __name__ == '__main__':
  unittest.main()
