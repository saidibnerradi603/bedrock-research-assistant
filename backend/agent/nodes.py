import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from schemas.state import AgentState, SearchResult, ResearchEvidence, ResearchDocument, ResearchSection
from utils.system_prompt import (
    REACT_SYSTEM_PROMPT, PLANNING_PROMPT, SEARCH_ANALYSIS_PROMPT, 
    DOCUMENT_GENERATION_PROMPT, ERROR_RECOVERY_PROMPT, COMPLETION_VALIDATION_PROMPT
)
from tools.search import tavily_search, perplexity_search
import re
from langchain_aws import ChatBedrockConverse
from config import get_settings
import boto3
import os
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

llm = ChatBedrockConverse(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",  
    client=bedrock_client
)




def planning_node(state: AgentState) -> AgentState:

    
    
    planning_message = PLANNING_PROMPT.format(query=state["original_query"])
    
    messages = [
        SystemMessage(content=REACT_SYSTEM_PROMPT),
        HumanMessage(content=planning_message)
    ]
    
    try:
        response = llm.invoke(messages)
        
        research_plan = _extract_research_plan(response.content)
        
        updated_state = state.copy()
        updated_state["messages"] = state["messages"] + [HumanMessage(content=planning_message), response]
        updated_state["research_plan"] = research_plan
        updated_state["current_reasoning"] = response.content
        updated_state["status"] = "researching"
        updated_state["current_step"] = 0
        
        return updated_state
        
    except Exception as e:
        return _handle_error(state, f"Planning error: {str(e)}", "planning_node")


def reasoning_node(state: AgentState) -> AgentState:

    
    if state["status"] == "researching":
        analysis_prompt = SEARCH_ANALYSIS_PROMPT.format(
            query=state["original_query"],
            current_step=state["current_step"],
            num_results=len(state["search_results"]),
            num_evidence=len(state["evidence_collected"])
        )
    elif state["status"] == "analyzing":
        analysis_prompt = COMPLETION_VALIDATION_PROMPT.format(
            num_sources=len(state["search_results"]),
            evidence_quality=_assess_evidence_quality(state["evidence_collected"]),
            coverage=_assess_coverage(state["research_plan"], state["evidence_collected"]),
            iterations=state["iteration_count"]
        )
    else:
        analysis_prompt = "Analyze the current research state and determine next action."
    
    messages = state["messages"] + [HumanMessage(content=analysis_prompt)]
    
    try:
        response = llm.invoke(messages)
        
        next_action = _extract_next_action(response.content)
        
        updated_state = state.copy()
        updated_state["messages"] = state["messages"] + [HumanMessage(content=analysis_prompt), response]
        updated_state["current_reasoning"] = response.content
        updated_state["next_action"] = next_action
        updated_state["iteration_count"] += 1
        
        return updated_state
        
    except Exception as e:
        return _handle_error(state, f"Reasoning error: {str(e)}", "reasoning_node")


def search_node(state: AgentState) -> AgentState:
 
    search_query = _extract_search_query(state["current_reasoning"], state["next_action"])
    
    if not search_query:
        search_query = state["research_plan"][min(state["current_step"], len(state["research_plan"]) - 1)]
    
    search_results = []
    
    try:
        if "tavily" in state["next_action"].lower() or "both" in state["next_action"].lower():
            tavily_result = tavily_search.invoke({"query": search_query})
            search_results.extend(_parse_search_results(tavily_result, "tavily"))
        
        if "perplexity" in state["next_action"].lower() or "both" in state["next_action"].lower():
            perplexity_result = perplexity_search.invoke({"query": search_query})
            search_results.extend(_parse_search_results(perplexity_result, "perplexity"))
        
        if not search_results:
            tavily_result = tavily_search.invoke({"query": search_query})
            perplexity_result = perplexity_search.invoke({"query": search_query})
            search_results.extend(_parse_search_results(tavily_result, "tavily"))
            search_results.extend(_parse_search_results(perplexity_result, "perplexity"))
        
        updated_state = state.copy()
        updated_state["search_results"].extend(search_results)
        updated_state["last_tool_result"] = f"Found {len(search_results)} new results for: {search_query}"
        updated_state["current_step"] += 1
        
        # Add tool message to conversation
        tool_message = ToolMessage(
            content=f"Search completed. Found {len(search_results)} results for: {search_query}",
            tool_call_id="search_" + str(state["current_step"])
        )
        updated_state["messages"] = state["messages"] + [tool_message]
        
        return updated_state
        
    except Exception as e:
        return _handle_error(state, f"Search error: {str(e)}", "search_node")


