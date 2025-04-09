import secrets
import os

def get_session_id():

  base_dir = os.environ.get('PWD')
  if not base_dir.startswith("/kaggle/working"):
    base_dir += "/bin/"

  _session_file = base_dir + "/_session_id"

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
    except FileNotFoundError:
      print(f"{_session_file} not found\n")
    except ValueError:
      print(f"Error: Invalid content in {_session_file}.\n")

  session_id = int.from_bytes(secrets.token_bytes(16), byteorder='big')
  # random_hex = random_int.hex()
  with open(_session_file, 'w') as outfile:
    outfile.write(f'{session_id}')

  return session_id