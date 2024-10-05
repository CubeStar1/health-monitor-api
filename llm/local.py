import requests
from config import LOCAL_LLM_URL

def nl_to_sql_local(question: str, table_info: str) -> str:
    prompt = f"""
    Given the following tables in a PostgreSQL database:

    {table_info}

    Convert the following natural language question to a SQL query:

    {question}

    Return only the SQL query, without any additional explanation.
    Also the sql code should not have ``` in beginning or end and sql word in output
    """

    response = requests.post(
        f"{LOCAL_LLM_URL}/v1/chat/completions",
        json={
            "model": "defog/sqlcoder-7b-2/sqlcoder-7b-q5_k_m.gguf",
            "messages": [
                {
                    "role": "system",
                    "content": prompt
                }
            ],
            "stream": False
        }
    )
    response = response.json()

    if response:
        return response['choices'][0]['message']['content'].strip()
    else:
        raise Exception("Error in local LLM request")

def format_response_local(prompt: str) -> str:
    response = requests.post(
        f"{LOCAL_LLM_URL}/v1/chat/completions",
        json={
            "model": "defog/sqlcoder-7b-2/sqlcoder-7b-q5_k_m.gguf",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a data analyst providing insights on query results. Use markdown formatting in your responses."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }
    )
    response_json = response.json()
    return response_json['choices'][0]['message']['content'].strip()