from fastapi import APIRouter
from controllers.chat_controller import ChatController
from schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])
controller = ChatController()


@router.post("/query", response_model=ChatResponse)
async def query_paper(request: ChatRequest):
  
    if request.paper_id:
        return await controller.query_paper(request)
    else:
        return await controller.query_all_papers(request)



@router.post("/query-paper/{paper_id}", response_model=ChatResponse)
async def query_specific_paper(paper_id: str, question: str, top_k: int = 15):
    
    request = ChatRequest(
        paper_id=paper_id,
        question=question,
        top_k=top_k
    )
    return await controller.query_paper(request)
