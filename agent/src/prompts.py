import file_fetcher

def get_disease_name_prompt(disease_name:str, version: str = "V1.0", language: str = "en") -> str:
  file_name="disease_name_instruction.txt"
  content = file_fetcher.get_resource(file_name=file_name, asset_type="text", version=version, language=language)
  return content.format(disease_name=disease_name)

def get_summarization_prompt(version: str = "V1.0", language: str = "en") -> str:
  file_name = "summarization_instruction.txt"
  return file_fetcher.get_resource(file_name=file_name, asset_type="text", version=version, language=language)

def get_welcome_msg(version: str = "V1.0", language: str = "en"):
  file_name = "welcome_msg.txt"
  return file_fetcher.get_resource(file_name=file_name, asset_type="text", version=version, language=language)

def get_feedback_query(version: str = "V1.0", language: str = "en"):
  file_name = "feedback_query.txt"
  return file_fetcher.get_resource(file_name=file_name, asset_type="text", version=version, language=language)

def get_eval_instruction(version: str = "V1.0", language: str = "en"):
  '''
  get an instruction for Pointwise summarization quality.  The string needs to
  be formatted with arguments for prompt and response.

  Args:
    version: the resource version number

  Returns:
    instruction to give to an LLM to evaluate another LLM's reponse to a prompt

  References:
    https://www.kaggle.com/code/markishere/day-1-evaluation-and-structured-output
    https://cloud.google.com/vertex-ai/generative-ai/docs/models/metrics-templates#pairwise_coherence
  '''
  file_name = "eval_instruction.txt"
  return file_fetcher.get_resource(file_name=file_name, asset_type="text", version=version, language=language)