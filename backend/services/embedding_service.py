from langchain_aws import BedrockEmbeddings
from config import get_settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    
    def __init__(self):
        settings = get_settings()
        
        self.embeddings = BedrockEmbeddings(
            model_id=settings.bedrock_embedding_model,
            region_name=settings.aws_default_region,
            aws_access_key_id=settings.access_key_id,
            aws_secret_access_key=settings.secret_access_key
        )
    
    def get_embeddings(self):
        return self.embeddings
