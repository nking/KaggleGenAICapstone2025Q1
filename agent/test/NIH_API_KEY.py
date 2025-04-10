import os

#code to read the NIH API_KEY from a local file that is not checked into the repository
# it replaces what kaggle secrets does for the notebook

def get_NIH_API_KEY():
  working_dir = os.environ.get('PWD')
  if working_dir.endswith("test"):
    working_dir += "/../.."
  working_dir += "/agent/testresources"
  filepath = working_dir + "/NIH_API_KEY.txt"
  with open(filepath, 'r') as f:
    key = f.read().strip()
  return key
