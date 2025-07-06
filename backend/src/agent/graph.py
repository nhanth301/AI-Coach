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
    add_to_db_node,
    retrieve_from_db_node,
    grade_retrieved_documents_node,
    should_continue_to_external_search,
    final_results_node
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
    builder.add_node("add_to_db", add_to_db_node)
    builder.add_node('retrieve_from_db', retrieve_from_db_node)
    builder.add_node('grade', grade_retrieved_documents_node)
    builder.add_node('final', final_results_node)


    builder.add_edge(START, 'rewrite_query')
    builder.add_edge('rewrite_query', 'retrieve_from_db')
    builder.add_edge('retrieve_from_db', 'grade')
    builder.add_conditional_edges(
        'grade', 
        should_continue_to_external_search,
        {
            'end_with_ids': 'final',
            'continue_search': 'router'
        }
    )
    builder.add_conditional_edges(
        'router',
        conditional_router,
        {
            "web_search_branch": "web_search",
            "arxiv_search_branch": "arxiv_search"
        }
    )
    builder.add_edge('web_search', 'process_web_results')
    builder.add_edge('process_web_results', 'add_to_db')
    builder.add_edge('arxiv_search', 'process_arxiv_results')
    builder.add_edge('process_arxiv_results', 'add_to_db')
    builder.add_edge('add_to_db', 'retrieve_from_db')
    builder.add_edge('final', END)
    graph = builder.compile()
    return graph

if __name__ == '__main__':
    graph = create_graph()
    img = graph.get_graph().draw_mermaid_png()
    filename = "my_langgraph_workflow.png"
    try:
        with open(filename, 'wb') as f:
            f.write(img)
    except:
        print('Error')