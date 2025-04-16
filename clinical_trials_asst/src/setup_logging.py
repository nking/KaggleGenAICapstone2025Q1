#manually uncomment this in jupyter notebook
#!pip install -q concurrent_log_handler

#TODO: swap out the logging library:.  sometimes double logs an item, that is 2 identical rows

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
agent_flpath = log_dir + "clinical_trials_asst.log"
feedback_dir = working_dir + 'data/feedback/'
feedback_flpath = feedback_dir + "feedback.log"
llm_eval_dir = working_dir + 'data/eval/'
llm_eval_flpath = llm_eval_dir + "llm.log"
error_dir = working_dir + 'data/error/'
error_flpath = error_dir + "err.log"


if not os.path.exists(feedback_dir):
  os.makedirs(log_dir, exist_ok=True)
  os.mkdir(llm_eval_dir)
  os.mkdir(error_dir)
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

agent_logger = get_logger(agent_flpath, "clinical_trials_asst")
eval_logger = get_logger(llm_eval_flpath, "llm_eval")
feedback_logger = get_logger(feedback_flpath, "feedback")
error_logger = get_logger(error_flpath, "error")

def get_agent_logger():
  return agent_logger

def get_llm_eval_logger():
  return eval_logger

def get_feedback_logger():
  return feedback_logger

def get_error_logger():
  return error_logger

def get_timestamp():
  return time.time_ns()

def log_to_cloud(msg: str, log_type: str):
  '''
  a stub for a cloud API method
  '''
  pass

def log_user_feedback(session_id: str, msg : str):
  logger = get_feedback_logger()
  stmt = f"{get_timestamp()}|{session_id}|{msg}"
  logger.info(stmt)
  log_to_cloud(stmt, 'feedback')

def log_llm_eval(session_id: str, msg : str):
  logger = get_llm_eval_logger()
  stmt = f"{get_timestamp()}|{session_id}|{msg}"
  logger.info(stmt)
  log_to_cloud(stmt, 'eval')

def log_error(session_id: str, msg : str):
  logger = get_error_logger()
  stmt = f"{get_timestamp()}|{session_id}|{msg}"
  logger.info(stmt)
  log_to_cloud(stmt, 'error')

def log_agent(session_id: str, msg : str, logger: logging.Logger = None):
  if logger is None:
    logger = get_agent_logger()
  stmt = f"{get_timestamp()}|{session_id}|{msg}"
  logger.info(stmt)
  log_to_cloud(stmt, 'clinical_trials_asst')
