import os

# replaces what kaggle secrets does for the notebook.  except is visible as a string
# this is adapted from https://www.kaggle.com/code/markishere/day-1-evaluation-and-structured-output
def get_AI_Studio_API_KEY():
  working_dir = os.environ.get('PWD')
  if working_dir.endswith("test"):
    working_dir += "/../.."
  working_dir += "/agent/testresources"
  filepath = working_dir + "/AI_Studio_API_KEY.txt"
  with open(filepath, 'r') as f:
    key = f.read().strip()
  return key
