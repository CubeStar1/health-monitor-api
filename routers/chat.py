from fastapi import APIRouter, HTTPException
from utils.custom_types import ChatRequest
import pandas as pd

from database import get_db_structure, execute_sql_query
from utils.formatting import format_response_with_llm
from utils.streaming import stream_formatted_response
from llm import open_ai, gemini, local
from config import OPENAI_MODEL, GEMINI_MODEL

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    print(request.dict())
    try:
        db_structure = get_db_structure(request.db_credentials)

        system_message = f"""You are a helpful AI assistant that can query a PostgreSQL database. 
        When generating SQL queries, do not include ``` or 'sql' tags. Only return the raw SQL query.
        Here's the database schema: {db_structure}
        """

        all_messages = [{"role": "system", "content": system_message}] + [m.dict() for m in request.messages]

        # Generate SQL query (non-streaming)
        if request.llm_choice == "openai":
            response = open_ai.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=all_messages,
                temperature=0,
            )
            sql_query = response.choices[0].message.content.strip()
        elif request.llm_choice == "gemini":
            model = gemini.genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content([m['content'] for m in all_messages])
            sql_query = response.text.strip()
        elif request.llm_choice == "local":
            response = local.requests.post(
                f"{local.LOCAL_LLM_URL}/v1/chat/completions",
                json={
                    "model": "defog/sqlcoder-7b-2/sqlcoder-7b-q5_k_m.gguf",
                    "messages": all_messages,
                    "stream": False
                }
            )
            response = response.json()
            if response:
                sql_query = response['choices'][0]['message']['content'].strip()
            else:
                raise HTTPException(status_code=500, detail="Error in local LLM request")
        else:
            raise ValueError("Invalid LLM choice")

        if "SELECT" in sql_query.upper():
            try:
                results = execute_sql_query(sql_query, request.db_credentials)
                print(results)
                df = pd.DataFrame(results)
                df.fillna("NULL", inplace=True)
                print(df.to_dict(orient="records"))

                if request.stream:
                    return await stream_formatted_response(sql_query, str(results), results, request.llm_choice)
                else:
                    formatted_response = format_response_with_llm(sql_query, str(results), request.llm_choice)
                    return {
                        "role": "assistant",
                        "content": formatted_response,
                        "tabular_data": df.to_dict(orient="records")
                    }
            except Exception as e:
                error_message = f"Error executing query: {str(e)}"
                if request.stream:
                    return await stream_formatted_response(sql_query, error_message, [], request.llm_choice)
                else:
                    formatted_response = format_response_with_llm(sql_query, error_message, request.llm_choice)
                    return {"role": "assistant", "content": formatted_response}
        else:
            return {"role": "assistant", "content": sql_query}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))