def analysis_node(state: AgentState) -> AgentState:
    """
    Analysis node: Processes search results and extracts evidence.
    """
    
    # Prepare analysis context
    recent_results = state["search_results"][-10:]  # Last 10 results
    results_summary = "\n".join([
        f"Source: {result.title}\nContent: {result.content[:300]}...\nURL: {result.url}\n" 
        for result in recent_results if result.content
    ])
    
    analysis_prompt = f"""
Analyze the search results for: "{state["original_query"]}"

Extract key findings, insights, and factual information from these sources:

{results_summary}

Provide specific, factual findings including:
- Important developments or breakthroughs
- Key statistics, data points, or metrics
- Expert opinions or research conclusions
- Trends or patterns identified
- Concrete examples or case studies

Focus on substantive content that would be valuable in a research report. Avoid meta-analysis about the search process.

Present each finding as a clear, standalone statement that could be included in a professional report.
    """
    
    messages = [
        SystemMessage(content="You are a research analyst extracting key insights from source materials. Focus on factual information, specific findings, and actionable insights. Avoid discussing research methodology."),
        HumanMessage(content=analysis_prompt)
    ]
    
    try:
        response = llm.invoke(messages)
        
        
        new_evidence = _extract_evidence(response.content, recent_results)
        
        
        updated_state = state.copy()
        updated_state["messages"] = state["messages"] + [HumanMessage(content=analysis_prompt), response]
        updated_state["evidence_collected"].extend(new_evidence)
        updated_state["current_reasoning"] = response.content
        
        
        if _should_generate_document(updated_state):
            updated_state["status"] = "generating"
        
        return updated_state
        
    except Exception as e:
        return _handle_error(state, f"Analysis error: {str(e)}", "analysis_node")


def document_generation_node(state: AgentState) -> AgentState:
    """
    Document generation node: Creates the final research document.
    """
    
    evidence_summary = "\n".join([
        f"• {evidence.claim} (Confidence: {evidence.confidence_level:.0%})" 
        for evidence in state["evidence_collected"]
    ])
    
    sources_summary = "\n".join([
        f"- {result.title}: {result.content[:200]}..." 
        for result in state["search_results"][:10]
    ])
    
    doc_prompt = DOCUMENT_GENERATION_PROMPT.format(
        query=state["original_query"],
        num_sources=len(state["search_results"]),
        num_evidence=len(state["evidence_collected"]),
        quality_assessment=_assess_evidence_quality(state["evidence_collected"])
    )
    
    # Add detailed research context
    context_prompt = f"""
{doc_prompt}

## Research Evidence:
{evidence_summary}

## Source Content Summary:
{sources_summary}

## Instructions:
Synthesize this information into a comprehensive, professional research report. Focus on:
- Key findings and insights
- Trends and developments
- Specific data and examples
- Multiple perspectives where relevant
- Clear, actionable conclusions

Do NOT include:
- Research methodology or process details
- Meta-commentary about the research
- Internal reasoning or thought processes
- Information about search tools or techniques

Generate a polished, professional markdown report that delivers real value to the reader."""
    
    messages = [
        SystemMessage(content="You are an expert research analyst. Create comprehensive, professional reports that synthesize information clearly and provide actionable insights. Focus on the substance of the research, not the process."),
        HumanMessage(content=context_prompt)
    ]
    
    try:
        response = llm.invoke(messages)
        document_content = response.content
        
       
        document_content = _clean_document_content(document_content)
        
        
        exec_summary = _extract_executive_summary(document_content)
        
      
        final_document = ResearchDocument(
            title=f"Research Report: {state['original_query']}",
            executive_summary=exec_summary,
            sections=[],
            references=state["search_results"],
            methodology="Comprehensive web research and analysis",
            confidence_assessment=_assess_evidence_quality(state["evidence_collected"])
        )
        
       
        final_document.content = document_content
        
        # Update state
        updated_state = state.copy()
        updated_state["messages"] = state["messages"] + [HumanMessage(content=context_prompt), response]
        updated_state["final_document"] = final_document
        updated_state["status"] = "completed"
        updated_state["completion_reason"] = "Professional research report generated"
        
        return updated_state
        
    except Exception as e:
        return _handle_error(state, f"Document generation error: {str(e)}", "document_generation_node")


