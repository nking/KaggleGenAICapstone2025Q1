#!pip install -q requests
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
import time

class HttpsRequester:
  '''
  send an https or http request given a url, a max number of 3 retries and a backoff factor of 1.  (no handling of post data)
  '''
  def __init__(self, max_retries : int = 3):
    self.session = requests.Session()
    # Delay between retries: {backoff factor} * (2 ** ({retry number} - 1))
    retries = Retry(total=max_retries,  backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], \
      allowed_methods=["HEAD", "TRACE", "GET", "PUT", "OPTIONS", "DELETE", "POST"])  # Methods to retry
    adapter = HTTPAdapter(max_retries=retries)
    self.session.mount('http://', adapter)
    self.session.mount('https://', adapter)

  def send_req(self, url_str: str) -> str:
    '''
     given the API string, return the response.
     throws exception upon error.  catch the exception and retry if it appears to be a rate limit
     violation from concurrent notebook images, else use alerts for notifying support.

     Args:
         url_str  is the full API url
     Throws:
         exception
     Returns:
         the result as a string
     '''
    error_str = None
    try:
      response = requests.get(url_str)
    except Exception as err:
      #print('Other error occurred:', err)
      error_str = str(err)
      i = error_str.find("Caused by")
      error_str = error_str[i:]
      return None
    if response.status_code == 200:
      #print('Request successful!')
      return response.content
    raise Exception(error_str)