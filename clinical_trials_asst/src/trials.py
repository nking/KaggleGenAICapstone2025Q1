from urllib.parse import quote
import json
from HttpsRequester import HttpsRequester
import io
from setup_logging import log_error
import time
from setup_logging import log_agent

def get_trial_request_url(disease: str) -> str:
  '''
  makes the url for an API call to clinical trials US gov for completed trials that have results for the disease
  and have prevention or treatment (or synonyms) in their titles or documentation.
  see https://clinicaltrials.gov/data-api/api
  Args:
    disease: string of disease type.  e.g. lung cancer
  '''
  #curl -X GET "https://clinicaltrials.gov/api/v2/studies?format=json
  # &query.cond=lung+cancer
  # &query.term=prevention+or+treatment&filter.overallStatus=COMPLETED
  # &aggFilters=results%3Awith%2Cstatus%3Acom%2CstudyType%3Aint&fields=protocolSection&pageToken=NF0g5JuOlPUtyQ" -H "accept: application/json" \

  disease_enc = quote(disease)
  return f'https://clinicaltrials.gov/api/v2/studies?format=json&query.cond={disease_enc}' \
    + '&query.term=prevention+or+treatment&filter.overallStatus=COMPLETED' \
    + '&aggFilters=results%3Awith%2Cstatus%3Acom%2CstudyType%3Aint&fields=protocolSection'

def parse_and_filter_trials(json_resp : str):
  '''
  Args:
    a json response from clinicaltrials API v2
  Returns:
    results_list, nextPageToken
    where results_list is a list of dictionaries with keys: briefTitle, officialTitle, citations, and nextPageToken
    where citations is a list of dictionaries with keys pmid, citation.  the citation is
    a text of the publication title, authors, and article publication
    returns None for parse or load errors.
  '''
  out = []
  try:
    json_data = json.loads(json_resp)
    #['studies'] returns a list of dictionaries
    # ['protocolSection']['referencesModule']['references'] returns a list then select for "pmid"  there may be many
    #nextPageToken
    # ['protocolSection']['identificationModule']['briefTitle']
    # ['protocolSection']['identificationModule']['officialTitle']
    #TODO: parse to keep ['protocolSection']['referencesModule']['seeAlsoLinks']
    #print(json_data)
    #print(type(json_data))
    for study in json_data['studies']:
      citations = []
      pr = study['protocolSection']
      if 'referencesModule' in pr and 'references' in pr['referencesModule']:
        for pmid_dict in pr['referencesModule']['references']:
          if 'pmid' in pmid_dict:
            citations.append({"pmid":pmid_dict["pmid"], "citation": pmid_dict["citation"]})
      if len(citations) > 0:
        # parse for organization
        out.append({'briefTitle' : pr['identificationModule']['briefTitle'], \
          'officialTitle' : pr['identificationModule']['officialTitle'], \
          'organization' : pr['identificationModule']['organization']['fullName'],\
          'citations' : citations})
  except Exception as e:
    print(f"Error decoding JSON: {e}")
    log_error("no_session_id", f"err={e}")
    return None, None
  nextPageToken = json_data["nextPageToken"] if "nextPageToken" in json_data else None
  return out, nextPageToken

def format_citations(citations: list) -> str:
  string_io = io.StringIO()
  #TODO: could improve this to place names, title, publication information each on separate lines.
  for i, cit in enumerate(citations):
    string_io.write(f"\n{i}\n{cit['citation']}\n")
  return string_io.getvalue()

def format_trials(trials: list) -> str:
  string_io = io.StringIO()
  for i, cit in enumerate(trials):
    string_io.write(f"\n{i}:\nfull title: {cit['officialTitle']}\n")
    string_io.write(f"brief title: {cit['briefTitle']}\n")
    string_io.write(f"organization: {cit['organization']}\n")
  return string_io.getvalue()

def get_clinical_trials_for_disease(session_id : str, query_number : int, disease: str) -> list:
  start_ns = time.time_ns()
  url_str = get_trial_request_url(disease)
  req = HttpsRequester()
  content = req.send_req(url_str)
  stop_ns = time.time_ns()
  elapsed_ns = stop_ns - start_ns
  log_agent(session_id=session_id, msg=f'q={query_number}|disease={disease}|trials_fetch_time={elapsed_ns}')
  results_list, nextPageToken = parse_and_filter_trials(content)
  return results_list