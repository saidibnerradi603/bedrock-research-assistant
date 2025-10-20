from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from controllers.embed_store_controller import EmbedStoreController
from schemas import EmbedStoreResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/papers", tags=["papers"])
controller = EmbedStoreController()


class EmbedStoreRequest(BaseModel):
    paper_id: str = Field(..., description="Paper identifier from upload-and-process endpoint")


@router.post("/embed-store", response_model=EmbedStoreResponse, status_code=200)
async def embed_and_store_paper(request: EmbedStoreRequest):
    """
    Embed and store paper in vector database (synchronous operation)
    """
    try:
        logger.info(f"Starting embedding process for paper {request.paper_id}")
        
        response = await controller.embed_and_store_paper(request.paper_id)
        
        logger.info(f"Completed embedding for paper {request.paper_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to embed paper: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to embed paper: {str(e)}")
