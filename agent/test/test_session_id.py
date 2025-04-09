import unittest
from ..src import session_id

class TestSessionId(unittest.TestCase):
  def test_script_execution(self):
    s_id = session_id.get_session_id()
    self.assertIsNotNone(s_id)
    self.assertTrue(isinstance(s_id, int))

if __name__ == '__main__':
  unittest.main()
