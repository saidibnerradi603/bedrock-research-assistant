from langchain_aws import ChatBedrockConverse
from config import get_settings
import logging

logger = logging.getLogger(__name__)


class LLMService:
    
    def __init__(self):
        settings = get_settings()
        self.settings = settings
        
        self.llm = ChatBedrockConverse(
            model=settings.bedrock_chat_model,
            region_name=settings.aws_default_region,
            credentials_profile_name=None,
            aws_access_key_id=settings.access_key_id,
            aws_secret_access_key=settings.secret_access_key
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
