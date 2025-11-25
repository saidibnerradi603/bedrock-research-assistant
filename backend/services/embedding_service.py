from langchain_aws import BedrockEmbeddings
from config import get_settings
import boto3
import logging
import os

logger = logging.getLogger(__name__)


class EmbeddingService:
    
    def __init__(self):
        settings = get_settings()
        
        
        os.environ['AWS_ACCESS_KEY_ID'] = settings.access_key_id
        os.environ['AWS_SECRET_ACCESS_KEY'] = settings.secret_access_key
        os.environ['AWS_DEFAULT_REGION'] = settings.aws_default_region
        
        bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            aws_access_key_id=settings.access_key_id,
            aws_secret_access_key=settings.secret_access_key,
            region_name=settings.aws_default_region
        )
        
        self.embeddings = BedrockEmbeddings(
            model_id=settings.bedrock_embedding_model,
            client=bedrock_client
        )
    
    def get_embeddings(self):
        return self.embeddings
