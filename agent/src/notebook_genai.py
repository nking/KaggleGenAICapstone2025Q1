#!pip install -Uq "google-genai==1.7.0"
#from kaggle_secrets import UserSecretsClient

#code adapted from notebooks from Google/Kaggle 5-day GenAI course 2025Q1
# https://www.kaggle.com/code/markishere/day-1-evaluation-and-structured-output
# and other notebooks
#    https://cloud.google.com/vertex-ai/generative-ai/docs/models/metrics-templates#pairwise_coherence

import time
from google import genai
from google.genai import types
from google.api_core import retry
from setup_logging import log_agent, log_llm_eval, log_user_feedback, get_agent_logger
from typing import Callable
import io
from collections import OrderedDict

from IPython.display import Markdown, display

genai.__version__

import enum
from prompts import get_eval_instruction, get_feedback_query

class SummaryRating(enum.Enum):
  VERY_GOOD = '5'
  GOOD = '4'
  OK = '3'
  BAD = '2'
  VERY_BAD = '1'

user_feedback_dict = OrderedDict()
user_feedback_dict['VERY_GOOD'] = 5
user_feedback_dict['GOOD'] = 4
user_feedback_dict['OK'] = 3
user_feedback_dict['BAD'] = 2
user_feedback_dict['VERYBAD'] = 1

reason_for_bad_dict = OrderedDict()
reason_for_bad_dict['TRIALS_NOT_RELEVANT'] = 0
reason_for_bad_dict['BAD_RESULTS_SUMMARY'] = 1
reason_for_bad_dict['ERRORS'] = 2
reason_for_bad_dict['OTHER'] = 3

def init_generate_content_retry():
  is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})
  # free tier for gemini flash 2: RPM=15, TPM=1E6, RPD=1500
  if not hasattr(genai.models.Models.generate_content, '__wrapped__'):
    genai.models.Models.generate_content = retry.Retry(
      predicate=is_retriable, initial=0.25)(genai.models.Models.generate_content)

def get_genAI_client(AI_Studio_API_Key : str) -> genai.Client:
  client = genai.Client(api_key=AI_Studio_API_Key)
  init_generate_content_retry()
  return client

def evaluate_the_summary(session_id : str, query_number : int, \
  client : genai.Client,  prompt, summary, model_name : str = 'gemini-1.5-flash',\
  verbose : int = 0) :
  '''
  Evaluate the generated summary against the prompt used
  based upon Groundedness, Conciseness, and Fluency

  Args:
    session_id: session id of user
    query_number: the current query number for a summarize task from the user
    client: an instance of the genAI client
    prompt: a text prompt to give to the LLM, e.g. "summarize this text"
    summary: the LLM output summary of the abstract
    model_name: name of the LLM to use for evaluation
  Usage:
    text_eval, struct_eval = evaluate_the_summary(client, prompt=[request, document_file], summary=summary)
    Markdown(text_eval)
    print(struct_eval)

  References:
    https://www.kaggle.com/code/markishere/day-1-evaluation-and-structured-output
  '''
  start_ns = time.time_ns()

  SUMMARY_PROMPT = get_eval_instruction()

  #chat = client.chats.create(model=')
  eval_chat = client.chats.create(model=model_name,\
    config = types.GenerateContentConfig(temperature=0.0))

  # Generate the full text response.
  response = eval_chat.send_message(
    message=SUMMARY_PROMPT.format(prompt=prompt, response=summary)
  )
  verbose_eval = response.text

  '''
  # Coerce into the desired structure.
  response_mime_type = None #"text/x.enum"
  #if model_name.lower().startswith("gemma"):
  #  response_mime_type = None
  structured_output_config = types.GenerateContentConfig(
    response_mime_type=response_mime_type,
    response_schema=SummaryRating,
    temperature=0.0,
  )
  response = eval_chat.send_message(
    message="Convert the final score.",
    config=structured_output_config,
  )
  #response.text
  #structured_eval = response.parsed
  '''
  last_line = verbose_eval.split("\n")[-1].strip()
  structured_eval = last_line[0:last_line.find(")")+1]

  stop_ns = time.time_ns()
  elapsed_ns = stop_ns - start_ns
  log_agent(session_id=session_id, msg=f'q={query_number}|eval time: {elapsed_ns}')

  log_llm_eval(session_id=session_id, msg=f'q={query_number}|eval={structured_eval}')

  if verbose > 0:
    print(f'verbose_eval=\n{verbose_eval}\n')
    print(f'structured_eval=\n{structured_eval}\n')

  return verbose_eval, structured_eval

