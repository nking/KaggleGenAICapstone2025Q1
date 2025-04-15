#!pip install -qU 'langgraph==0.3.21' 'langchain-google-genai==2.1.2' 'langgraph-prebuilt==0.1.7'
# latest version is langchain-google-genai==2.1.2
#   latest version of the langraph libs might be later, but might not be compatible
import unittest
from langchain_core.prompts import ChatPromptTemplate
from typing import Annotated, Literal, Union, Callable
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from IPython.display import Image, display
from pprint import pprint, pformat
from langchain_core.messages.ai import AIMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from collections.abc import Iterable
from random import randint
from langchain_core.messages.tool import ToolMessage
from langchain_core.tools.render import render_text_description
import os
import re
from contextlib import redirect_stdout
import io
import sys
import threading
import time

#The code is adpated from
#adapted from https://www.kaggle.com/code/markishere/day-3-building-an-agent-with-langgraph

# The tool schema is added to the prompt now to improve the decisions and to enable the gamma model to work with the
# code all the way until the LLM is going to choose a tool given its prompt history (first message includes instructions)
# and then a user input.
# I added notes below where gamma model steps have to be programmatically handled to parse the user input
# and understand it in context of the recent history
# (it's instructive to see how much the LLM is doing in the gemini invoke call instead)

import mock_functions
from trials import format_citations, get_clinical_trials_for_disease, format_trials
from prompts import get_summarization_prompt, get_disease_name_prompt, get_welcome_msg
from article import get_article_abstract_from_pubmed
from notebook_genai import get_genAI_client, summarize_abstract, evaluate_the_summary, user_list_index_input, \
  user_response_to_feedback_query, store_feedback_rating, store_feedback_reason
from session_id import get_session_id
from setup_logging import log_error, log_agent
from disease_choices_for_automated import select_disease_name_randomly
from . import HasInternetConnection

AI_STUDIO_KEY = mock_functions.get_AI_STUDIO_API_KEY()
os.environ["GOOGLE_API_KEY"] = AI_STUDIO_KEY

NIH_API_KEY = mock_functions.get_NIH_API_KEY()

class GraphState(TypedDict):
  messages: Annotated[list, add_messages]
  q_id: int
  finished: bool
  disease: str
  pmid: str
  trials: list
  trial_number: int
  abstract:str
  next_node:str

def reset_graph_state(state: GraphState):
  if "abstract" in state:
    state.pop("abstract")
  if "trial_number" in state:
    state.pop("trial_number")
  if "trials" in state:
    state.pop("trials")
  if "pmid" in state:
    state.pop("pmid")
  if "disease" in state:
    state.pop("disease")

from enum import Enum
class RunType(Enum):
  DEBUG = 1
  AUTOMATIC = 2
  INTERACTIVE = 3

run_type = RunType.AUTOMATIC
verbosity = 0

#langchain_google_genai.chat_models.ChatGoogleGenerativeAIError:
# Invalid argument provided to Gemini: 400 Function calling is not enabled for models/gemma-3-27b-it
# so I added the schema for the functions for tools to the prompts.
# gemini did okay with it inspite of my alterations of the instructions.
# gemma however has this error now: Developer instruction is not enabled for models/gemma-3-27b-it
models = ['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemma-3-27b-it']
model_name = models[2]

WELCOME_MSG = get_welcome_msg()

