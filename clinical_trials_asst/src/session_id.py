import secrets
import os
import time
from setup_logging import log_error

def get_session_filepath():
  base_dir = os.environ.get('PWD')
  if not base_dir.startswith("/kaggle/working"):
    base_dir += "/bin/"
  return base_dir + "/_session_id"

def get_session_id():
  _session_file = get_session_filepath()
  _session_ts = _session_file + "_ts.txt"

  write_new = True
  if os.path.exists(_session_ts):
    with open(_session_ts, 'r') as infile:
      ts = infile.read().strip()
    #1 hour = 3600 sec = 3600 sec * (1E9 ns/1sec)
    if (time.time_ns() - int(ts)) < 3600*1_000_000_000:
      write_new = False

  if not write_new:
    try:
      #update ts
      with open(_session_ts, 'w') as outfile:
        outfile.write(f'{time.time_ns()}')
      with open(_session_file, 'r') as infile:
        content = infile.read().strip()
        return int(content)
    except Exception as e:
      print(f"Error reading {_session_file}\n")
      log_error("no_session_id", f"session_file_read|err={e}")
      #drop through to create a new session id

  # 128 bit session id
  session_id = int.from_bytes(secrets.token_bytes(16), byteorder='big')
  with open(_session_file, 'w') as outfile:
    outfile.write(f'{session_id}')
  with open(_session_ts, 'w') as outfile:
    outfile.write(f'{time.time_ns()}')
  return session_id