def summarize_abstract(session_id : str, query_number : int, \
  client : genai.Client, prompt: str, abstract : str, \
  model_name : str ="gemini-1.5-flash", verbose : int = 0) -> str:
  """summarize the abstract using the given client and prompt.
  the method also logs to the agent log file.
  Args:
    session_id: session id of user
    query_number: the current query number for a summarize task from the user
    client: an instance of the genAI client
    prompt: a text prompt to give to the LLM, e.g. "summarize this text"
    abstract: the abstract to summarize
    model_name: name of the LLM to use
  Returns:
    the LLM's summarization of the abstract
  """
  start_ns = time.time_ns()

  # in the config, can use a system instruction too if wanted:
  # e.g. system_instruction='terse_guidance'
  # system_instruction='moderate_guidance'
  # system_instruction='cited_guidance'

  # Set the temperature low to stabilise the output.
  config = types.GenerateContentConfig(temperature=0.0)
  response = client.models.generate_content(
      model=model_name,
      config=config,
      contents=[prompt, abstract],
  )
  # reponse dictionary"
  #"candidates": [{object(Candidate)}],  <== https://ai.google.dev/api/generate-content#v1beta.Candidate
  #"promptFeedback": {object(PromptFeedback)},
  #"usageMetadata": {object(UsageMetadata)},
  #"modelVersion": string

  stop_ns = time.time_ns()
  elapsed_ns = stop_ns - start_ns

  logger = get_agent_logger()
  log_agent(session_id=session_id, msg=f'q={query_number}|summary time: {elapsed_ns}', logger=logger)

  num_input_tokens = client.models.count_tokens(
    model=model_name, contents=[prompt, abstract]
  )
  log_agent(session_id=session_id, msg=f'q={query_number}| n_input: {num_input_tokens}', logger=logger)
  log_agent(session_id=session_id, msg=f'q={query_number}| n_output: {response.usage_metadata}', logger=logger)

  if verbose > 0:
    print(f'LLM summary:\n{response.text}\n')
    print(f"num input tokens = {num_input_tokens}\n")
    print(f"num output tokens = {response.usage_metadata}\n")
  # num input tokens = total_tokens=231 cached_content_token_count=None
  # num output tokens = cached_content_token_count=None candidates_token_count=127 prompt_token_count=227 total_token_count=354

  return response.text

def print_models(client : genai.Client) :
  for model in client.models.list():
    print(model.name)

def user_response_to_feedback_query() -> bool:
  '''
  query user for whether they would like to leave feedback.

  Returns:
    True if user responded y, else False
  '''
  query = get_feedback_query()
  user_input = input(f'{query}\n(y or n): ')
  user_input = user_input.strip()
  if user_input.lower() not in {"y", "yes"}:
    return False
  return True

def simple_list_format(a_list : list):
  string_io = io.StringIO()
  for i, a in enumerate(a_list):
    string_io.write(f"{i} {a}\n")
  return string_io.getvalue()

def store_feedback_rating(session_id: str, query_number: int) -> str:
  '''
  after user has consented to user_response_to_feedback_query()
  this method can be invoked to query them and log the responses.
  '''
  options_list = [k for k in user_feedback_dict]
  print("Please rate your text summarization for the disease trial:")
  options_name = "rating"
  idx = user_list_index_input(options_name=options_name, options_list=options_list, format_func=simple_list_format)
  if idx == -1:
    return None
  print(f"received {idx}\n")
  log_user_feedback(session_id, f'q_id={query_number}|{options_name}={idx, options_list[idx]}')
  print("Thank you for the feedback!")
  return options_list[idx]

def store_feedback_reason(session_id: str, query_number: int):
  '''
  after user has consented to user_response_to_feedback_query() and submitted a bad rating,
  this method can be invoked to query them and log the responses.
  '''
  print("\nPlease choose the closest reason for the poor experience:")
  options_list = [k for k in reason_for_bad_dict]
  options_name = "reason"
  idx = user_list_index_input(options_name=options_name, options_list=options_list, format_func=simple_list_format)
  if idx == -1:
    print("Thank you for the feedback!")
    return
  print(f"received {idx}\n")
  log_user_feedback(session_id, f'q_id={query_number}|{options_name}={idx, options_list[idx]}')
  print("Thank you for the feedback!")

def user_list_index_input(options_name: str, options_list: list, format_func:Callable) -> int:
  '''
  given a list of options and an options_name to use in the query to the user, and given
  a function to use to format the list of options into a printable string, ask the
  user to select an option by the index. The user can select an index or q to quit.

  Args:
    options_name: the name of the option, e.g. citation
    options_list: a list of options
    format_func: a function that will return a string to print when given the options_list
  Returns:
    the index of the option chosen by the user, else a -1 if the user chose q to quit or took more than
    the maximum number of retries to enter valid input.
  '''
  if options_name is None or options_list is None or len(options_list) == 0 or format_func is None:
    return -1
  max_iter = 10
  num_iter = 0
  while True:
    #pprint(format_func(options_list))
    print(format_func(options_list))
    user_input = input(f'Please choose a {options_name} number from 0 to {len(options_list)} or q to quit\n:')
    if user_input in {"q", "quit", "exit", "done", "goodbye"}:
      return -1
    if num_iter == max_iter:
      print("Maximum number of attempts exceeded.  please start again.")
      return -1
    num_iter += 1
    try:
      idx = int(user_input)
      if idx < 0 or idx >= len(options_list):
        print(f'number must be in range 0 to {len(options_list)}\n')
        continue
      return idx
    except Exception as ex:
      print(f'error interpreting {idx} as a number. try again\n:')
      continue
  return None
