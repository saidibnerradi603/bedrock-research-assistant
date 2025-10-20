import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from agent.graph import ResearchAgent
from schemas.state import AgentConfig, AgentState, ResearchDocument


class ResearchRunner:
    
    def __init__(self, output_dir: str = "results/exports"):
        self.output_dir = None
        if output_dir:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def run_research(self, query: str, config: Optional[AgentConfig] = None) -> dict:
        print(f"🔍 Starting research on: {query}")
        print("="*50)
        
        agent = ResearchAgent(config)
        
        start_time = datetime.now()
        final_state = agent.research(query)
        end_time = datetime.now()
        
        summary = agent.get_research_summary(final_state)
        summary["duration"] = str(end_time - start_time)
        summary["timestamp"] = end_time.isoformat()
        
        document_content = None
        if final_state["final_document"]:
            document_content = self._generate_markdown_document(final_state["final_document"], final_state)
        
        document_path = None
        if self.output_dir:
            document_path = self._save_results(query, final_state, summary, document_content)
        
        self._print_summary(summary)
        
        return {
            "summary": summary,
            "state": final_state,
            "document_path": document_path,
            "document_content": document_content
        }
    
    def _save_results(self, query: str, state: AgentState, summary: dict, doc_content: str = None):
        """Save research results to markdown file only and return the path."""
        if not self.output_dir:
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()[:50]
        base_name = f"{safe_query}_{timestamp}"
        
        if state["final_document"]:
            if not doc_content:
                doc_content = self._generate_markdown_document(state["final_document"], state)
                
            doc_path = self.output_dir / f"{base_name}.md"
            doc_path.write_text(doc_content, encoding='utf-8')
            print(f"📄 Research report saved: {doc_path}")
            return str(doc_path)
        else:
            print("⚠️  No document was generated")
            return None
    
    def _generate_markdown_document(self, doc: ResearchDocument, state: AgentState) -> str:
        if hasattr(doc, 'content') and doc.content:
            return doc.content
        
        content = []
        
        
        content.append(f"# {state['original_query']}")
        content.append("")
        
        if doc.executive_summary and len(doc.executive_summary.strip()) > 20:
            content.append("## Executive Summary")
            content.append(doc.executive_summary.strip())
            content.append("")
        
        if state["evidence_collected"]:
            content.append("## Key Findings")
            content.append("")
            
            for i, evidence in enumerate(state["evidence_collected"], 1):
                claim = evidence.claim.strip()
                
                # Skip if it looks like a search query or meta-instruction
                if any(skip in claim.lower() for skip in [
                    'search for', 'look up', 'investigate', 'plan next', 
                    'formulate', 'thought:', 'action:', 'analyze current evidence'
                ]):
                    continue
                    
                content.append(f"### {claim}")
                content.append("")
                
               
                if evidence.supporting_results:
                    for source in evidence.supporting_results[:2]:  # Limit to 2 sources per finding
                        if source.content and len(source.content.strip()) > 50:
                            source_content = source.content[:400].strip()
                            source_content = re.sub(r'(THOUGHT|ACTION|OBSERVATION):', '', source_content)
                            if source_content:
                                content.append(source_content)
                                content.append("")
                            break
                
                if evidence.supporting_results:
                    citations = []
                    for source in evidence.supporting_results[:3]:
                        if source.title and source.url:
                            citations.append(f"[{source.title}]({source.url})")
                    if citations:
                        content.append(f"*Sources: {', '.join(citations)}*")
                        content.append("")
        
        elif state["search_results"]:
            content.append("## Research Findings")
            content.append("")
            
            for result in state["search_results"][:5]:  # Top 5 results
                if result.content and len(result.content.strip()) > 100:
                    content.append(f"### {result.title}")
                    content.append("")
                    
                    clean_content = result.content[:500].strip()
                    clean_content = re.sub(r'\s+', ' ', clean_content)
                    content.append(clean_content)
                    content.append("")
                    
                    if result.url:
                        content.append(f"*Source: [{result.title}]({result.url})*")
                        content.append("")
        
        unique_sources = {source.url: source for source in state["search_results"] if source.url}.values()
        if unique_sources:
            content.append("## References")
            content.append("")
            for i, source in enumerate(sorted(unique_sources, key=lambda x: x.title or 'Untitled'), 1):
                title = source.title or 'Untitled'
                content.append(f"{i}. [{title}]({source.url})")
            content.append("")
        
        return "\n".join(content)
        
        return "\n".join(content)
    
    def _prepare_state_for_json(self, state: AgentState) -> dict:
        """Prepare state for JSON serialization."""
        json_state = {}
        
        for key, value in state.items():
            if key == "messages":
                json_state[key] = [
                    {
                        "type": msg.__class__.__name__,
                        "content": msg.content
                    } for msg in value
                ]
            elif key == "search_results":
                json_state[key] = [result.dict() for result in value]
            elif key == "evidence_collected":
                json_state[key] = [evidence.dict() for evidence in value]
            elif key == "final_document" and value:
                json_state[key] = value.dict()
            else:
                json_state[key] = value
                
        return json_state
    
    def _print_summary(self, summary: dict):
        """Print research summary to console."""
        print("\n✅ Research Completed!")
        print("="*30)
        print(f"Status: {summary['status']}")
        print(f"Duration: {summary['duration']}")
        print(f"Iterations: {summary['iterations']}")
        print(f"Sources Found: {summary['sources_found']}")
        print(f"Evidence Collected: {summary['evidence_collected']}")
        print(f"Document Generated: {'Yes' if summary['has_document'] else 'No'}")
        if summary['errors'] > 0:
            print(f"⚠️  Errors: {summary['errors']}")
        print(f"Completion Reason: {summary['completion_reason']}")
        print("="*30)
    
    def _get_document_path(self, query: str) -> str:
        """Get the expected document path for a query."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()[:50]
        return str(self.output_dir / f"{safe_query}_{timestamp}.md")
