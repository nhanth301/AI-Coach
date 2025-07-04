from langgraph.graph import StateGraph, START, END
from ..schemas import GraphState, GraphInput, GraphOutput
from .nodes import (
    rewrite_query_node,
    router_node,
    web_search_node,
    process_web_results_node,
    arxiv_search_node,
    process_arxiv_results_node,
    conditional_router,
)

def create_graph():
    """
    Create and compile LangGraph graphs.
    """
    builder = StateGraph(GraphState, input_schema=GraphInput, output_schema=GraphOutput)

    builder.add_node('rewrite_query', rewrite_query_node)
    builder.add_node('router', router_node)
    builder.add_node('web_search', web_search_node)
    builder.add_node('process_web_results', process_web_results_node)
    builder.add_node('arxiv_search', arxiv_search_node)
    builder.add_node('process_arxiv_results', process_arxiv_results_node)

    builder.add_edge(START, 'rewrite_query')
    builder.add_edge('rewrite_query', 'router')
    builder.add_conditional_edges(
        'router',
        conditional_router,
        {
            "web_search_branch": "web_search",
            "arxiv_search_branch": "arxiv_search"
        }
    )
    builder.add_edge('web_search', 'process_web_results')
    builder.add_edge('process_web_results', END)
    builder.add_edge('arxiv_search', 'process_arxiv_results')
    builder.add_edge('process_arxiv_results', END)

    graph = builder.compile()
    return graph