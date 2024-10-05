from typing import Literal
from llm import open_ai, gemini, local

def choose_llm(llm_choice: Literal["openai", "gemini", "local"]):
    if llm_choice == "openai":
        return open_ai.nl_to_sql_openai
    elif llm_choice == "gemini":
        return gemini.nl_to_sql_gemini
    elif llm_choice == "local":
        return local.nl_to_sql_local
    else:
        raise ValueError("Invalid LLM choice")