class MyTestCase(unittest.TestCase):
  def test_something(self):
    if not HasInternetConnection.have_internet():
      return

    s_id = get_session_id()

    client = get_genAI_client(AI_STUDIO_KEY)

    disease_name_checker = ChatGoogleGenerativeAI(
      model=model_name, temperature=0, max_tokens=None, timeout=None, max_retries=2,
      # other params...
    )

    #if decide to use a chatbot w/ an LLM that has instruction and tool ability, you can modify the below code to
    # give the chatbot more of the input processing and flow control.  the chatbot can be the google langraph genai chatbot
    # see https://www.kaggle.com/code/markishere/day-3-building-an-agent-with-langgraph
    # see args: https://python.langchain.com/api_reference/google_genai/llms/langchain_google_genai.llms.GoogleGenerativeAI.html#langchain_google_genai.llms.GoogleGenerativeAI
    #llm = ChatGoogleGenerativeAI(
    #  model=model_name, temperature=0, max_tokens=None, timeout=None, max_retries=2,
    #  # other params...
    #)

    #instead, will use the LLM for text summarization only
    #it's common for sequential chained workflows to outline the flow rather than leave it to LLM reasonong.
    #using langraph below for the flow control

    #the agent tools are coded into these langgraph nodes (functions directly below), invoked client-side

    # nodes can return the modified field of state for efficient update of state,
    # or can modify state directly and return the whole state though this is inefficient because
    # the entire state is re-copied.
    #
    # the conditional END for each step is implemented by updating state for "next_node" each time

    def user_input_disease(state: GraphState) -> GraphState:
      #print(f"Model (user_input_disease) debug\n")
      reset_graph_state(state)
      state["q_id"] = 0 if "q_id" not in state else state["q_id"] + 1

      if run_type == RunType.AUTOMATIC:
        original_stdin = sys.stdin
        if state["q_id"] > 0:
          #for automatic setting, we only run text summarization once
          sys.stdin = io.StringIO("q\n")
        else:
          sys.stdin = io.StringIO(f"{select_disease_name_randomly()}\n")

      #ask the user for the disease name then ask the llm if it recognizes the disease name
      max_iter = 10
      num_iter = 0
      while num_iter < max_iter:
        user_input = input("Please enter a disease to search for (q to quit at any time).\n:")
        user_input = user_input.strip()
        if user_input in {"q", "quit", "exit", "done", "goodbye"}:
          return {"finished": True}

        start_ns = time.time_ns()
        _prompt = get_disease_name_prompt(user_input)
        #ask the llm if it recognizes the name:
        response = disease_name_checker.invoke(_prompt)
        stop_ns = time.time_ns()
        elapsed_ns = stop_ns - start_ns
        log_agent(session_id=s_id, msg=f'q={state["q_id"]}|llm_disease_recog_time={elapsed_ns}')
        if response.content.lower().startswith("no"):
          user_input_2 = input(f"I don't recognize {user_input} as a disease name but clinicaltrials.gov might.\nType 0 to proceed or Type 1 to retype the disease name.\n:")
          user_input_2 = user_input_2.strip()
          if user_input_2 == "0":
            break
        else:
          break
        num_iter += 1
      #TODO: consider asking the LLM if this looks like a disease name, or let chatbot logic handle more of the code
      #LLM can suggest corrections if there are typos
      state["disease"] = user_input

      state["next_node"] = "fetch_trials"
      #return the entire state because we've reset fields and are modified others
      return state

    def simulate_input_0_if_auto():
      '''
      a convenience method for automating user input for notebook when run_type is AUTOMATIC
      '''
      if run_type == RunType.AUTOMATIC:
        original_stdin = sys.stdin
        sys.stdin = io.StringIO("0\n")

    def fetch_trials(state: GraphState) -> GraphState:
      #print(f"Model (fetch_trials_conditional) debug\n")
      if "disease" not in state:
        print("missing disease name")
        return {"next_node": "user_input_disease"}
      print("fetching trials...")
      if run_type == RunType.DEBUG:
        results = mock_functions.get_clinical_trials_for_disease(state["disease"])
      else:
        results = get_clinical_trials_for_disease(s_id, state["q_id"], state["disease"])
      if results is None or len(results) == 0:
        print("No trials were found.  The search at clinicaltrials.gov uses synonyms, but you might want to try different words.")
        return {"next_node": "user_input_disease"}
      return {"trials": results, "next_node": "user_choose_trial_number"}

    def user_choose_trial_number(state: GraphState) -> GraphState:
      #print(f"Model (user_choose_trial_number) debug\n")
      if "trials" not in state or len(state["trials"]) == 0:
        print("System Error.  no trials found.  please start again.")
        return {"next_node": "user_input_disease"}
      if run_type == RunType.AUTOMATIC:
        simulate_input_0_if_auto()
      idx = user_list_index_input(options_name="trial", options_list=state["trials"], format_func=format_trials)
      if idx is None or idx == -1:
        return {"finished": True}
      return {"trial_number": idx, "next_node": "user_choose_citation_number"}

    def user_choose_citation_number(state: GraphState) -> GraphState:
      #print(f"Model (user_choose_citation_number) debug\n")
      if "trials" not in state or len(state["trials"]) == 0:
        print("System Error.  no trials found.  please start again.")
        return {"next_node": "user_input_disease"}
      if "trial_number" not in state:
        print("System Error.  trial_number not found.  ")
        return {"next_node": "user_choose_trial_number"}
      #this is prevented by parsing stage, but check in any case:
      if "citations" not in state["trials"][state["trial_number"]] or len(state["trials"][state["trial_number"]]) == 0:
        print("System Error.  citations not found.  please choose another trial.")
        return {"next_node": "user_choose_trial_number"}
      citations = state["trials"][state["trial_number"]]["citations"]
      if run_type == RunType.AUTOMATIC:
        simulate_input_0_if_auto()
      idx = user_list_index_input(options_name="citation", options_list=citations, format_func=format_citations)
      if idx is None or idx == -1:
        return {"finished": True}
      return {"pmid" : citations[idx]["pmid"], "next_node" : "fetch_abstract"}

    def fetch_abstract(state: GraphState) -> GraphState:
      #print(f"Model (fetch_abstract): debug\n")
      if "pmid" not in state:
        print("Error.  article id not found.  please choose a citation.")
        return {"next_node" : "user_choose_citation_number"}
      print("fetching article...")
      if run_type == RunType.DEBUG:
        results = mock_functions.get_article_abstract_from_pubmed(state["pmid"])
      else:
        results = get_article_abstract_from_pubmed(s_id, state["q_id"], state["pmid"], NIH_API_KEY)
      if results is None or len(results) == 0:
        print(f'no articles found.  pubmed search for pmid={state["pmid"]} failed or the article did not have an abstract.  please choose another citation\n')
        return {"next_node" : "user_choose_citation_number"}
      return {"abstract": results, "next_node": "llm_summarization"}

    def llm_summarization(state: GraphState) -> GraphState:
      #print(f"Model (llm_summarization) debug\n")
      if "abstract" not in state or len(state["abstract"]) == 0:
        print("System Error.  no article found.  please choose another citation.")
        return {"next_node" : "user_choose_citation_number"}
      if run_type == RunType.DEBUG:
        summary = "a summary of the abstract"
      else:
        summary = summarize_abstract(session_id=s_id, query_number=state["q_id"], client=client, \
          prompt = get_summarization_prompt(), abstract=state["abstract"],\
          model_name= model_name,  verbose=verbosity)
        # the evaluation results are logged in the method
        # asynchronous to reduce user latency
        thread1 = threading.Thread(target=evaluate_the_summary, \
          args=(s_id, state["q_id"], client, [get_summarization_prompt(), state["abstract"]], \
          summary, model_name, verbosity))
        thread1.start()
        #text_eval, struct_eval = evaluate_the_summary(session_id=s_id, query_number=state["q_id"], client=client, \
        #  prompt = [get_summarization_prompt(), state["abstract"]], \
        #  summary = summary, model_name= model_name, verbose=verbosity)
      print("Here is a summary of the abstract of the chosen citation.\n")
      if model_name.lower().startswith("gemma"):
        # correct pprint output to remove tuple wrap and explicit "\n" characters and line single quote wrappers
        _summary = pformat(summary)
        _summary = _summary[1:len(_summary)-1].replace("\\n", "")
        _summary = _summary.replace("\'\'", "")
        _summary = _summary.replace(" \'", "")
        print(f"{_summary}")
      else:
        pprint(summary)
      return {"next_node": "query_user_for_feedback"}

    def query_user_for_feedback(state: GraphState) -> GraphState:
      #print(f"Model (query_user_for_feedback) debug\n")
      if run_type == RunType.AUTOMATIC:
        sys.stdin = io.StringIO("y\n")
      confirmed = user_response_to_feedback_query()
      if confirmed:
        if run_type == RunType.AUTOMATIC:
          sys.stdin = io.StringIO("0\n")
        resp = store_feedback_rating(session_id=s_id, query_number=state["q_id"])
        if resp.lower().find("bad") > -1:
          if run_type == RunType.AUTOMATIC:
            sys.stdin = io.StringIO("3\n")
          store_feedback_reason(session_id=s_id, query_number=state["q_id"])
      print("\n")
      return {"next_node": "user_input_disease"}

    def check_end_conditional(state: GraphState) -> GraphState:
      if "finished" in state and state["finished"] or "next_node" not in state:
        return END
      return state["next_node"]

    functions = [user_input_disease, fetch_trials, user_choose_trial_number, user_choose_citation_number, \
             fetch_abstract, llm_summarization, query_user_for_feedback]

    graph_builder = StateGraph(GraphState)

    for func in functions:
      graph_builder.add_node(func.__name__, func)

    for func in functions:
      graph_builder.add_conditional_edges(func.__name__, check_end_conditional)

    graph_builder.add_edge(START, "user_input_disease")

    graph = graph_builder.compile()

    #png_img_bytes = graph.get_graph().draw_mermaid_png()
    #Image(png_img_bytes)

    print(WELCOME_MSG)
    state = graph.invoke({"messages": []}, {"recursion_limit": 100})
    #pprint(state)

if __name__ == '__main__':
  unittest.main()
