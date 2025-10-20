from pydantic import BaseModel, Field
from typing import Optional, List


class ChatRequest(BaseModel):
    """Request model for chat/QA"""
    paper_id: Optional[str] = Field(
        None, 
        description="Paper identifier (omit to search all papers)"
    )
    question: str = Field(
        ..., 
        description="Question about the paper content",
        min_length=3
    )
    top_k: int = Field(
        15, 
        description="Number of relevant chunks to retrieve",
        ge=1,
        le=50
    )


class SourceDocument(BaseModel):
    """Source document chunk"""
    content: str = Field(..., description="Text content of the chunk")
    metadata: dict = Field(..., description="Chunk metadata (paper_id, chunk_index, source)")


class ChatResponse(BaseModel):
    """Response model for chat/QA"""
    paper_id: Optional[str] = Field(None, description="Paper identifier (if querying specific paper)")
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="AI-generated answer with citations")
    source_documents: List[SourceDocument] = Field(
        ..., 
        description="Source chunks used to generate the answer"
    )
    message: str = Field(..., description="Status message")
