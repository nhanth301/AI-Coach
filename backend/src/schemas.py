from typing import TypedDict, List
from langchain_core.documents import Document

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