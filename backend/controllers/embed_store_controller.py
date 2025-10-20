from fastapi import HTTPException
from services import EmbedStoreService
from schemas import EmbedStoreResponse
import logging

logger = logging.getLogger(__name__)


class EmbedStoreController:
    """Controller for embedding and vector store operations"""
    
    def __init__(self):
        self.embed_store_service = EmbedStoreService()
    
    async def embed_and_store_paper(self, paper_id: str) -> EmbedStoreResponse:
       
        try:
            response = self.embed_store_service.embed_and_store_paper(paper_id=paper_id)
            
            return response
            
        except Exception as e:
            logger.error(f"Error embedding and storing paper: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to embed and store paper: {str(e)}")
