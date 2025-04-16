#NOTE: this could be modified for batch requests
#  and in that case, might want to use pyMed
#NOTE: I couldn't find version information for the entrez code, so just note that this request and parsing worked in April 2025

#!pip install -q lxml
from lxml import etree
import HttpsRequester
from setup_logging import log_error
import time
from setup_logging import log_agent

def get_pubmed_request_url(pmid: str, NIH_API_KEY : str) -> str:
  '''
  makes the url for an API call to pubmed for the specific PMID and a response in XML.
  Args:
    pmid: the pubmed ID
  returns the request url to use
  '''
  #https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed\
  # &id=30224019&retstart=0&retmax=1&retmode=xml&rettext=xml\
  # &api_key=_______"

  if NIH_API_KEY is None:
    raise Exception("NIH_API_KEY cannot be none")

  #default return type is xml
  #https://www.ncbi.nlm.nih.gov/books/NBK25499/table/chapter4.T._valid_values_of__retmode_and/?report=objectonly
  return f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retstart=0&retmax=1' \
    + f'&api_key={NIH_API_KEY}'

def parse_and_filter(xml_resp : str) -> str:
  '''
  Args:
    an XML response from PubMed
    the current schema version is https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_250101.dtd
  Returns:
    the abstract as a string.  returns None if an exception occurred.
  '''
  import io
  string_io = io.StringIO()

  try:
    root = etree.XML(xml_resp)
    xpath_query = "//AbstractText"
    elements = root.xpath(xpath_query)

    if elements is None:
      return None

    for element in elements:
      text = element.text
      string_io.write(text)
      string_io.write("\n")
  except Exception as e:
    print(f"Error parsing xml: {e}")
    log_error("no_session_id", f"xml_parse|err={e}")
    return None
  return string_io.getvalue()

#TODO: consider how to replace w/ kaggle notebook secrets passing of api key
def get_article_abstract_from_pubmed(session_id : str, query_number : int, \
  pmid : str, NIH_API_KEY: str) -> str:
  start_ns = time.time_ns()
  url_str = get_pubmed_request_url(pmid, NIH_API_KEY)
  req = HttpsRequester.HttpsRequester()
  content = req.send_req(url_str)
  stop_ns = time.time_ns()
  elapsed_ns = stop_ns - start_ns
  log_agent(session_id=session_id, msg=f'q={query_number}|pmid={pmid}|pubmed_fetch_time={elapsed_ns}')
  abstract = parse_and_filter(content)
  return abstract


