#!pip install -q requests
import requests
import time
import os
from urllib.parse import urlparse

class HttpsRequester:
  last_req_time: int = None
  max_fails: int = 2
  def __init__(self):
    pass

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
    if self.last_req_time:
      # time units are seconds
      delta = time.clock_gettime(time.CLOCK_REALTIME) - self.last_req
      if delta < 1:
        time.sleep(1)
    self.last_req = time.clock_gettime(time.CLOCK_REALTIME)

    n_tries = 0
    error_str = None
    while n_tries < self.max_fails:
      try:
        response = requests.get(url_str)
      except requests.exceptions.HTTPError as err:
        #print('HTTP error occurred:', err)
        error_str = str(err)
        return None
      except Exception as err:
        #print('Other error occurred:', err)
        error_str = str(err)
        return None
      if response.status_code == 200:
        #print('Request successful!')
        return response.content
      n_tries += 1
    raise Exception(error_str)