def get_disease_name_prompt(disease_name) -> str:
  return f"""You are a librarian at the National Institutes of Health.
    Do you recognize the words "{disease_name}" as a valid disease name? 
    Answer yes or no."""