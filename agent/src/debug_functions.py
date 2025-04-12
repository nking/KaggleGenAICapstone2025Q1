import os
import article

def get_clinical_trials_for_disease(disease : str) -> list:
  return [{'briefTitle': 'Trial A', 'officialTitle': 'Trial A Official Title',
           'organization': "Organization A", \
           "citations": [{'pmid': "35730613", 'citation': 'citation 1 for A'}, \
                         {'pmid': "34987204", 'citation': 'citation 2 for A'}]}, \
          {'briefTitle': 'Trial B', 'officialTitle': 'Trial B Official Title',
           'organization': "Organization B", \
           "citations": [{'pmid': "20833684", 'citation': 'citation 1 for B'}, \
                         {'pmid': "20156960", 'citation': 'citation 2 for B'}]}, \
          ]

def get_article_abstract_from_pubmed(pmid : str) -> str:
  content = _read_pubmed_response()
  abstract = article.parse_and_filter(content)
  return abstract

def _read_pubmed_response(self):
    working_dir = os.environ.get('PWD')
    if working_dir.endswith("test"):
      working_dir += "/../../"
    flpath = working_dir + "/agent/testresources/entrez_pubmed_response_20250409.xml"
    try:
      with open(flpath, 'r') as infile:
        return infile.read().strip()
    except FileNotFoundError:
      print(f"{flpath} not found\n")
    except ValueError:
      print(f"Error: Invalid content in {flpath}.\n")

def get_NIH_API_KEY():
  working_dir = os.environ.get('PWD')
  if working_dir.endswith("test"):
    working_dir += "/../.."
  working_dir += "/agent/testresources"
  filepath = working_dir + "/NIH_API_KEY.txt"
  with open(filepath, 'r') as f:
    key = f.read().strip()
  return key

def get_AI_STUDIO_API_KEY():
  working_dir = os.environ.get('PWD')
  if working_dir.endswith("test"):
    working_dir += "/../.."
  working_dir += "/agent/testresources"
  filepath = working_dir + "/AI_Studio_API_KEY.txt"
  with open(filepath, 'r') as f:
    key = f.read().strip()
  return key