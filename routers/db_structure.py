from fastapi import APIRouter, HTTPException

from utils.custom_types import DBStructureRequest
from database import get_db_structure

router = APIRouter()

@router.post("/db-structure")
async def get_db_structure_endpoint(request: DBStructureRequest):
    try:
        structure = get_db_structure(request.db_credentials)
        return {"structure": structure}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))