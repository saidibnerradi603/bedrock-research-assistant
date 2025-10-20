import uuid
import time
import hashlib
from utils import S3Client
from services.ocr_service import OCRService
from services.embedding_service import EmbeddingService
from services.vector_store_service import VectorStoreService
from schemas import PaperProcessResponse
from config import get_settings
import logging

logger = logging.getLogger(__name__)


class PaperService:
    """Service for handling paper upload and processing"""
    
    def __init__(self):
        self.s3_client = S3Client()
        self.ocr_service = OCRService()
        self.settings = get_settings()
        # Initialize vector store service for duplicate checking
        self.embedding_service = EmbeddingService()
        self.vector_store_service = VectorStoreService(self.embedding_service.get_embeddings())
    
    def _compute_file_hash(self, file_content: bytes) -> str:
        """Compute SHA256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()
    
    def _check_duplicate(self, file_hash: str) -> tuple[bool, str | None, str | None, int, bool]:
        """
        Check if paper with same hash already exists and is fully processed
        
        Verifies:
        1. Hash index exists in S3
        2. Markdown file exists in S3
        3. Paper is embedded in Pinecone (optional check)
        
        Returns:
            (is_duplicate, existing_paper_id, existing_markdown_s3_key, vector_count, is_embedded)
        """
        hash_index_key = f"{self.settings.s3_hash_index_prefix}/{file_hash}.txt"
        
        if not self.s3_client.file_exists(hash_index_key):
            return False, None, None, 0, False
        
        try:
            # Read existing paper metadata from hash index
            metadata = self.s3_client.download_file(hash_index_key).decode('utf-8')
            paper_id, markdown_s3_key = metadata.split('|')
            logger.info(f"Hash index found: hash={file_hash}, paper_id={paper_id}")
            
            # Verify markdown file actually exists in S3
            if not self.s3_client.file_exists(markdown_s3_key):
                logger.warning(f"Hash index exists but markdown missing for paper {paper_id}. Treating as non-duplicate.")
                # Clean up orphaned hash index
                try:
                    self.s3_client.delete_file(hash_index_key)
                    logger.info(f"Deleted orphaned hash index: {hash_index_key}")
                except Exception as e:
                    logger.error(f"Failed to delete orphaned hash index: {e}")
                return False, None, None, 0, False
            
            # Check if paper is embedded in Pinecone
            is_embedded, vector_count = self.vector_store_service.check_paper_exists(paper_id)
            
            logger.info(f"Duplicate detected: paper_id={paper_id}, embedded={is_embedded}, vectors={vector_count}")
            return True, paper_id, markdown_s3_key, vector_count, is_embedded
            
        except Exception as e:
            logger.error(f"Error checking duplicate for hash {file_hash}: {e}")
            return False, None, None, 0, False
    
    def _save_hash_index(self, file_hash: str, paper_id: str, markdown_s3_key: str):
        """Save hash index for duplicate detection"""
        hash_index_key = f"{self.settings.s3_hash_index_prefix}/{file_hash}.txt"
        metadata = f"{paper_id}|{markdown_s3_key}"
        self.s3_client.upload_file(
            file_content=metadata.encode('utf-8'),
            s3_key=hash_index_key,
            content_type="text/plain"
        )
    
    def upload_and_process_paper(self, file_content: bytes, filename: str) -> PaperProcessResponse:
        """
        Upload PDF to S3 and process it with OCR
        
        Args:
            file_content: PDF file bytes
            filename: Original filename
            
        Returns:
            PaperProcessResponse with processing results
        """
        start_time = time.time()
        
        # Compute file hash for duplicate detection
        file_hash = self._compute_file_hash(file_content)
        logger.info(f"File hash: {file_hash}")
        
        # Check for duplicates with comprehensive validation
        is_duplicate, existing_paper_id, existing_markdown_s3_key, vector_count, is_embedded = self._check_duplicate(file_hash)
        
        if is_duplicate:
            # Return existing paper info without reprocessing
            logger.info(f"Duplicate paper detected: paper_id={existing_paper_id}, embedded={is_embedded}, vectors={vector_count}")
            
            processing_time = time.time() - start_time
            
            # Build informative message based on embedding status
            if is_embedded:
                message = f"Paper already processed and embedded ({vector_count} vectors in database)"
            else:
                message = "Paper already processed (not yet embedded - use embed-store endpoint)"
            
            return PaperProcessResponse(
                paper_id=existing_paper_id,
                markdown_s3_key=existing_markdown_s3_key,
                total_pages=0,  # We don't store page count, could be enhanced
                processing_time_seconds=round(processing_time, 2),
                message=message
            )
        
        # Generate paper ID for new paper
        paper_id = str(uuid.uuid4())
        raw_pdf_s3_key = f"{self.settings.s3_raw_pdf_prefix}/{paper_id}/{filename}"
        
        # Upload PDF to S3
        logger.info(f"Uploading paper {paper_id} to S3: {raw_pdf_s3_key}")
        self.s3_client.upload_file(
            file_content=file_content,
            s3_key=raw_pdf_s3_key,
            content_type="application/pdf"
        )
        
        # Generate presigned URL for OCR processing
        logger.info(f"Generating presigned URL for paper {paper_id}")
        presigned_url = self.s3_client.get_presigned_url(raw_pdf_s3_key, expiration=3600)
        
        if not presigned_url:
            raise Exception("Failed to generate presigned URL for PDF")
        
        # Process with Mistral OCR using URL
        logger.info(f"Processing PDF with Mistral OCR for paper {paper_id}")
        ocr_response = self.ocr_service.process_pdf_from_url(presigned_url)
        
        # Extract combined markdown
        combined_markdown = self.ocr_service.extract_combined_markdown(ocr_response)
        total_pages = self.ocr_service.get_page_count(ocr_response)
        
        # Save markdown to S3
        markdown_s3_key = f"{self.settings.s3_parsed_markdown_prefix}/{paper_id}/paper.md"
        self.s3_client.upload_file(
            file_content=combined_markdown.encode('utf-8'),
            s3_key=markdown_s3_key,
            content_type="text/markdown"
        )
        
        # Save hash index for future duplicate detection
        self._save_hash_index(file_hash, paper_id, markdown_s3_key)
        
        processing_time = time.time() - start_time
        
        logger.info(f"Processed paper {paper_id}: {total_pages} pages")
        
        return PaperProcessResponse(
            paper_id=paper_id,
            markdown_s3_key=markdown_s3_key,
            total_pages=total_pages,
            processing_time_seconds=round(processing_time, 2),
            message="Paper uploaded and processed successfully"
        )
    
    def get_paper_status(self, paper_id: str) -> dict:
        """
        Get comprehensive status of a paper
        
        Args:
            paper_id: Paper identifier
            
        Returns:
            Dictionary with paper status information
        """
        # Check if markdown exists in S3
        markdown_s3_key = f"{self.settings.s3_parsed_markdown_prefix}/{paper_id}/paper.md"
        markdown_exists = self.s3_client.file_exists(markdown_s3_key)
        
        # Check if paper is embedded in Pinecone
        is_embedded, vector_count = self.vector_store_service.check_paper_exists(paper_id)
        
        # Determine overall existence
        exists = markdown_exists or is_embedded
        
        # Build status message
        if not exists:
            message = "Paper not found in system"
        elif markdown_exists and is_embedded:
            message = f"Paper fully processed and embedded ({vector_count} vectors)"
        elif markdown_exists and not is_embedded:
            message = "Paper processed but not yet embedded"
        else:
            message = "Paper embedded but markdown missing (inconsistent state)"
        
        logger.info(f"Paper {paper_id} status: exists={exists}, markdown={markdown_exists}, embedded={is_embedded}, vectors={vector_count}")
        
        return {
            "paper_id": paper_id,
            "exists": exists,
            "markdown_exists": markdown_exists,
            "is_embedded": is_embedded,
            "vector_count": vector_count,
            "message": message
        }
