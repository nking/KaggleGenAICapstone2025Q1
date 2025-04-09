#manually uncomment this in jupyter notebook
#!pip install -q concurrent_log_handler

import time
import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
import typing 
import os

working_dir = os.environ.get('PWD')
if not working_dir.startswith("/kaggle/working"):
  if working_dir.endswith("test"):
    working_dir += "/../../bin/"
  else:
    working_dir += "/bin/"

log_dir = working_dir + 'data/log/'
agent_flpath = log_dir + "agent.log"
feedback_dir = working_dir + 'data/feedback/'

if not os.path.exists(feedback_dir):
  os.makedirs(log_dir, exist_ok=True)
  os.mkdir(feedback_dir)

def get_logger(log_flpath : str, logger_name : str) -> logging.Logger:
  '''
  Args:
     log_fln - local log file name
     logger_name - name of logger in the instance
  Returns:
     an instance o logging logger
  '''
  logger = logging.getLogger(logger_name)
  logger.setLevel(logging.DEBUG)
  handler = ConcurrentRotatingFileHandler(log_flpath, maxBytes=8*1024*1024, backupCount=5)
  #formatter = logging.Formatter('%(asctime)s - %(message)s')
  formatter = logging.Formatter('%(message)s')
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  return logger

def get_agent_logger():
    return get_logger(agent_flpath, "agent")

def get_timestamp():
  return time.time_ns()

def log_step(logger : logging.Logger, session_id: str, msg : str):
  logger.info(f"{get_timestamp()} {session_id} {msg}\n")

def store_user_feedback(msg : str, session_id : str):
  log = get_logger(feedback_dir, "feedback")
  log.info(f"{get_timestamp()} {session_id} {msg}")

for dirname, _, filenames in os.walk("."):
  for filename in filenames:
    print(os.path.join(dirname, filename))

