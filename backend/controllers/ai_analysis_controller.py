from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from services.ai_analysis_service import AIAnalysisService
from schemas.ai_analysis import SummaryResponse, QuizResponse
import logging

logger = logging.getLogger(__name__)


class AIAnalysisController:
    """Controller for AI analysis operations: summaries, quizzes, and mindmaps"""
    
    def __init__(self):
        self.ai_analysis_service = AIAnalysisService()
    
    async def generate_summary(self, paper_id: str) -> SummaryResponse:
        """Generate comprehensive summary for a paper"""
        try:
            result = self.ai_analysis_service.generate_summary(paper_id)
            return SummaryResponse(**result)
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate summary: {str(e)}"
            )
    
    async def generate_quiz(self, paper_id: str, num_questions: int = 10) -> QuizResponse:
        """Generate quiz questions for a paper"""
        try:
            result = self.ai_analysis_service.generate_quiz(paper_id, num_questions)
            return QuizResponse(**result)
            
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate quiz: {str(e)}"
            )
    
    async def generate_mindmap(self, paper_id: str) -> HTMLResponse:
        """Generate interactive mindmap for a paper"""
        try:
            result = self.ai_analysis_service.generate_mindmap(paper_id)
            return HTMLResponse(content=result["html_content"])
            
        except Exception as e:
            logger.error(f"Error generating mindmap: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate mindmap: {str(e)}"
            )
