import secrets
import os
from setup_logging import log_error

def get_session_filepath():
  base_dir = os.environ.get('PWD')
  if not base_dir.startswith("/kaggle/working"):
    base_dir += "/bin/"
  return base_dir + "/_session_id"

def get_session_id():

  _session_file = get_session_filepath()

  if not os.path.exists(_session_file):
    #128 bit session id
    session_id = int.from_bytes(secrets.token_bytes(16), byteorder='big')
    #random_hex = random_int.hex()
    with open(_session_file, 'w') as outfile:
      outfile.write(f'{session_id}')
    return session_id
  else:
    try:
      with open(_session_file, 'r') as infile:
        content = infile.read().strip()
        return int(content)
    except Exception as e:
      print(f"Error reading {_session_file}\n")
      log_error("no_session_id", f"session_file_read|err={e}")
      #drop through to create a new session id
  session_id = int.from_bytes(secrets.token_bytes(16), byteorder='big')
  # random_hex = random_int.hex()
  with open(_session_file, 'w') as outfile:
    outfile.write(f'{session_id}')

  return session_id