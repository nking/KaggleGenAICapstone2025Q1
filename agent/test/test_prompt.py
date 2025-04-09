import unittest
from ..src import prompt

class TestPrompt(unittest.TestCase):
  def test_script_execution(self):
    llm_prompt = prompt.get_prompt()
    self.assertIsNotNone(llm_prompt)

if __name__ == '__main__':
  unittest.main()
