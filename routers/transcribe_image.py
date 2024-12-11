import uvicorn
from fastapi import APIRouter, HTTPException
import google.generativeai as genai
from supabase import create_client, Client
import os
from pydantic import BaseModel, Field
import base64

from utils.embedding import generate_embedding
from utils.transcription import create_image_analyzer
from utils.custom_types import ImageAnalysisRequest


router = APIRouter()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
supabase_client: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))




@router.post("/analyze-image")
async def analyze_image_endpoint(request: ImageAnalysisRequest):
    if not request.file or not request.file_id or not request.user_id:
        raise HTTPException(status_code=400, detail="file, file_id and user_id are required")

    try:
        # Decode the base64 file
        file_bytes = base64.b64decode(request.file)

        # Analyze the image
        analyze_image = create_image_analyzer(os.getenv("GOOGLE_API_KEY"))
        analysis_result = analyze_image(file_bytes)  # Pass bytes directly

        # Store the result in Supabase
        result = supabase_client.table("image_analysis").insert({
            "file_id": request.file_id,
            "user_id": request.user_id,
            "text_content": analysis_result.text_content,
            "confidence_level": analysis_result.confidence_level,
            "text_locations": analysis_result.text_locations,
            "languages": analysis_result.languages,
            "ocr_quality": analysis_result.ocr_quality
        }).execute()
        # Generate embedding
        embedding = generate_embedding(analysis_result.text_content)

        try:
            print("Generating embedding")
            # Store the embedding
            embedding_result = supabase_client.table("embeddings").insert({
                "file_id": request.file_id,
                "embedding": embedding,
                "text_content": analysis_result.text_content
            }).execute()
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))

        return {"message": "Image analyzed and stored successfully", "analysis": analysis_result.dict()}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

