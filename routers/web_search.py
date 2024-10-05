from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from tavily import TavilyClient
from config import TAVILY_API_KEY, OPENAI_API_KEY, OPENAI_MODEL
from langchain.adapters.openai import convert_openai_messages
from langchain_community.chat_models import ChatOpenAI

router = APIRouter()

# Initialize Tavily client
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

class MedicalSearchRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    title: str
    url: str
    content: str
    image_url: Optional[str] = None

class MedicalSearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    report: str

@router.post("/medical-search", response_model=MedicalSearchResponse)
async def medical_search(request: MedicalSearchRequest):
    try:
        # Perform web search using Tavily API
        search_response = tavily_client.search(
            query=request.query,
            search_depth="advanced",
            include_images=True,
            include_answer=True,
            max_results=5
        )

        # Extract relevant information from the search response
        results = [
            SearchResult(
                title=result['title'],
                url=result['url'],
                content=result['content'],
                image_url=result.get('image_url')
            )
            for result in search_response['results']
        ]

        # Generate report using OpenAI
        content = search_response['results']
        prompt = [{
            "role": "system",
            "content": f'You are an AI medical research assistant. '
                       f'Your purpose is to write well-written, critically acclaimed, '
                       f'objective and structured medical reports based on given information.'
        }, {
            "role": "user",
            "content": f'Information: """{content}"""\n\n'
                       f'Using the above information, answer the following '
                       f'query: "{request.query}" in a detailed medical report -- '
                       f'Please use MLA format and markdown syntax.'
        }]

        lc_messages = convert_openai_messages(prompt)
        chat_model = ChatOpenAI(model=OPENAI_MODEL, openai_api_key=OPENAI_API_KEY)
        report = chat_model.invoke(lc_messages).content

        return MedicalSearchResponse(
            query=request.query,
            results=results,
            report=report
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))