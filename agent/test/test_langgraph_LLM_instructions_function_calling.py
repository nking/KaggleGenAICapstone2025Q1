#!pip install -qU 'langgraph==0.3.21' 'langchain-google-genai==2.1.2' 'langgraph-prebuilt==0.1.7'
# latest version is langchain-google-genai==2.1.2
#   latest version of the langraph libs might be later, but might not be compatible
import unittest
from langchain_core.prompts import ChatPromptTemplate
from typing import Annotated, Literal, Union
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from IPython.display import Image, display
from pprint import pprint
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

#The code is adpated from
#adapted from https://www.kaggle.com/code/markishere/day-3-building-an-agent-with-langgraph

# The tool schema is added to the prompt now to improve the decisions and to enable the gamma model to work with the
# code all the way until the LLM is going to choose a tool given its prompt history (first message includes instructions)
# and then a user input.
# I added notes below where gamma model steps have to be programmatically handled to parse the user input
# and understand it in context of the recent history
# (it's instructive to see how much the LLM is doing in the gemini invoke call instead)

import mock_functions
AI_STUDIO_KEY = mock_functions.get_AI_STUDIO_API_KEY()
os.environ["GOOGLE_API_KEY"] = AI_STUDIO_KEY

MENU = """MENU: 
unsweetened almond milk
unsweetened coconut milk
unsweetened soy milk
water
vitamin-infused water
vegetable and bean bowl
vegetable and quinoa bowl
"""
class OrderState(TypedDict):
    messages: Annotated[list, add_messages]
    order: list[str]
    finished: bool
    modifiable_test:str

@tool
def get_menu() -> str:
  """get the latest menu

  Returns:
    the latest menu
  """
  print(f'get_menu\n')
  return MENU

@tool
def add_to_order(drink: str, modifiers: Iterable[str]) -> str:
  '''add to order

  Args:
    drink: a drink to add to the order
    modifiers: modifiers to the drink

  Returns:
    The updated order in progress.
  '''
  print(f'add_to_order.  type mod={type(modifiers)}\n')

@tool
def confirm_order() -> str:
  '''ask the user ot conform their order.

  Returns:
     users reply'''
  print(f'confirm_order\n')

@tool
def get_order() -> str:
  '''get the order

  Returns:
    the order
  '''
  print(f'get_order\n')

@tool
def clear_order():
  '''clear the order'''
  print(f'clean_order\n')

@tool
def place_order() -> int:
  ''' place the order

  Returns:
    minutes until the order ready '''
  print(f'place_order\n')

 # Auto-tools will be invoked automatically by the ToolNode
auto_tools = [get_menu]
tool_node = ToolNode(auto_tools)

# Order-tools will be handled by the order node.
order_tools = [add_to_order, confirm_order, get_order, clear_order, place_order]

rendered_tools = render_text_description(auto_tools + order_tools)

INSTR = f"""
You are a BaristaBot, an interactive cafe ordering system. A human will
talk to you about the available products you have and you will answer
any questions about menu items (and only about menu items - no
off-topic discussion, but you can chat about the products and their
history).  The customer will place an order for 1 or more items from
the menu, which you will structure and send to the ordering system
after confirming the order with the human.

Add items to the customer's order with add_to_order, and reset the
order with clear_order.  To see the contents of the order so far, call
get_order (this is shown to you, not the user)

Always confirm_order with the user (double-check) before calling
place_order. Calling confirm_order will display the order items to the
user and returns their response to seeing the list. Their response may
contain modifications.  Always verify and respond with drink and
modifier names from the MENU before adding them to the order.  If you
are unsure a drink or modifier matches those on the MENU, ask a
question to clarify or redirect.  You only have the modifiers listed on
the menu.  Once the customer has finished ordering items, Call
confirm_order to ensure it is correct then make any necessary updates
and then call place_order. Once place_order has returned, thank the
user and say goodbye!

The ordering system schema is defined as:
{rendered_tools}
"""

#for gemma, one has to include the function, that is tool) declarations as schema in the prompts.
models = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemma-3-27b-it']
#for testing, I have this set to the gemma model
model_name = models[2]

#BARISTABOT_SYSINT = ("system", INSTR) <-- Gemma does not work with "system" in the prompts
BARISTABOT_SYSINT = (INSTR)
WELCOME_MSG = f"Welcome to the BaristaBot cafe. Type `q` to quit.\nHere is our menu:\n {MENU}\nHow can I help you?"

