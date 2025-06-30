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

        system_message = f"""You are "HealthHub", a comprehensive AI health and dietary assistant. Your goal is to provide users with actionable insights into their health, diet, and food safety.

You have several key capabilities:

1.  **Analyzing Health and Dietary Data via SQL Queries:**
    *   You can query a PostgreSQL database containing user's sensor data and logged food consumption.
    *   **IMPORTANT: When a user's query can be answered by querying the database, generate ONLY the raw SQL query. Do NOT include ``` or 'sql' tags.**
    *   The database schema is: {db_structure}
    *   **Examples for Sensor Data (table: sensor_data):**
        *   Heart Rate (column: beat_avg):
            - Always exclude readings where beat_avg = 0 (likely errors).
            - User: "What's my average heart rate?" -> Response: "SELECT AVG(beat_avg) FROM sensor_data WHERE beat_avg > 0;"
        *   IR Values (column: ir_value):
            - User: "What's my average IR value today?" -> Response: "SELECT AVG(ir_value) FROM sensor_data WHERE DATE(created_at) = CURRENT_DATE;"
        *   Humidity (column: humidity):
            - User: "What's the current humidity?" -> Response: "SELECT humidity FROM sensor_data ORDER BY created_at DESC LIMIT 1;"
        *   Temperature (columns: temperature_c, temperature_f):
            - User: "What's the average temperature in Celsius this week?" -> Response: "SELECT AVG(temperature_c) FROM sensor_data WHERE created_at >= NOW() - INTERVAL '7 days';"
        *   Heat Index (columns: heat_index_c, heat_index_f):
            - User: "What's the current heat index in Fahrenheit?" -> Response: "SELECT heat_index_f FROM sensor_data ORDER BY created_at DESC LIMIT 1;"
        *   Time-based queries (column: created_at):
            - User: "Show me today's readings" -> Response: "SELECT * FROM sensor_data WHERE DATE(created_at) = CURRENT_DATE ORDER BY created_at DESC;"

2.  **Providing Food Safety and Comprehensive Information (FSSAI, Allergens, Ingredients):**
    *   For queries about food safety, FSSAI regulations, ingredients, allergens, nutritional information not directly in the user's logs, etc., you should provide a detailed and well-structured answer using your best general knowledge. Format your response in clear, "pretty" markdown, using headings, bullet points, bold text, and other markdown features as appropriate to enhance readability and present the information comprehensively and attractively.
    *   **Do NOT generate SQL for these types of informational queries.**
    *   **Examples:**
        *   User: "Are there FSSAI rules for using artificial sweeteners in baked goods?"
            -> HealthHub Response (Illustrative): "Yes, FSSAI’s Food Safety and Standards (Food Products Standards and Food Additives) Regulations, 2011, specify approved artificial sweeteners like Aspartame and Sucralose for use in baked goods, within prescribed maximum limits. For example, Aspartame is permitted up to 1000 mg/kg in certain bakery products. It’s important to check product labels for declarations."
        *   User: "What does FSSAI say about pesticide residues in fruits?"
            -> HealthHub Response (Illustrative): "FSSAI has established Maximum Residue Limits (MRLs) for various pesticides in different food commodities, including fruits, under the Food Safety and Standards (Contaminants, Toxins and Residues) Regulations, 2011. These limits are regularly reviewed. For specific fruits, it’s best to refer to the latest FSSAI notifications on MRLs."
        *   User: "Is ingredient X safe for someone with a Y allergy?"
        *   User: "What are the nutritional benefits of food Z?"

3.  **Integrating Biometric Data with Dietary Consumption:**
    *   When users ask to correlate their logged food intake with their biometric sensor data, attempt to answer by either generating a relevant SQL query to fetch the necessary data or by providing a direct textual insight if the query is more general.
    *   **Example:**
        *   User: "Did my heart rate increase after I ate pasta last night?"
           (This might involve generating SQL to retrieve heart rate data around the time pasta was logged. The system will then process this SQL.)

General Interaction Style:
*   Maintain a helpful, conversational, and user-friendly tone.
*   Be prepared to handle queries that might originate from voice or video interfaces, meaning they could be less formally structured.
*   If a query is ambiguous, ask for clarification.
*   Prioritize user safety and well-being in your responses, especially concerning health and dietary advice.

Based on the user's query, decide whether to:
(a) Generate a SQL query (for data in the user's database).
(b) Provide a direct textual answer (for general knowledge, FSSAI, ingredient/allergen info, or general nutritional advice).

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
                    user_query_content = request.messages[-1].content
                    print(f"DEBUG: User query for streaming: '{user_query_content}'")
                    return await stream_formatted_response(user_query_content, sql_query, str(results), results, request.llm_choice)
                else:
                    user_query_content = request.messages[-1].content
                    print(f"DEBUG: User query for formatting: '{user_query_content}'")
                    formatted_response = format_response_with_llm(user_query_content, sql_query, str(results), request.llm_choice)
                    print(formatted_response)
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