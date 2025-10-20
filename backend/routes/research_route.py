
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from agent.runner import ResearchRunner
from schemas.state import AgentConfig

router = APIRouter(
    prefix="/api/research",
    tags=["research"],
    responses={404: {"description": "Not found"}},
)

class ResearchRequest(BaseModel):
    query: str
    max_iterations: Optional[int] = 15
    min_search_results: Optional[int] = 8

class ResearchResponse(BaseModel):
    query: str
    document_content: str

@router.post("/query", response_model=ResearchResponse)
async def direct_research(request: ResearchRequest):
   
    try:
        config = AgentConfig(
            max_iterations=request.max_iterations,
            min_search_results=request.min_search_results
        )
        
        runner = ResearchRunner(output_dir=None)  # Set to None to prevent saving files
        
        print(f"🔍 Starting direct research on: {request.query}")
        result = runner.run_research(request.query, config)
        
        if result['summary']['has_document'] and result['state']['final_document']:
            document_content = ""
            
            if hasattr(result['state']['final_document'], 'content') and result['state']['final_document'].content:
                document_content = result['state']['final_document'].content
            else:
                document_content = runner._generate_markdown_document(result['state']['final_document'], result['state'])
            
            return ResearchResponse(
                query=request.query,
                document_content=document_content
            )
        else:
            raise HTTPException(status_code=500, detail="Research completed but no document was generated")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research error: {str(e)}")