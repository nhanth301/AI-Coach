from typing import TypedDict, List
from langchain_core.documents import Document
from pydantic import BaseModel, Field

class GraphState(TypedDict):
    """
    The complete state definition is passed between nodes in the graph.
    """
    user_query: str
    rewritten_query: str
    routing_decision: dict
    web_search_results: dict
    arxiv_search_results: dict
    processed_results: List[str]
    db_add_status: str | None
    retrieved_documents: List[Document]
    relevant_doc_ids: List[str] | None
    final_results: List[str]

class GraphInput(TypedDict):
    """
    Defines the input structure for the graph.
    """
    user_query: str


class GraphOutput(TypedDict):
    """
    Defines the output structure for the graph.
    """
    user_query: str
    rewritten_query: str
    final_results: List[str]


class TranslationFeedbackRequest(BaseModel):
    """The data sent from the frontend to the feedback API."""
    original_passage: str = Field(..., description="The full original Vietnamese passage for context.")
    current_sentence: str = Field(..., description="The specific Vietnamese sentence the user is currently translating.")
    user_translation: str = Field(..., description="The user's English translation of the current sentence.")

class CategorizedFeedback(BaseModel):
    grammar: str = Field(..., description="Feedback on grammar and sentence structure.")
    vocabulary: str = Field(..., description="Feedback on word choice and vocabulary.")
    nuance: str = Field(..., description="Feedback on tone, style, and nuance.")

class Feedback(BaseModel):
    """The structured feedback object returned by the LLM."""
    score: int = Field(..., ge=0, le=100)
    categorized_feedback: CategorizedFeedback
    suggestions: List[str] = Field(..., description="A list of improved or alternative English translations.")

class TranslationFeedbackResponse(BaseModel):
    """The final response sent back to the frontend."""
    feedback_data: Feedback