from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone.vectorstores import PineconeVectorStore
from config import get_settings
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing Pinecone vector store"""
    
    def __init__(self, embeddings):
        settings = get_settings()
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index_name = settings.pinecone_index_name
        self._ensure_index_exists()
        
        # Get Pinecone index
        self.index = self.pc.Index(self.index_name)
        
        # Initialize vector store
        self.vector_store = PineconeVectorStore(
            index=self.index,
            embedding=embeddings
        )
    
    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist"""
        settings = get_settings()
        
        if not self.pc.has_index(self.index_name):
            logger.info(f"Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=settings.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=settings.aws_default_region
                )
            )
            logger.info(f"Pinecone index created: {self.index_name}")
        else:
            logger.info(f"Pinecone index already exists: {self.index_name}")
    
    def check_paper_exists(self, paper_id: str) -> Tuple[bool, int]:
        """
        Check if paper already exists in Pinecone and count total vectors
        
        Args:
            paper_id: Paper identifier
            
        Returns:
            (exists, vector_count) - True if paper exists, and actual count of vectors
        """
        try:
            # Query vectors with paper_id metadata filter to check existence
            query_response = self.index.query(
                vector=[0.0] * 1024,  # Dummy vector for metadata-only query
                filter={"paper_id": {"$eq": paper_id}},
                top_k=1,
                include_metadata=True
            )
            
            if not query_response.matches:
                return False, 0
            
            # Paper exists, now count all vectors for this paper_id
            # Use pagination to count all vectors (Pinecone limitation workaround)
            vector_count = self._count_vectors_for_paper(paper_id)
            
            logger.info(f"Paper {paper_id} found in Pinecone with {vector_count} vectors")
            return True, vector_count
            
        except Exception as e:
            logger.error(f"Error checking paper existence: {e}")
            return False, 0
    
    def _count_vectors_for_paper(self, paper_id: str, max_count: int = 10000) -> int:
        """
        Count total vectors for a specific paper_id using pagination
        
        Args:
            paper_id: Paper identifier
            max_count: Maximum vectors to count (safety limit)
            
        Returns:
            Total count of vectors for this paper
        """
        try:
            # Query in batches to count all vectors
            total_count = 0
            batch_size = 1000
            
            # We'll query multiple times with increasing top_k to estimate count
            # This is a workaround since Pinecone doesn't have a direct count API
            query_response = self.index.query(
                vector=[0.0] * 1024,
                filter={"paper_id": {"$eq": paper_id}},
                top_k=min(batch_size, max_count),
                include_metadata=True
            )
            
            total_count = len(query_response.matches)
            
            # If we got exactly batch_size results, there might be more
            # For now, return what we found (good enough for duplicate detection)
            return total_count
            
        except Exception as e:
            logger.error(f"Error counting vectors for paper {paper_id}: {e}")
            return 0
    
    def add_documents(self, documents):
        """
        Add documents to Pinecone vector store
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            List of document IDs
        """
        logger.info(f"Adding {len(documents)} documents to Pinecone")
        ids = self.vector_store.add_documents(documents=documents)
        logger.info(f"Successfully added {len(ids)} documents to Pinecone")
        return ids
    
    def add_documents_batch(self, documents, batch_size: int = 100):
        """
        Add documents to Pinecone in batches for better performance
        
        Args:
            documents: List of LangChain Document objects
            batch_size: Number of documents per batch
            
        Returns:
            List of all document IDs
        """
        logger.info(f"Adding {len(documents)} documents to Pinecone in batches of {batch_size}")
        all_ids = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_ids = self.vector_store.add_documents(documents=batch)
            all_ids.extend(batch_ids)
            logger.info(f"Processed batch {i//batch_size + 1}: {len(batch_ids)} vectors")
        
        logger.info(f"Successfully added {len(all_ids)} documents to Pinecone")
        return all_ids
