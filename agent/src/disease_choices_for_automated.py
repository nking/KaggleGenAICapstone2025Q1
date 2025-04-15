import random
def select_disease_name_randomly():
  '''
  a method for use in automated running of the Kaggle notebook
  '''
  opts = ['heart disease', 'colorectal cancer', 'breast cancer', 'stomach cancer', 'liver cancer', \
   'pancreatic cancer', 'prostate cancer', 'lung cancer', 'ovarian cancer',\
   'stroke', 'bronchitis', 'asthma', 'pneumonia', "alzheimer's", "parkinson's", "dementia",\
   "diabetes type I", "diabetes type II"]
  return random.choice(opts)