def _clean_document_content(content: str) -> str:
    """Clean up document content to remove unwanted elements."""
    patterns_to_remove = [
        r'\*\*THOUGHT\*\*:.*?(?=\*\*|$)',
        r'\*\*ACTION\*\*:.*?(?=\*\*|$)',
        r'\*\*OBSERVATION\*\*:.*?(?=\*\*|$)',
        r'THOUGHT:.*?\n',
        r'ACTION:.*?\n',
        r'OBSERVATION:.*?\n',
        r'## Research Process.*?(?=##|$)',
        r'## Methodology.*?(?=##|$)',
        r'## Research Plan.*?(?=##|$)'
    ]
    
    cleaned_content = content
    for pattern in patterns_to_remove:
        cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean up excessive whitespace
    cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content)
    cleaned_content = re.sub(r'^\s+', '', cleaned_content, flags=re.MULTILINE)
    
    return cleaned_content.strip()


def _extract_executive_summary(content: str) -> str:
   
    # Look for executive summary section
    summary_patterns = [
        r'## Executive Summary\s*\n([^#]+?)(?=##|$)',
        r'# Executive Summary\s*\n([^#]+?)(?=##|$)',
        r'\*\*Executive Summary\*\*:?\s*\n([^*]+?)(?=\*\*|$)'
    ]
    
    for pattern in summary_patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            summary = match.group(1).strip()
            summary = re.sub(r'\s+', ' ', summary)
            return summary[:500] + "..." if len(summary) > 500 else summary
    
    paragraphs = content.split('\n\n')
    for para in paragraphs:
        if len(para.strip()) > 50 and not para.strip().startswith('#'):
            summary = para.strip()
            summary = re.sub(r'\s+', ' ', summary)
            return summary[:300] + "..." if len(summary) > 300 else summary
    
    return "Comprehensive analysis of the research topic with key findings and insights."




def _extract_research_plan(response_content: str) -> List[str]:
    """Extract research plan from LLM response."""
    lines = response_content.split('\n')
    plan_items = []
    
    for line in lines:
        line = line.strip()
        if (line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•')) or
            'search' in line.lower() or 'investigate' in line.lower()):
            plan_items.append(line.lstrip('123456789.- •'))
    
    return plan_items[:10]  # Limit to 10 items


def _extract_next_action(response_content: str) -> str:
    """Extract next action from reasoning response."""
    action_indicators = ['action:', 'next:', 'should:', 'will:', 'search for']
    
    for line in response_content.lower().split('\n'):
        for indicator in action_indicators:
            if indicator in line:
                return line.strip()
    
    return "continue research"


def _extract_search_query(reasoning: str, next_action: str) -> str:
    """Extract search query from reasoning and action."""
    text = f"{reasoning} {next_action}".lower()
    
    # Look for quoted queries
    quotes = re.findall(r'["\']([^"\'\']+)["\']', text)
    if quotes:
        return quotes[0]
    
    # Look for search indicators
    search_patterns = [
        r'search for (.+?)(?:\.|$|\n)',
        r'look up (.+?)(?:\.|$|\n)',
        r'investigate (.+?)(?:\.|$|\n)'
    ]
    
    for pattern in search_patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0].strip()
    
    return ""


