import os
from setup_logging import log_error

def get_base_dir():
  working_dir = os.environ.get('PWD')
  #base_dir/clinical_trials_asst/test
  if working_dir.endswith("test"):
    working_dir += "/../../"
  return working_dir

def get_resource(file_name:str, asset_type:str="text", version:str = "V1.0", language: str="en"):
  #resources/text/en/V1.0
  fl_path = f"{get_base_dir()}/agent/resources/{asset_type}/{language}/{version}/{file_name}"
  return read_file_contents(fl_path)

def get_testresource(file_name:str):
  #resources/text/en/V1.0
  fl_path = f"{get_base_dir()}/agent/testresources/{file_name}"
  return read_file_contents(fl_path)

def read_file_contents(flpath: str):
  '''
  read file contents into a string

  Args:
    flpath: absolute file path

  Returns:
    returns file contents.  returns None if an exception occurred.
  '''
  try:
    with open(flpath, 'r') as infile:
      return infile.read().strip()
  except Exception as e:
    print(f"Error reading {flpath}\n")
    log_error("no_session_id", f"file_read|err={e}")
    return None
