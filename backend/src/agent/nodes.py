from typing import Literal
import requests
from bs4 import BeautifulSoup

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.document_loaders import PyPDFLoader

import uuid
from langchain_core.documents import Document
from ..vectordb.store import get_qdrant_store

from ..schemas import GraphState
from ..config import llm
from ..prompts import (
    REWRITE_PROMPT,
    ROUTER_PROMPT_TEMPLATE,
    WEB_SUMMARY_PROMPT_TEMPLATE,
    ARXIV_SUMMARY_PROMPT_TEMPLATE,
    DOCUMENT_GRADER_PROMPT_TEMPLATE
)
from ..tools.web_search_tool import Web_Searcher_Tool
from ..tools.arxiv_search_tool import Arxiv_Search_Tool

web_search_tool = Web_Searcher_Tool()
arxiv_search_tool = Arxiv_Search_Tool()

def rewrite_query_node(state: GraphState) -> dict:
    """Rewrites the initial user query for search efficiency."""
    result = llm.invoke([REWRITE_PROMPT, HumanMessage(state['user_query'])])
    return {'rewritten_query': result.content}

def retrieve_from_db_node(state: GraphState) -> dict:
    """
    Use rewritten_query to search for related documents in Qdrant.
    """
    query = state["rewritten_query"]
    qdrant_store = get_qdrant_store()
    
    found_docs = qdrant_store.similarity_search(query=query, k=3)
    return {"retrieved_documents": found_docs}

def grade_retrieved_documents_node(state: GraphState) -> dict:
    """
    Uses an LLM to grade the relevance of retrieved documents.
    """

    query = state["rewritten_query"]
    retrieved_docs = state.get("retrieved_documents", [])

    if not retrieved_docs:
        return {"relevant_doc_ids": None}

    formatted_docs = ""
    for i, doc in enumerate(retrieved_docs):
        formatted_docs += f"\n\n--- Document {i} ---\n{doc.page_content}"

    parser = JsonOutputParser()
    chain = DOCUMENT_GRADER_PROMPT_TEMPLATE | llm | parser
    
    try:
        response = chain.invoke({
        "query": query,
        "documents": formatted_docs
    })
        relevant_indices = response.get("relevant_indices", [])
    except Exception as e:
        relevant_indices = []

    if not relevant_indices:
        return {"relevant_doc_ids": None}

    top_indices = relevant_indices[:3]
    final_ids = []
    for i in top_indices:
        if i < len(retrieved_docs):
            doc_id = retrieved_docs[i].metadata.get("_id")
            final_ids.append(doc_id)

    print(f"LLM Grader selected {len(final_ids)} relevant document(s).")
    return {"relevant_doc_ids": final_ids if final_ids else None}


def should_continue_to_external_search(state: GraphState) -> Literal["continue_search", "end_with_ids"]:
    """
    Checks if the grader found any relevant document IDs.
    """
    if state.get("relevant_doc_ids"):
        print("Relevant documents found and graded. Ending process.")
        return "end_with_ids"
    else:
        print("No relevant documents found after grading. Continuing to external search.")
        return "continue_search"
    
def final_results_node(state: GraphState) -> dict:
    relevant_doc_ids = state['relevant_doc_ids']
    results = []
    for doc in state['retrieved_documents']:
        if doc.metadata.get('_id') in relevant_doc_ids:
            results.append(doc.page_content)
    return {'final_results': results}


def router_node(state: GraphState) -> dict:
    """Determines the appropriate tool (web or arXiv) for the query."""
    prompt = ROUTER_PROMPT_TEMPLATE.invoke({"query": state['rewritten_query']})
    result = llm.invoke(prompt).content
    parsed_result = JsonOutputParser().invoke(result)
    return {'routing_decision': parsed_result}

def web_search_node(state: GraphState) -> dict:
    """Performs a web search."""
    search_results = web_search_tool.invoke(state['rewritten_query'])
    return {'web_search_results': search_results}

def process_web_results_node(state: GraphState) -> dict:
    """Scrapes and summarizes content from web search results."""
    summaries = []
    user_query = state['rewritten_query']
    for result in state['web_search_results']:
        url = result['url']
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            text = "\n".join([p.get_text() for p in soup.find_all('p')])
            prompt = WEB_SUMMARY_PROMPT_TEMPLATE.invoke({"query": user_query, "context": text})
            summary = llm.invoke(prompt).content
            summaries.append(summary)
        except Exception as e:
            print(f"[WARN] Skipping URL {url} due to error: {e}")
    return {"processed_results": summaries}

def arxiv_search_node(state: GraphState) -> dict:
    """Performs a search on arXiv."""
    payload = {'query': state['rewritten_query'], 'search_type': state['routing_decision']['arxiv_field']}
    search_results = arxiv_search_tool.invoke(payload)
    return {'arxiv_search_results': search_results}

def process_arxiv_results_node(state: GraphState) -> dict:
    """Downloads, extracts text, and summarizes arXiv papers."""
    summaries = []
    user_query = state['rewritten_query']
    for result in state['arxiv_search_results']:
        pdf_url = result['link'].replace('abs', 'pdf')
        try:
            loader = PyPDFLoader(pdf_url)
            docs = loader.load()[:5]
            context = " ".join([doc.page_content for doc in docs])
            prompt = ARXIV_SUMMARY_PROMPT_TEMPLATE.invoke({'context': context, 'query': user_query})
            summary = llm.invoke(prompt).content
            summaries.append(summary)
        except Exception as e:
            print(f"[WARN] Failed to process arXiv PDF {pdf_url}: {e}")
    return {"processed_results": summaries}

def add_to_db_node(state: GraphState) -> dict:
    qdrant_store = get_qdrant_store()

    route = state['routing_decision']['route']
    original_results = state['web_search_results'] if route == 'web_search' else state['arxiv_search_results']
    processed_summaries = state['processed_results']
    documents_to_add = []
    ids_to_add = []

    if not original_results or not processed_summaries:
        status = "Nothing to add to DB."
        print(f"[INFO] {status}")
        return {"db_add_status": status}


    for i, summary in enumerate(processed_summaries):
        original_item = original_results[i]
        
        metadata = {
            "title": original_item.get("title", "N/A"),
            "source": original_item.get("link") or original_item.get("url"),
        }
        if route == 'arxiv_search':
            metadata["authors"] = original_item.get("authors", "N/A")

        doc = Document(page_content=summary, metadata=metadata)
        documents_to_add.append(doc)

        source_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, metadata["source"]))
        ids_to_add.append(source_id)

    try:
        qdrant_store.add_documents(documents=documents_to_add, ids=ids_to_add)
        status = f"Successfully added {len(documents_to_add)} documents to VectorDB."
        print(f"[INFO] {status}")
    except Exception as e:
        status = f"Error adding to VectorDB: {e}"
        print(f"[ERROR] {status}")
        
    return {"db_add_status": status}

def conditional_router(state: GraphState) -> Literal["web_search_branch", "arxiv_search_branch"]:
    """Determines the execution path based on the routing decision."""
    return "arxiv_search_branch" if state['routing_decision']['route'] == 'arxiv_search' else "web_search_branch"