def _parse_search_results(search_result: str, source: str) -> List[SearchResult]:
    """Parse search results from tool output."""
    results = []
    
    # Split by numbered items or bullet points
    items = re.split(r'\n(?:\d+\.|-)\s*\*\*', search_result)
    
    for item in items[1:]:  # Skip first item
        lines = item.strip().split('\n')
        if len(lines) >= 2:
            # Extract title (first line)
            title_line = lines[0].strip()
            title = title_line.split('**')[0].strip() if '**' in title_line else title_line
            
            # Extract URL
            url = ""
            content_lines = []
            
            for line in lines[1:]:
                line = line.strip()
                if line.lower().startswith('url:') or line.lower().startswith('source:'):
                    url = line.split(':', 1)[1].strip()
                elif line.lower().startswith('summary:') or line.lower().startswith('content:'):
                    content_lines.append(line.split(':', 1)[1].strip())
                elif line and not line.lower().startswith(('url:', 'source:', 'retrieved:')):
                    content_lines.append(line)
            
            content = ' '.join(content_lines).strip()
            
            # Clean up content
            if content:
                # Remove excessive whitespace and clean up
                content = re.sub(r'\s+', ' ', content)
                content = content[:500]  # Limit content length
                
                if title and len(content) > 20:  # Ensure meaningful content
                    results.append(SearchResult(
                        title=title,
                        url=url,
                        content=content,
                        source=source
                    ))
    
    return results


def _extract_evidence(analysis_content: str, sources: List[SearchResult]) -> List[ResearchEvidence]:
    """Extract evidence from analysis response."""
    evidence_list = []
    
    lines = analysis_content.split('\n')
    
    findings = []
    current_finding = ""
    
    for line in lines:
        line = line.strip()
        if any(skip_word in line.lower() for skip_word in ['thought:', 'action:', 'next:', 'should:', 'plan', 'analyze']):
            continue
            
        if line.startswith(('-', '•')) or any(indicator in line.lower() for indicator in ['breakthrough', 'development', 'advancement', 'discovery', 'research shows', 'studies indicate']):
            finding = line.lstrip('-• ').strip()
            if len(finding) > 20 and not any(meta in finding.lower() for meta in ['search for', 'look up', 'investigate']):
                findings.append(finding)
    
    for i, finding in enumerate(findings[:5]):  # Limit to 5 key findings
        if finding:
            evidence_list.append(ResearchEvidence(
                claim=finding,
                supporting_results=sources[i:i+2] if i < len(sources) else sources[:2],
                confidence_level=0.8,
                reasoning="Derived from comprehensive search analysis"
            ))
    
    return evidence_list


def _handle_error(state: AgentState, error_message: str, node_name: str) -> AgentState:
    """Handle errors and update state accordingly."""
    updated_state = state.copy()
    updated_state["error_count"] += 1
    updated_state["last_tool_result"] = error_message
    
    if updated_state["error_count"] >= updated_state["max_errors"]:
        updated_state["status"] = "error"
        updated_state["completion_reason"] = f"Max errors reached in {node_name}: {error_message}"
    
    return updated_state


def _assess_evidence_quality(evidence: List[ResearchEvidence]) -> str:
    """Assess the quality of collected evidence."""
    if not evidence:
        return "No evidence collected"
    
    avg_confidence = sum(e.confidence_level for e in evidence) / len(evidence)
    
    if avg_confidence >= 0.8:
        return "High quality"
    elif avg_confidence >= 0.6:
        return "Medium quality"
    else:
        return "Low quality"


def _assess_coverage(plan: List[str], evidence: List[ResearchEvidence]) -> str:
    """Assess research coverage completeness."""
    if len(evidence) >= len(plan):
        return "Comprehensive"
    elif len(evidence) >= len(plan) * 0.7:
        return "Good"
    else:
        return "Limited"


def _should_generate_document(state: AgentState) -> bool:
    """Determine if ready for document generation."""
    return (
        len(state["search_results"]) >= 10 or
        len(state["evidence_collected"]) >= 5 or
        state["iteration_count"] >= state["max_iterations"]
    )


def _create_research_document(query: str, content: str, evidence: List[ResearchEvidence], sources: List[SearchResult]) -> ResearchDocument:
    """Create the final research document."""
    exec_summary = "Research findings and analysis based on comprehensive investigation."
    if "executive summary" in content.lower():
        summary_match = re.search(r'executive summary[:\n]([^#]+)', content, re.IGNORECASE)
        if summary_match:
            exec_summary = summary_match.group(1).strip()[:300]
    
    return ResearchDocument(
        title=query,
        executive_summary=exec_summary,
        sections=[],
        references=sources,
        methodology="Web research using multiple sources",
        confidence_assessment=_assess_evidence_quality(evidence)
    )
