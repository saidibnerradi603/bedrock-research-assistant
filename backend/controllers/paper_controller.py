from fastapi import UploadFile, HTTPException
from services import PaperService
from schemas import PaperProcessResponse
from config import get_settings
import logging

logger = logging.getLogger(__name__)


class PaperController:
    """Controller for paper-related operations"""
    
    def __init__(self):
        self.paper_service = PaperService()
        self.settings = get_settings()
    
    async def upload_and_process_paper(self, file: UploadFile) -> PaperProcessResponse:
       
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Validate content type
        if file.content_type != 'application/pdf':
            raise HTTPException(status_code=400, detail="Invalid content type. Must be application/pdf")
        
        try:
            file_content = await file.read()
            
            # Validate file is not empty
            if len(file_content) == 0:
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            
            # Validate file size (max 5MB)
            max_size_mb = self.settings.max_file_size_mb
            max_size_bytes = max_size_mb * 1024 * 1024
            if len(file_content) > max_size_bytes:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File size exceeds maximum allowed size of {max_size_mb}MB"
                )
            
            response = self.paper_service.upload_and_process_paper(
                file_content=file_content,
                filename=file.filename
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading and processing paper: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process paper: {str(e)}")
    
    async def get_paper_status(self, paper_id: str):
       
        try:
            status = self.paper_service.get_paper_status(paper_id)
            return status
            
        except Exception as e:
            logger.error(f"Error getting paper status: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get paper status: {str(e)}")
