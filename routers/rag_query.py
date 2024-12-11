from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Literal

from supabase import create_client, Client
import cohere

from utils.formatting import format_rag_response
from config import SUPABASE_URL, SUPABASE_KEY, COHERE_API_KEY

router = APIRouter()

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

class RAGQueryRequest(BaseModel):
    query: str
    match_count: int = 5
    llm_choice: Literal["openai", "gemini", "local"] = "openai"

def generate_embedding(text: str) -> List[float]:
    response = co.embed(texts=[text], model="embed-english-v3.0", input_type="search_document")
    return response.embeddings[0]

def query_embeddings(query_embedding: List[float], match_count: int):
    response = supabase.rpc(
        'query_embeddings',
        {
            'query_embedding': query_embedding,
            'match_count': match_count
        }
    ).execute()
    return response.data



@router.post("/rag-query")
async def rag_query(request: RAGQueryRequest):
    try:
        # Generate embedding for the query
        query_embedding = generate_embedding(request.query)

        # Perform similarity search
        search_results = query_embeddings(query_embedding, request.match_count)

        # Extract relevant context
        context = "\n".join([result['text_content'] for result in search_results])

        print(context)

        # Use the format_rag_response function
        response = format_rag_response(request.query, context, request.llm_choice)

        return {
            "query": request.query,
            "context": context,
            "response": response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))