import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_MODEL

genai.configure(api_key=GOOGLE_API_KEY)

def nl_to_sql_gemini(question: str, table_info: str) -> str:
    prompt = f"""
    Given the following tables in a PostgreSQL database, Also the sql code should not have ``` in beginning or end and sql word in output:

    {table_info}

    Convert the following natural language question to a SQL query:

    {question}

    Return only the SQL query, without any additional explanation.
    """

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    return response.text.strip()

def format_response_gemini(prompt: str) -> str:
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()