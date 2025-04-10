from urllib.parse import quote
import json

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
    + '&aggFilters=results%3Awith%2Cstatus%3Acom%2CstudyType%3Aint&fields=protocolSection&pageToken=NF0g5JuOlPUtyQ'

def parse_and_filter(json_resp : str):
  '''
  Args:
    a json response from clinicaltrials API v2
  Returns:
    results_list, nextPageToken
    where results_list is a list of dictionaries with keys: briefTitle, officialTitle, citations, and nextPageToken
    where citations is a list of dictionaries with keys pmid, citation.  the citation is
    a text of the publication title, authors, and article publication
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
  except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    raise e
  nextPageToken = json_data["nextPageToken"] if "nextPageToken" in json_data else None
  return out, nextPageToken
