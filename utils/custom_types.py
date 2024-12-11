import uvicorn
from pydantic import BaseModel, Field
from typing import List,  Optional, Literal

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


class ImageAnalysisRequest(BaseModel):
    file: str
    file_name: str
    file_id: str
    user_id: str
class PDFAnalysisRequest(BaseModel):
    file_url: str
    file_id: str
    user_id: str

class ImageAnalysis(BaseModel):
    """Structured output for image analysis."""
    text_content: str = Field(description="All text found in the image")
    confidence_level: Optional[str] = Field(default=None,
                                            description="High, Medium, or Low confidence in transcription")
    text_locations: Optional[List[dict]] = Field(default=None, description="Locations of text in the image")
    languages: Optional[List[str]] = Field(default=None, description="Languages detected in the text")
    ocr_quality: Optional[int] = Field(
        default=None,
        description="Quality of OCR results on a scale of 1-10"
)

