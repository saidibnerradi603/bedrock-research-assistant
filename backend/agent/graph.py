from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from schemas.state import AgentState, AgentConfig
from agent.nodes import (
    planning_node, reasoning_node, search_node, 
    analysis_node, document_generation_node
)
from utils.system_prompt import REACT_SYSTEM_PROMPT


class ResearchAgent:
    
    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        
        workflow = StateGraph(AgentState)
        
        workflow.add_node("planning", planning_node)
        workflow.add_node("reasoning", reasoning_node)
        workflow.add_node("search", search_node)
        workflow.add_node("analysis", analysis_node)
        workflow.add_node("document_generation", document_generation_node)
        
        workflow.add_edge(START, "planning")
        workflow.add_edge("planning", "reasoning")
        
        workflow.add_conditional_edges(
            "reasoning",
            self._route_from_reasoning,
            {
                "search": "search",
                "analysis": "analysis",
                "generate": "document_generation",
                "end": END
            }
        )
        
        workflow.add_edge("search", "analysis")
        workflow.add_edge("analysis", "reasoning")
        
        workflow.add_edge("document_generation", END)
        
        return workflow.compile()
    
    def _route_from_reasoning(self, state: AgentState) -> Literal["search", "analysis", "generate", "end"]:
        
        if state["status"] == "error" or state["error_count"] >= state["max_errors"]:
            return "end"
        
        if state["status"] == "completed":
            return "end"
        
        if state["iteration_count"] >= state["max_iterations"]:
            return "generate"
        
        if state["status"] == "generating":
            return "generate"
        
        next_action = state.get("next_action", "").lower()
        
        if any(keyword in next_action for keyword in ["search", "look up", "investigate", "find"]):
            return "search"
        
        if any(keyword in next_action for keyword in ["analyze", "examine", "review", "synthesize"]):
            return "analysis"
        
        if any(keyword in next_action for keyword in ["generate", "write", "create", "document", "report"]):
            return "generate"
        
        if len(state["search_results"]) < self.config.min_search_results:
            return "search"
        
        if len(state["evidence_collected"]) < 3:
            return "analysis"
        
        return "generate"
    
    def research(self, query: str) -> AgentState:
        
        initial_state: AgentState = {
            "messages": [
                SystemMessage(content=REACT_SYSTEM_PROMPT),
                HumanMessage(content=f"Research Query: {query}")
            ],
            "original_query": query,
            "research_plan": [],
            "current_step": 0,
            "search_results": [],
            "evidence_collected": [],
            "document_outline": [],
            "final_document": None,
            "current_reasoning": "",
            "next_action": "",
            "iteration_count": 0,
            "max_iterations": self.config.max_iterations,
            "last_tool_result": None,
            "error_count": 0,
            "max_errors": self.config.max_errors,
            "status": "planning",
            "completion_reason": ""
        }
        
        try:
            final_state = self.graph.invoke(initial_state)
            return final_state
        except Exception as e:
            error_state = initial_state.copy()
            error_state["status"] = "error"
            error_state["completion_reason"] = f"Unexpected error: {str(e)}"
            error_state["error_count"] = error_state["max_errors"]
            return error_state
    
    def get_research_summary(self, state: AgentState) -> dict:
        return {
            "query": state["original_query"],
            "status": state["status"],
            "completion_reason": state["completion_reason"],
            "iterations": state["iteration_count"],
            "sources_found": len(state["search_results"]),
            "evidence_collected": len(state["evidence_collected"]),
            "has_document": state["final_document"] is not None,
            "errors": state["error_count"]
        }
