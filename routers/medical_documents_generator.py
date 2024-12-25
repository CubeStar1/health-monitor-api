from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import logging
import uuid
import traceback
from supabase import create_client, Client

from config import SUPABASE_URL, SUPABASE_ADMIN
from utils.medical_document_generator import generate_indian_details, generate_medical_content
from utils.pdf_generator import generate_pdf

# Configure logging and Supabase
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ADMIN)

router = APIRouter()

class MedicalDocumentRequest(BaseModel):
    document_type: str  # "prescription" | "lab_report" | "discharge_summary"
    count: int = 1
    llm_choice: str = "openai"  # "openai" | "gemini" | "local"

class MedicalDocumentResponse(BaseModel):
    document_ids: List[str]
    message: str

@router.post("/generate", response_model=MedicalDocumentResponse)
async def generate_medical_documents(request: MedicalDocumentRequest) -> MedicalDocumentResponse:
    """Generate sample medical documents using LLM and store them in Supabase"""
    try:
        logger.info(f"Starting document generation. Type: {request.document_type}, Count: {request.count}")
        document_ids = []
        
        for i in range(request.count):
            logger.info(f"Generating document {i+1} of {request.count}")
            
            # Generate content using specified LLM
            content = await generate_medical_content(request.document_type, request.llm_choice)
            
            # Generate PDF
            logger.debug("Generating PDF from content")
            pdf_content = await generate_pdf(content, request.document_type)
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"{request.document_type}_{file_id}.pdf"
            
            try:
                # Upload to Supabase Storage with content type
                file_options = {
                    "content-type": "application/pdf",
                    "content-disposition": f"attachment; filename={filename}"
                }
                
                storage_response = supabase.storage.from_('sample_medical_documents').upload(
                    filename,
                    pdf_content,
                    file_options=file_options
                )
                
                # Get the public URL
                file_url = supabase.storage.from_('sample_medical_documents').get_public_url(filename)
                logger.debug(f"File URL generated: {file_url}")
                
                # Store document metadata in Supabase
                document_data = {
                    "id": file_id,
                    "document_type": request.document_type,
                    "file_name": filename,
                    "file_url": file_url,
                    "doctor_name": content['doctor_name'],
                    "patient_name": content['patient_name'],
                    "hospital_name": content['hospital_name'],
                    "created_at": datetime.utcnow().isoformat(),
                    "document_date": content['date']
                }
                
                result = supabase.table("sample_medical_documents").insert(document_data).execute()
                document_ids.append(result.data[0]['id'])
                logger.info(f"Successfully generated document {i+1}: {file_id}")
                
            except Exception as e:
                logger.error(f"Error processing document {i+1}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing document {i+1}: {str(e)}"
                )
            
        return MedicalDocumentResponse(
            document_ids=document_ids,
            message=f"Successfully generated {request.count} {request.document_type} document(s)"
        )
        
    except Exception as e:
        logger.error(f"Failed to generate medical documents: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate medical documents: {str(e)}"
        )       