from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from config import get_settings
from schemas import TextChunk, ChunkMetadata


class MarkdownChunker:
    
    def __init__(self):
        settings = get_settings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=[
                "\n\n\n\n",    
                "\n\n\n",      
                "\n\n",        
                "\n### ",      
                "\n## ",      
                "\n# ",       
                "\n---\n",   
                "\n\n---",     
                "$$\n\n",      
                "\n$$",      
                ". ",          
                ".\n",         
                "\n",          
                " ",           
                ""
            ],
            length_function=len,
            is_separator_regex=False,
        )
    
    def chunk_markdown(self, markdown_content: str, paper_id: str, source: str = "research_paper") -> List[TextChunk]:
       
        doc = Document(
            page_content=markdown_content,
            metadata={"source": source, "paper_id": paper_id}
        )
        
        split_docs = self.splitter.split_documents([doc])
        
        chunks = []
        for idx, split_doc in enumerate(split_docs):
            chunk = TextChunk(
                content=split_doc.page_content,
                metadata=ChunkMetadata(
                    paper_id=paper_id,
                    chunk_index=idx,
                    source=source
                )
            )
            chunks.append(chunk)
        
        return chunks
