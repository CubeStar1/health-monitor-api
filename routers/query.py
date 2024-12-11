from fastapi import APIRouter, HTTPException
from database import get_db_structure, execute_sql_query
from utils.custom_types import QueryRequest
from utils.options import choose_llm

router = APIRouter()

@router.post("/query")
async def query(request: QueryRequest):
    try:
        db_structure = get_db_structure(request.db_credentials)
        table_info_str = "\n".join(
            [f"Table: {table}, Columns: {', '.join(columns)}" for table, columns in db_structure.items()])

        nl_to_sql_func = choose_llm(request.llm_choice)

        sql_query = nl_to_sql_func(request.question, table_info_str)
        print(sql_query)

        results = execute_sql_query(sql_query, request.db_credentials)

        return {
            "question": request.question,
            "sql_query": sql_query,
            "results": results
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))