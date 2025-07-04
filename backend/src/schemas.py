from typing import TypedDict, List

class GraphState(TypedDict):
    """
    The complete state definition is passed between nodes in the graph.
    """
    user_query: str
    rewritten_query: str
    routing_decision: dict
    web_search_results: dict
    arxiv_search_results: dict
    processed_web_results: List[str]
    processed_arxiv_results: List[str]

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
    routing_decision: dict
    processed_web_results: List[str]
    processed_arxiv_results: List[str]