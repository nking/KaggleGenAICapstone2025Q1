import os

def get_base_dir():
  working_dir = os.environ.get('PWD')
  #base_dir/agent/test
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

def read_file_contents(flpath: str) :
  try:
    with open(flpath, 'r') as infile:
      return infile.read().strip()
  except FileNotFoundError:
    print(f"{flpath} not found\n")
  except ValueError:
    print(f"Error: Invalid content in {flpath}.\n")
