from fastapi import APIRouter, HTTPException, BackgroundTasks
import os
import tempfile
from supabase import create_client, Client
import google.generativeai as genai
import requests
from typing import List
from enum import Enum
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter

from utils.embedding import generate_embedding
from utils.custom_types import PDFAnalysisRequest, ImageAnalysis

class TranscriptionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

router = APIRouter()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
supabase_client: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Set up logging at the top of the file
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 100) -> List[str]:
    """
    Split text into chunks using LangChain's RecursiveCharacterTextSplitter
    """
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        logger.info(f"Successfully split text into {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logger.error(f"Error in chunk_text: {e}")
        raise

async def process_pdf(file_url: str, file_id: str, user_id: str):
    """Background task to process the PDF"""
    try:
        logger.info(f"Starting PDF processing for file_id: {file_id}")
        
        # Update status to processing
        supabase_client.table("transcriptions").update({
            "status": TranscriptionStatus.PROCESSING,
            "updated_at": "now()"
        }).match({"file_id": file_id}).execute()
        
        logger.info(f"Downloading PDF from URL for file_id: {file_id}")
        response = requests.get(file_url)
        if response.status_code != 200:
            raise Exception("Could not download PDF from provided URL")

        # Save the PDF to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            temp_pdf.write(response.content)
            logger.info(f"PDF saved to temporary file: {temp_pdf.name}")

        # Upload the PDF to Gemini
        pdf_file = genai.upload_file(temp_pdf.name)
        logger.info(f"PDF uploaded to Gemini for file_id: {file_id}")

        # Initialize the model and process
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = """
        Analyze this PDF document and return a JSON object with exactly these fields:
        {
            "text_content": "all extracted text here",
            "confidence_level": "High/Medium/Low",
            "languages": ["list", "of", "detected", "languages"],
            "ocr_quality": number_between_1_and_10
        }

        Important: Return ONLY the JSON object, no other text or formatting.
        """

        logger.info(f"Sending PDF to Gemini for analysis, file_id: {file_id}")
        response = model.generate_content([prompt, pdf_file])
        logger.info(f"Received response from Gemini for file_id: {file_id}")
        
        # Clean and parse the response
        try:
            # Clean the response text to ensure it's valid JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text.split('```json')[1]
            if response_text.endswith('```'):
                response_text = response_text.rsplit('```', 1)[0]
            response_text = response_text.strip()
            
            logger.debug(f"Cleaned response text: {response_text[:500]}...")
            analysis_result = ImageAnalysis.parse_raw(response_text)
            logger.info("Successfully parsed Gemini response as JSON")
        except Exception as parse_error:
            logger.warning(f"Failed to parse Gemini response as JSON: {parse_error}")
            # Create a more informative fallback with the actual text
            analysis_result = ImageAnalysis(
                text_content=response.text,  # Use the full response as text_content
                confidence_level="Low",  # Set to Low since parsing failed
                languages=["en"],
                ocr_quality=5  # Lower quality score due to parsing failure
            )
            logger.info("Created fallback analysis result")

        # Store the analysis result
        logger.info(f"Storing analysis result for file_id: {file_id}")
        result = supabase_client.table("image_analysis").insert({
            "file_id": file_id,
            "user_id": user_id,
            "text_content": analysis_result.text_content,
            "confidence_level": analysis_result.confidence_level,
            "languages": analysis_result.languages,
            "ocr_quality": analysis_result.ocr_quality,
        }).execute()
        logger.info("Analysis result stored successfully")

        # Process chunks and store embeddings with better error handling
        logger.info(f"Starting text chunking for file_id: {file_id}")
        try:
            chunks = chunk_text(analysis_result.text_content)
            logger.info(f"Created {len(chunks)} chunks from text")
            if chunks:  # Add check to ensure chunks were created
                logger.debug(f"First chunk preview: {chunks[0][:200]}...")
        except Exception as chunk_error:
            logger.error(f"Failed to chunk text: {chunk_error}")
            raise

        # Process chunks in smaller batches to avoid memory issues
        batch_size = 10  # Adjust based on your needs
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} of {(len(chunks) + batch_size - 1)//batch_size}")
            
            for j, chunk in enumerate(batch):
                chunk_index = i + j
                logger.info(f"Processing chunk {chunk_index + 1}/{len(chunks)}")
                try:
                    embedding = generate_embedding(chunk)
                    
                    embedding_result = supabase_client.table("embeddings").insert({
                        "file_id": file_id,
                        "chunk_index": chunk_index,
                        "embedding": embedding,
                        "text_content": chunk,
                        "total_chunks": len(chunks)
                    }).execute()
                    logger.info(f"Stored embedding for chunk {chunk_index + 1}")
                except Exception as e:
                    logger.error(f"Error processing chunk {chunk_index + 1}: {e}")
                    continue  # Skip failed chunks instead of stopping the whole process

        # Update status to completed
        logger.info(f"Updating status to completed for file_id: {file_id}")
        supabase_client.table("transcriptions").update({
            "status": TranscriptionStatus.COMPLETED,
            "updated_at": "now()"
        }).match({"file_id": file_id}).execute()

        # Clean up
        try:
            genai.delete_file(pdf_file.name)
            os.unlink(temp_pdf.name)
            logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")

    except Exception as e:
        logger.error(f"Error processing PDF: {e}", exc_info=True)
        # Update status to failed
        supabase_client.table("transcriptions").update({
            "status": TranscriptionStatus.FAILED,
            "error_message": str(e),
            "updated_at": "now()"
        }).match({"file_id": file_id}).execute()

@router.post("/analyze-pdf")
async def analyze_pdf_endpoint(
    request: PDFAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Endpoint to initiate PDF analysis. Returns immediately with a tracking ID
    while processing continues in the background.
    """
    if not request.file_url or not request.file_id or not request.user_id:
        raise HTTPException(status_code=400, detail="file_url, file_id and user_id are required")

    try:
        # Create initial transcription record
        transcription = supabase_client.table("transcriptions").insert({
            "file_id": request.file_id,
            "user_id": request.user_id,
            "status": TranscriptionStatus.PENDING,
            "file_url": request.file_url,
        }).execute()

        # Start processing in background
        background_tasks.add_task(
            process_pdf,
            request.file_url,
            request.file_id,
            request.user_id
        )

        return {
            "message": "PDF processing started",
            "file_id": request.file_id,
            "status": TranscriptionStatus.PENDING,
            "analysis": "to be done"
        }

    except Exception as e:
        print(f"Error initiating PDF analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))