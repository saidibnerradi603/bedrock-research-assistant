from langchain_aws import ChatBedrockConverse
from config import get_settings
import boto3
import logging
import os
logger = logging.getLogger(__name__)


class LLMService:
    
    def __init__(self):
        settings = get_settings()
        self.settings = settings
        
      
        os.environ['AWS_ACCESS_KEY_ID'] = settings.access_key_id
        os.environ['AWS_SECRET_ACCESS_KEY'] = settings.secret_access_key
        os.environ['AWS_DEFAULT_REGION'] = settings.aws_default_region
        
        bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            aws_access_key_id=settings.access_key_id,
            aws_secret_access_key=settings.secret_access_key,
            region_name=settings.aws_default_region
        )
        
        self.llm = ChatBedrockConverse(
            model=settings.bedrock_chat_model,
            client=bedrock_client
        )
        
        # self.streaming_llm = ChatBedrockConverse(
        #     model=settings.bedrock_chat_model,
        #     region_name=settings.aws_default_region,
        #     streaming=True
        # )
    
    def get_llm(self):
        return self.llm
    
    # def get_streaming_llm(self):
    #     """Get streaming LLM instance"""
    #     return self.streaming_llm
