import unittest

import prompts

class TestPrompt(unittest.TestCase):
  def test_get_summarization_prompt(self):
    prompt = prompts.get_summarization_prompt()
    self.assertIsNotNone(prompt)

  def test_get_eval_instr(self):
    prompt = prompts.get_eval_instruction()
    self.assertIsNotNone(prompt)

  def test_get_disease_name_prompt(self):
    prompt = prompts.get_disease_name_prompt("lung cancer")
    self.assertIsNotNone(prompt)

  def test_get_welcome_msg(self):
    prompt = prompts.get_welcome_msg()
    self.assertIsNotNone(prompt)

if __name__ == '__main__':
  unittest.main()
