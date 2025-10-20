from pydantic import BaseModel, Field, model_validator, validator, ValidationError
from typing import List,Literal
from uuid import UUID


class ResearchPaperSummary(BaseModel):
    """Comprehensive research paper summary"""
    summary: str = Field(..., description="Extended executive summary (6-10 sentences)")
    background: str = Field(..., description="Theoretical or technical background")
    problem: str = Field(..., description="Precise research problem and motivation")
    methods: str = Field(..., description="Detailed explanation of methods and models")
    experiments: str = Field(..., description="Experimental setup, datasets, baselines, metrics")
    results: str = Field(..., description="Comprehensive description of findings")
    limitations: str = Field(..., description="Critical analysis of weaknesses")
    implications: str = Field(..., description="Contribution to the broader field")
    future_work: str = Field(..., description="Suggested future research directions")


class SummaryRequest(BaseModel):
    """Request model for paper summary"""
    paper_id: str = Field(..., description="Paper identifier")


class SummaryResponse(BaseModel):
    """Response model for paper summary"""
    paper_id: str = Field(..., description="Paper identifier")
    summary: ResearchPaperSummary = Field(..., description="Comprehensive paper summary")
    processing_time_seconds: float = Field(..., description="Processing duration")
    message: str = Field(..., description="Status message")







class MarkMapResponse(BaseModel):
    markmap: str = Field(..., description="Paper Markmap code")
    
    
    







class OptionsModel(BaseModel):
    A: str = Field(..., description="Option A text")
    B: str = Field(..., description="Option B text")
    C: str = Field(..., description="Option C text")
    D: str = Field(..., description="Option D text")


class QuestionModel(BaseModel):
    id: int = Field(..., description="Question identifier (integer)")
    question: str = Field(..., description="The question text")
    options: OptionsModel = Field(..., description="Answer choices A-D")
    correct_answer: Literal["A", "B", "C", "D"] = Field(
        ..., description="The correct option label (one of 'A','B','C','D')"
    )
    explanation: str = Field(..., description="Explanation why the correct answer is correct")

    @model_validator(mode="after")
    def correct_answer_must_be_in_options(self):  # Remove 'cls' and 'values' parameters
        """Validate that correct_answer corresponds to an existing option"""
        correct = self.correct_answer
        opts = self.options
        
        if correct and opts:
            if not getattr(opts, correct, None):
                raise ValueError(f"correct_answer '{correct}' has no corresponding option text")
        return self


class MCQSet(BaseModel):
    questions: List[QuestionModel] = Field(..., description="List of question objects")

class QuizResponse(BaseModel):
    paper_id: UUID = Field(..., description="UUID of the paper")
    questions: List[QuestionModel] = Field(..., description="List of quiz questions")  # Changed from MCQSet
    processing_time_seconds: float = Field(..., description="Processing duration")
    message: str = Field(..., description="Status message")
