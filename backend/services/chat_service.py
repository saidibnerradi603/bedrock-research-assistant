from langchain_aws import ChatBedrockConverse
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from services.embedding_service import EmbeddingService
from services.vector_store_service import VectorStoreService
from config import get_settings
import boto3
import os
import logging

logger = logging.getLogger(__name__)


class ChatService:
    
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
        
        self.llm = ChatBedrockConverse(
            model=settings.bedrock_chat_model,
            client=bedrock_client
        )
        
        self.streaming_llm = ChatBedrockConverse(
            model=settings.bedrock_chat_model,
            client=bedrock_client,
            streaming=True
        )
        
        self.embedding_service = EmbeddingService()
        self.vector_store_service = VectorStoreService(self.embedding_service.get_embeddings())
        
        self.prompt_template = """
You are an expert research assistant analyzing academic papers. Your goal is to provide a thorough, accurate, and well-structured answer.

---

### 📚 Context from the Paper:
{context}

---

### ❓ Research Question:
{question}

---

### 🧭 Instructions:

1. **Start with the context provided.**
   - Use quotes, paraphrases, or references from the context to support your reasoning.
   - Be explicit when citing parts of the text (e.g., "The paper states that…").

2. **Then, if helpful, use your general academic and domain knowledge**
   to expand, interpret, or clarify ideas — but **clearly distinguish** this from what comes directly from the paper.
   - Example: "Beyond the paper's content, existing literature suggests that…"

3. **If the context lacks enough information to fully answer the question:**
   - State clearly that the context is incomplete or ambiguous.
   - Indicate what information is missing and how it limits the analysis.
   - You may still provide partial insights based on general understanding, clearly marked as such.

4. **If the question itself is unclear or underspecified:**
   - Propose reasonable interpretations.
   - Suggest specific follow-up questions that would help clarify the intent.

5. **Structure your answer clearly**.

6. **Maintain an academic tone** — objective, precise, and well-supported.

7. **After providing your main answer**, do the following:
   - Suggest **follow-up questions** that would deepen or extend the analysis.

8. **Your response may include:**
   - LaTeX math expressions (use $$E = mc^2$$ or inline $x$, $y$)
   - Markdown tables

---

### 🧩 Answer:
"""
        
        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )
    
    def query_paper(
        self, 
        paper_id: str, 
        question: str, 
        top_k: int = 15
    ) -> dict:
       
        try:
            logger.info(f"Querying paper {paper_id} with question: {question}")
            
            retriever = self.vector_store_service.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": top_k,
                    "filter": {"paper_id": {"$eq": paper_id}}
                }
            )
            
            qa_chain = RetrievalQA.from_llm(
                llm=self.llm,
                retriever=retriever,
                prompt=self.prompt,
                return_source_documents=True
            )
            
            logger.info(f"Executing RAG query for paper {paper_id}")
            response = qa_chain.invoke(question)
            
            logger.info(f"Successfully answered question for paper {paper_id}")
            
            return {
                "query": response.get("query", question),
                "result": response.get("result", ""),
                "source_documents": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in response.get("source_documents", [])
                ]
            }
            
        except Exception as e:
            logger.error(f"Error querying paper {paper_id}: {e}")
            raise
    
    def query_all_papers(
        self, 
        question: str, 
        top_k: int = 15
    ) -> dict:
        """
        Query across all papers (no paper_id filter)
        
        Args:
            question: User's question
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            dict with 'query', 'result', and 'source_documents'
        """
        try:
            logger.info(f"Querying all papers with question: {question}")
            
            retriever = self.vector_store_service.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": top_k}
            )
            
            qa_chain = RetrievalQA.from_llm(
                llm=self.llm,
                retriever=retriever,
                prompt=self.prompt,
                return_source_documents=True
            )
            
            logger.info("Executing RAG query across all papers")
            response = qa_chain.invoke(question)
            
            logger.info("Successfully answered question across all papers")
            
            return {
                "query": response.get("query", question),
                "result": response.get("result", ""),
                "source_documents": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in response.get("source_documents", [])
                ]
            }
            
        except Exception as e:
            logger.error(f"Error querying all papers: {e}")
            raise
