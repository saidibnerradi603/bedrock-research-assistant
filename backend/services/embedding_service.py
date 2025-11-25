from langchain_aws import BedrockEmbeddings
from config import get_settings
import boto3
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    
    def __init__(self):
        settings = get_settings()
        
        session = boto3.Session(
            aws_access_key_id=settings.access_key_id,
            aws_secret_access_key=settings.secret_access_key,
            region_name=settings.aws_default_region
        )
        
        bedrock_client = session.client(
            service_name='bedrock-runtime',
            region_name=settings.aws_default_region
        )
        
        self.embeddings = BedrockEmbeddings(
            model_id=settings.bedrock_embedding_model,
            client=bedrock_client
        )
    
    def get_embeddings(self):
        return self.embeddings
