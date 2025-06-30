from typing import Literal
from llm import open_ai, gemini, local
from fastapi import HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from config import OPENAI_API_KEY, GOOGLE_API_KEY, OPENAI_MODEL, GEMINI_MODEL


def format_response_with_llm(user_query: str, sql_query: str, query_results: str, llm_choice: str) -> str:
    prompt = f"""
    As HealthHub, your task is to analyze the following SQL query results and present them in a clear, insightful, and user-friendly manner, directly addressing the user's original question.

    The user asked:
    
    {user_query}
    

    And the SQL query executed to help answer this returned:
    
    {query_results}
    

    Please provide a concise analysis of these results, specifically in the context of the user's query. Focus on key health-related trends, patterns, or notable information that directly help answer their question. Your response should be easy to understand and informative.

    **Formatting Guidelines (use Markdown):**
    - **Main Title:** Start with a clear, descriptive main title for the analysis (e.g., "# Analysis of Your Recent Heart Rate Data", "# Summary of Today's Food Consumption").
    - **Headers:** Use sub-headers (e.g., "### Key Observations", "### Detailed Breakdown") for different sections of your analysis.
    - **Key Points:** Utilize bullet points (`-`) or numbered lists (`1.`) for specific findings or observations.
    - **Emphasis:** Use bold (`**text**`) or italic (`*text*`) for emphasis where appropriate.
    - **Data Presentation:** If presenting numerical data or lists of items from the results, consider using markdown tables or formatted code blocks (```) for clarity.
    - **Food Items:** If the results pertain to food consumption and include image URLs, try to render the food items and their images in a markdown table. For example:
    

    Your goal is to transform the raw data into a meaningful summary that empowers the user with insights about their health or diet. Ensure the language is supportive and geared towards promoting well-being.
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