class MyTestCase(unittest.TestCase):
  def test_something(self):

    # see args: https://python.langchain.com/api_reference/google_genai/llms/langchain_google_genai.llms.GoogleGenerativeAI.html#langchain_google_genai.llms.GoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
      model=model_name, temperature=0, max_tokens=None, timeout=None, max_retries=2,
      # other params...
    )

    def human_node(state: OrderState) -> OrderState:
      last_msg = state["messages"][-1]
      print(f"Model (human_node):{last_msg.content}\n")
      user_input = input("User: ")
      if user_input in {"q", "quit", "exit", "done", "goodbye"}:
        state["finished"] = True
      return state | {"messages": [("user", user_input)]}

    def maybe_exit_human_node(state: OrderState) -> Literal["chatbot", "__end__"]:
      """Route to the chatbot, unless it looks like the user is exiting."""
      print("Model (maybe_exit_human_node)")
      if state.get("finished", False):
        return END
      else:
        return "chatbot"

    def chatbot_with_tools(state: OrderState) -> OrderState:
      """The chatbot with tools. A simple wrapper around the model's own chat interface."""
      print("Model (chatbot_with_tools)")
      defaults = {"order": [], "finished": False}
      if state["messages"]:
        new_output = llm.invoke([BARISTABOT_SYSINT] + state["messages"])
      else:
        new_output = AIMessage(content=WELCOME_MSG)
      # Set up some defaults if not already set, then pass through the provided state,
      # overriding only the "messages" field.
      return defaults | state | {"messages": [new_output]}

    def order_node(state: OrderState) -> OrderState:
      """The ordering node. This is where the order state is manipulated."""
      print("Model (order_node)")
      tool_msg = state.get("messages", [])[-1]
      order = state.get("order", [])
      outbound_msgs = []
      order_placed = False

      for tool_call in tool_msg.tool_calls:
        print(f'TOOL_CALL {tool_call}\n')
        if tool_call["name"] == "add_to_order":
          # Each order item is just a string. This is where it assembled as "drink (modifiers, ...)".
          modifiers = tool_call["args"]["modifiers"]
          modifier_str = ", ".join(modifiers) if modifiers else "no modifiers"
          order.append(f'{tool_call["args"]["drink"]} ({modifier_str})')
          #add_to_order(tool_call["args"])
          response = "\n".join(order)
        elif tool_call["name"] == "confirm_order":
          # We could entrust the LLM to do order confirmation, but it is a good practice to
          # show the user the exact data that comprises their order so that what they confirm
          # precisely matches the order that goes to the kitchen - avoiding hallucination
          # or reality skew.
          # In a real scenario, this is where you would connect your POS screen to show the
          # order to the user.
          print("Your order:")
          if not order:
            print("  (no items)")
          for drink in order:
            print(f"  {drink}")
          response = input("Is this correct? ")
        elif tool_call["name"] == "get_order":
           response = "\n".join(order) if order else "(no order)"
        elif tool_call["name"] == "clear_order":
           order.clear()
           response = None
        elif tool_call["name"] == "place_order":
           order_text = "\n".join(order)
           print("Sending order to kitchen!")
           print(order_text)
           # TODO(you!): Implement cafe.
           order_placed = True
           response = randint(1, 5)  # ETA in minutes
        else:
           raise NotImplementedError(f'Unknown tool call: {tool_call["name"]}')
        # Record the tool results as tool messages.
        outbound_msgs.append(
          ToolMessage(
            content=response,
              name=tool_call["name"],
              tool_call_id=tool_call["id"],
          )
        )
      return {"messages": outbound_msgs, "order": order, "finished": order_placed}

    def maybe_route_to_tools(state: OrderState) -> str:
      """Route between chat and tool nodes if a tool call is made."""
      print("Model (maybe_route_to_tools)")
      if not (msgs := state.get("messages", [])):
        raise ValueError(f"No messages found when parsing state: {state}")

      msg = msgs[-1]

      if state.get("finished", False):
        # When an order is placed, exit the app. The system instruction indicates
        # that the chatbot should say thanks and goodbye at this point, so we can exit
        # cleanly.
        return END
      elif hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        # Route to `tools` node for any automated tool calls first.
        if any(tool["name"] in tool_node.tools_by_name.keys() for tool in msg.tool_calls):
          return "tools"
        else:
          return "ordering"
      else:
        return "human"


    llm_tools = llm

    #llm_with_tools = llm.bind_tools(auto_tools + order_tools)

    graph_builder = StateGraph(OrderState)

    # Nodes
    graph_builder.add_node("chatbot", chatbot_with_tools)
    graph_builder.add_node("human", human_node)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_node("ordering", order_node)
    # Chatbot -> {ordering, tools, human, END}
    graph_builder.add_conditional_edges("chatbot", maybe_route_to_tools)
    # Human -> {chatbot, END}
    graph_builder.add_conditional_edges("human", maybe_exit_human_node)

    # Tools (both kinds) always route back to chat afterwards.
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge("ordering", "chatbot")

    graph_builder.add_edge(START, "chatbot")
    graph_with_order_tools = graph_builder.compile()

    Image(graph_with_order_tools.get_graph().draw_mermaid_png())

    state = graph_with_order_tools.invoke({"messages": []}, {"recursion_limit": 100})
    pprint(state)

    tt = 2

if __name__ == '__main__':
  unittest.main()
