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

from IPython.display import Markdown, display

genai.__version__

import enum
from eval_instruction import get_eval_instruction

class SummaryRating(enum.Enum):
  VERY_GOOD = '5'
  GOOD = '4'
  OK = '3'
  BAD = '2'
  VERY_BAD = '1'

class UserFeedBack(enum.Enum):
  VERY_GOOD = '5'
  GOOD = '4'
  OK = '3'
  BAD = '2'
  VERY_BAD = '1'

class ReasonForBad(enum.Enum):
  TRIALS_NOT_RELEVANT = '3'
  BAD_RESULTS_SUMMARY = '2'
  ERROR = '1'

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
  chat = client.chats.create(model=model_name)

  # Generate the full text response.
  response = chat.send_message(
    message=SUMMARY_PROMPT.format(prompt=prompt, response=summary)
  )
  verbose_eval = response.text

  # Coerce into the desired structure.
  structured_output_config = types.GenerateContentConfig(
    response_mime_type="text/x.enum",
    response_schema=SummaryRating,
  )
  response = chat.send_message(
    message="Convert the final score.",
    config=structured_output_config,
  )
  structured_eval = response.parsed

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