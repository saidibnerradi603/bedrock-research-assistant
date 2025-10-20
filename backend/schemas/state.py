from typing import List, Dict, Any, Optional, TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel
from datetime import datetime


class SearchResult(BaseModel):
    """Represents a single search result."""
    title: str
    url: str
    content: str
    source: str  # 'tavily' or 'perplexity'
    relevance_score: Optional[float] = None
    timestamp: datetime = datetime.now()


class ResearchEvidence(BaseModel):
    """Represents evidence gathered during research."""
    claim: str
    supporting_results: List[SearchResult]
    confidence_level: float  # 0.0 to 1.0
    reasoning: str


class ResearchSection(BaseModel):
    """Represents a section of the research report."""
    title: str
    content: str
    evidence: List[ResearchEvidence]
    subsections: List['ResearchSection'] = []


class ResearchDocument(BaseModel):
    """Final research document structure."""
    title: str
    executive_summary: str
    sections: List[ResearchSection]
    references: List[SearchResult]
    methodology: str
    confidence_assessment: str
    content: Optional[str] = None  # Full markdown content
    generated_at: datetime = datetime.now()


class AgentState(TypedDict):
    """State schema for the ReAct Research Agent."""
    messages: Annotated[List[BaseMessage], add_messages]
    
    original_query: str
    research_plan: List[str]  
    current_step: int
    search_results: List[SearchResult]
    evidence_collected: List[ResearchEvidence]
    
    document_outline: List[str]
    final_document: Optional[ResearchDocument]
    
    current_reasoning: str
    next_action: str
    iteration_count: int
    max_iterations: int
    
    last_tool_result: Optional[str]
    error_count: int
    max_errors: int
    
    status: str 
    completion_reason: str


class AgentConfig(BaseModel):
    max_iterations: int = 15
    max_errors: int = 3
    min_search_results: int = 10
    confidence_threshold: float = 0.7
    enable_tavily: bool = True
    enable_perplexity: bool = True
    research_depth: str = "comprehensive" 
    output_format: str = "markdown" 
