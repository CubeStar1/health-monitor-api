from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def nl_to_sql_openai(question: str, table_info: str) -> str:
    prompt = f"""
    The sql code should not have ``` in beginning or end and sql word in output
    Given the following tables in a PostgreSQL database:

    {table_info}

    Convert the following natural language question to a SQL query:

    {question}

    Return only the SQL query, without any additional explanation.
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a SQL expert. Convert natural language questions to SQL queries."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()

def format_response_openai(prompt: str) -> str:
    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a data analyst providing insights on query results. Use markdown formatting in your responses."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()