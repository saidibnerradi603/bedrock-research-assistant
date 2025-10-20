import time
from utils import S3Client, MarkdownChunker
from services.embedding_service import EmbeddingService
from services.vector_store_service import VectorStoreService
from schemas import EmbedStoreResponse
from config import get_settings
import logging

logger = logging.getLogger(__name__)


class EmbedStoreService:
    
    def __init__(self):
        self.s3_client = S3Client()
        self.chunker = MarkdownChunker()
        self.embedding_service = EmbeddingService()
        self.vector_store_service = VectorStoreService(self.embedding_service.get_embeddings())
        self.settings = get_settings()
    
    def embed_and_store_paper(self, paper_id: str) -> EmbedStoreResponse:
       
        start_time = time.time()
        
        logger.info(f"Checking if paper {paper_id} already exists in Pinecone")
        paper_exists, existing_vector_count = self.vector_store_service.check_paper_exists(paper_id)
        
        if paper_exists:
            logger.info(f"Paper {paper_id} already embedded with {existing_vector_count} vectors")
            processing_time = time.time() - start_time
            
            return EmbedStoreResponse(
                paper_id=paper_id,
                total_chunks=existing_vector_count,
                total_vectors=existing_vector_count,
                processing_time_seconds=round(processing_time, 2),
                message="Paper already embedded and stored in vector database"
            )
        
        markdown_s3_key = f"{self.settings.s3_parsed_markdown_prefix}/{paper_id}/paper.md"
        
        logger.info(f"Downloading markdown from S3: {markdown_s3_key}")
        
        if not self.s3_client.file_exists(markdown_s3_key):
            raise Exception(f"Markdown file not found for paper_id: {paper_id}")
        
        markdown_content = self.s3_client.download_file(markdown_s3_key).decode('utf-8')
        
        logger.info(f"Chunking markdown for paper {paper_id}")
        chunks = self.chunker.chunk_markdown(
            markdown_content=markdown_content,
            paper_id=paper_id,
            source=markdown_s3_key
        )
        
        from langchain_core.documents import Document
        documents = [
            Document(
                page_content=chunk.content,
                metadata={
                    "paper_id": chunk.metadata.paper_id,
                    "chunk_index": chunk.metadata.chunk_index,
                    "source": chunk.metadata.source
                }
            )
            for chunk in chunks
        ]
        
        logger.info(f"Generating embeddings and storing in Pinecone for paper {paper_id}")
        vector_ids = self.vector_store_service.add_documents_batch(documents, batch_size=100)
        
        processing_time = time.time() - start_time
        
        logger.info(f"Vectorized paper {paper_id}: {len(chunks)} chunks, {len(vector_ids)} vectors")
        
        return EmbedStoreResponse(
            paper_id=paper_id,
            total_chunks=len(chunks),
            total_vectors=len(vector_ids),
            processing_time_seconds=round(processing_time, 2),
            message="Paper embedded and stored successfully"
        )
