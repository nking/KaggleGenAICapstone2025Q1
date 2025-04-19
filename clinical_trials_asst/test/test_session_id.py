import unittest
import os
import session_id
import time

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

  def _read_stale_session_file(self, flpath: str):
    s_id = session_id.get_session_id()
    ts = time.time_ns() - 2*3600*1_000_000_000
    _session_file = session_id.get_session_filepath()
    _session_ts = _session_file + "_ts.txt"
    with open(_session_ts, 'w') as outfile:
      outfile.write(f'{ts}')
    s_id_2 = session_id.get_session_id()
    self.assertNotEqual(s_id, s_id2)

if __name__ == '__main__':
  unittest.main()
