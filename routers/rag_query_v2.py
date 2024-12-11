from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, UUID4
from typing import List, Optional, Literal

from supabase import create_client, Client
import cohere

from utils.formatting import format_rag_response
from config import SUPABASE_URL, SUPABASE_KEY, COHERE_API_KEY

router = APIRouter()
security = HTTPBearer()

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

class RAGQueryRequest(BaseModel):
    query: str
    match_count: int = 5
    llm_choice: Literal["openai", "gemini", "local"] = "openai"
    user_id: UUID4

def generate_embedding(text: str) -> List[float]:
    response = co.embed(texts=[text], model="embed-english-v3.0", input_type="search_document")
    return response.embeddings[0]

def query_embeddings(query_embedding: List[float], match_count: int, user_id: UUID4):
    print(f"Calling RPC with params: match_count={match_count}, user_id={user_id}")
    try:
        response = supabase.rpc(
            'query_embeddings_v3',
            {
                'query_embedding': query_embedding,
                'match_count': match_count,
                'user_id': str(user_id)
            }
        ).execute()
        return response.data
    except Exception as e:
        print(f"Full error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rag-query-v2")
async def rag_query(request: RAGQueryRequest):
    try:
        # Generate embedding for the query
        query_embedding = generate_embedding(request.query)
        print(request)

        # Perform similarity search with user_id from request
        search_results = query_embeddings(query_embedding, request.match_count, request.user_id)

        # If no results found, return early
        if not search_results:
            return {
                "query": request.query,
                "context": "",
                "response": "No relevant documents found for your query."
            }

        # Extract relevant context with location information
        context = "\n".join([result['text_content'] for result in search_results])
        
        # Create context sources information
        context_sources = [{
            'file_id': result['file_id'],
            'chunk_index': result['chunk_index'],
            'total_chunks': result['total_chunks'],
            'similarity': result['similarity']
        } for result in search_results]

        # Use the format_rag_response function
        response = format_rag_response(request.query, context, request.llm_choice)

        return {
            "query": request.query,
            "context": context,
            "response": response,
            "sources": context_sources
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))