from pydantic import BaseModel, Field


class PaperProcessResponse(BaseModel):
    """Response model for paper processing"""
    paper_id: str = Field(..., description="Paper identifier")
    markdown_s3_key: str = Field(..., description="S3 key for parsed markdown")
    total_pages: int = Field(..., description="Number of pages processed")
    processing_time_seconds: float = Field(..., description="Processing duration")
    message: str = Field(..., description="Status message")


class EmbedStoreResponse(BaseModel):
    """Response model for vectorization"""
    paper_id: str = Field(..., description="Paper identifier")
    total_chunks: int = Field(..., description="Number of text chunks created")
    total_vectors: int = Field(..., description="Number of vectors stored in Pinecone")
    processing_time_seconds: float = Field(..., description="Processing duration")
    message: str = Field(..., description="Status message")


class ChunkMetadata(BaseModel):
    """Metadata for a text chunk"""
    paper_id: str
    chunk_index: int
    source: str


class TextChunk(BaseModel):
    """Represents a chunked text segment"""
    content: str = Field(..., description="Text content of the chunk")
    metadata: ChunkMetadata = Field(..., description="Chunk metadata")


class PaperStatusResponse(BaseModel):
    """Response model for paper status check"""
    paper_id: str = Field(..., description="Paper identifier")
    exists: bool = Field(..., description="Whether paper exists in system")
    markdown_exists: bool = Field(..., description="Whether markdown file exists in S3")
    is_embedded: bool = Field(..., description="Whether paper is embedded in vector database")
    vector_count: int = Field(..., description="Number of vectors in database")
    message: str = Field(..., description="Status message")

