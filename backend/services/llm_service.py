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
            region_name=settings.aws_default_region
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
