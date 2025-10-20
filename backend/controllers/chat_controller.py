from fastapi import HTTPException
from services.chat_service import ChatService
from schemas.chat import ChatRequest, ChatResponse
import logging

logger = logging.getLogger(__name__)


class ChatController:
    """Controller for chat/QA operations"""
    
    def __init__(self):
        self.chat_service = ChatService()
    
    async def query_paper(self, request: ChatRequest) -> ChatResponse:
       
        try:
            response = self.chat_service.query_paper(
                paper_id=request.paper_id,
                question=request.question,
                top_k=request.top_k
            )
            
            return ChatResponse(
                paper_id=request.paper_id,
                question=response["query"],
                answer=response["result"],
                source_documents=response["source_documents"],
                message="Question answered successfully"
            )
            
        except Exception as e:
            logger.error(f"Error in query_paper: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to answer question: {str(e)}"
            )
    
    async def query_all_papers(self, request: ChatRequest) -> ChatResponse:
      
        try:
            response = self.chat_service.query_all_papers(
                question=request.question,
                top_k=request.top_k
            )
            
            return ChatResponse(
                paper_id=None,
                question=response["query"],
                answer=response["result"],
                source_documents=response["source_documents"],
                message="Question answered successfully across all papers"
            )
            
        except Exception as e:
            logger.error(f"Error in query_all_papers: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to answer question: {str(e)}"
            )
    
    
    async def query_all_papers_stream(self, request: ChatRequest):
      
        try:
            async for chunk in self.chat_service.query_all_papers_stream(
                question=request.question,
                top_k=request.top_k
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Error in query_all_papers_stream: {e}")
            yield f"Error: {str(e)}"
