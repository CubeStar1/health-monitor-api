import uvicorn
from pydantic import BaseModel
from typing import List, Literal

class DBCredentials(BaseModel):
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str

class QueryRequest(BaseModel):
    question: str
    db_credentials: DBCredentials
    llm_choice: Literal["openai", "gemini", "local"] = "openai"

class DBStructureRequest(BaseModel):
    db_credentials: DBCredentials

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    db_credentials: DBCredentials
    llm_choice: Literal["openai", "gemini", "local"] = "openai"
    stream: bool = False

class RAGQueryRequest(BaseModel):
    query: str
    llm_choice: Literal["openai", "gemini", "local"] = "openai"
    stream: bool = False