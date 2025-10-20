import json
from mistralai import Mistral
from typing import Dict
from config import get_settings
import logging

logger = logging.getLogger(__name__)


class OCRService:
    """Service for processing PDFs using Mistral OCR"""
    
    def __init__(self):
        settings = get_settings()
        self.client = Mistral(api_key=settings.mistral_api_key)
    
    def process_pdf_from_url(self, pdf_url: str) -> Dict:
        """
        Process PDF from URL using Mistral OCR
        
        Args:
            pdf_url: Public URL to PDF document
            
        Returns:
            Dictionary containing OCR response with pages and markdown
        """
        try:
            pdf_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": pdf_url
                },
                include_image_base64=False
            )
            
            response_dict = json.loads(pdf_response.model_dump_json())
            logger.info(f"Successfully processed PDF from URL: {pdf_url}")
            return response_dict
            
        except Exception as e:
            logger.error(f"Failed to process PDF from URL: {e}")
            raise
    
    @staticmethod
    def extract_combined_markdown(ocr_response: Dict) -> str:
        """
        Extract and combine markdown from all pages
        
        Args:
            ocr_response: OCR response dictionary
            
        Returns:
            Combined markdown string from all pages
        """
        combined_md = []
        for page in ocr_response.get("pages", []):
            markdown_text = page.get("markdown", "")
            if markdown_text:
                combined_md.append(markdown_text)
        
        return "\n\n".join(combined_md)
    
    @staticmethod
    def get_page_count(ocr_response: Dict) -> int:
        """Get total number of pages in OCR response"""
        return len(ocr_response.get("pages", []))
