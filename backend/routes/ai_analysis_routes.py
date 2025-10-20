from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from controllers.ai_analysis_controller import AIAnalysisController
from schemas.ai_analysis import SummaryResponse, QuizResponse

router = APIRouter(prefix="/api/papers", tags=["ai-analysis"])
controller = AIAnalysisController()


@router.get("/{paper_id}/summary", response_model=SummaryResponse)
async def generate_paper_summary(paper_id: str):
   
    return await controller.generate_summary(paper_id)


@router.get("/{paper_id}/quiz", response_model=QuizResponse)
async def generate_paper_quiz(paper_id: str, num_questions: int = 10):
   
    return await controller.generate_quiz(paper_id, num_questions)


@router.get("/{paper_id}/mindmap", response_class=HTMLResponse)
async def generate_paper_mindmap(paper_id: str):
    
    return await controller.generate_mindmap(paper_id)
