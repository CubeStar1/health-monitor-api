from typing import Literal
from llm import open_ai, gemini, local
from fastapi import HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import os
from dotenv import load_dotenv
from config import OPENAI_API_KEY, GOOGLE_API_KEY, OPENAI_MODEL, GEMINI_MODEL

load_dotenv()


def choose_llm(llm_choice: Literal["openai", "gemini", "local"]):
    if llm_choice == "openai":
        return open_ai.nl_to_sql_openai
    elif llm_choice == "gemini":
        return gemini.nl_to_sql_gemini
    elif llm_choice == "local":
        return local.nl_to_sql_local
    else:
        raise ValueError("Invalid LLM choice")

def format_response_with_llm(sql_query: str, query_results: str, llm_choice: str) -> str:
    prompt = f"""
    Analyze the following query results and provide insights:

    Results: {query_results}

    Please provide a clear and concise analysis of the data. Focus on key trends, patterns, or notable information in the results. Use markdown formatting to structure your response, including:

    - Headers for main sections
    - Bullet points or numbered lists for key points
    - Bold or italic text for emphasis
    - Code blocks for any numerical data or examples

    Your analysis should be informative and easy to understand for someone looking at this data.
    """

    if llm_choice == "openai":
        formatted_response = open_ai.format_response_openai(prompt)
    elif llm_choice == "gemini":
        formatted_response = gemini.format_response_gemini(prompt)
    elif llm_choice == "local":
        formatted_response = local.format_response_local(prompt)
    else:
        raise ValueError("Invalid LLM choice")

    formatted_response += f"\n\n[SQL_QUERY]{sql_query}[/SQL_QUERY]"

    return formatted_response

async def stream_formatted_response(sql_query: str, query_results: str, tabular_data: list, llm_choice: str):
    prompt = f"""
    Analyze the following query results and provide insights:

    Results: {query_results}

    Please provide a clear and concise analysis of the data. Focus on key trends, patterns, or notable information in the results. Use markdown formatting to structure your response, including:

    - Headers for main sections
    - Bullet points or numbered lists for key points
    - Bold or italic text for emphasis
    - Code blocks for any numerical data or examples

    Your analysis should be informative and easy to understand for someone looking at this data.
    """

    if llm_choice == "openai":
        model = ChatOpenAI(
            temperature=0.7,
            model=OPENAI_MODEL,
            streaming=True,
            api_key=OPENAI_API_KEY,
        )
    elif llm_choice == "gemini":
        raise NotImplementedError("Gemini streaming not implemented yet")
    elif llm_choice == "local":
        raise NotImplementedError("Local LLM streaming not implemented yet")
    else:
        raise ValueError("Invalid LLM choice")

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a data analyst providing insights on query results. Use markdown formatting in your responses."),
        ("human", "{input}"),
    ])

    chain = chat_prompt | model | StrOutputParser()

    async def generate_formatted_response():
        try:
            async for chunk in chain.astream({"input": prompt}):
                yield f"{chunk}"
            yield f"[SQL_QUERY]{sql_query}[/SQL_QUERY]"
            yield f"[TABULAR_DATA]{json.dumps(tabular_data)}[/TABULAR_DATA]"
            yield "[DONE]"
        except Exception as e:
            yield f"Error: {str(e)}"
            yield "[DONE]"

    return StreamingResponse(generate_formatted_response(), media_type="text/event-stream")


def format_rag_response(query: str, context: str, llm_choice: Literal["openai", "gemini", "local"]) -> str:
    prompt = f"""
    Given the following context and query, provide a comprehensive and insightful response:

    Context: {context}

    Query: {query}

    Please provide a clear and concise response based on the given context. Your response should:

    - Directly address the query
    - Incorporate relevant information from the context
    - Use markdown formatting to structure your response, including:
      - Headers for main sections
      - Bullet points or numbered lists for key points
      - Bold or italic text for emphasis
      - Code blocks for any numerical data or examples

    Your response should be informative, easy to understand, and directly relevant to the query and provided context.
    """

    if llm_choice == "openai":
        model = ChatOpenAI(
            temperature=0.7,
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
        )
    elif llm_choice == "gemini":
        model = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            temperature=0.7,
            google_api_key=GOOGLE_API_KEY,
        )
    elif llm_choice == "local":
        raise NotImplementedError("Local LLM not implemented yet")
    else:
        raise ValueError("Invalid LLM choice")

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI assistant providing information based on given context. Use markdown formatting in your responses."),
        ("human", "{input}"),
    ])

    chain = chat_prompt | model | StrOutputParser()

    try:
        response = chain.invoke({"input": prompt})
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in LLM processing: {str(e)}")

async def stream_rag_response(query: str, context: str, llm_choice: Literal["openai", "gemini", "local"]):
    prompt = f"""
    Given the following context and query, provide a comprehensive and insightful response:

    Context: {context}

    Query: {query}

    Please provide a clear and concise response based on the given context. Your response should:

    - Directly address the query
    - Incorporate relevant information from the context
    - Use markdown formatting to structure your response, including:
      - Headers for main sections
      - Bullet points or numbered lists for key points
      - Bold or italic text for emphasis
      - Code blocks for any numerical data or examples

    Your response should be informative, easy to understand, and directly relevant to the query and provided context.
    """

    if llm_choice == "openai":
        model = ChatOpenAI(
            temperature=0.7,
            model=OPENAI_MODEL,
            streaming=True,
            api_key=OPENAI_API_KEY,
        )
    elif llm_choice == "gemini":
        raise NotImplementedError("Gemini streaming not implemented yet")
    elif llm_choice == "local":
        raise NotImplementedError("Local LLM streaming not implemented yet")
    else:
        raise ValueError("Invalid LLM choice")

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI assistant providing information based on given context. Use markdown formatting in your responses."),
        ("human", "{input}"),
    ])

    chain = chat_prompt | model | StrOutputParser()

    async def generate_rag_response():
        try:
            async for chunk in chain.astream({"input": prompt}):
                yield f"{chunk}"
            yield "[DONE]"
        except Exception as e:
            yield f"Error: {str(e)}"
            yield "[DONE]"

    return StreamingResponse(generate_rag_response(), media_type="text/event-stream")

