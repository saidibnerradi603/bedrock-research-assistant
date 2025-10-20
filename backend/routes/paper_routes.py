from fastapi import APIRouter, UploadFile, File
from controllers import PaperController
from schemas import PaperProcessResponse, PaperStatusResponse

router = APIRouter(prefix="/api/papers", tags=["papers"])
controller = PaperController()


@router.post("/upload-and-process", response_model=PaperProcessResponse, status_code=201)
async def upload_and_process_paper(
    file: UploadFile = File(..., description="PDF file to upload and process (max 5MB)")
):
    
    return await controller.upload_and_process_paper(file)


@router.get("/{paper_id}/status", response_model=PaperStatusResponse)
async def get_paper_status(paper_id: str):
   
    return await controller.get_paper_status(paper_id)
