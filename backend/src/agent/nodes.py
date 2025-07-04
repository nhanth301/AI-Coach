from typing import Literal
import requests
from bs4 import BeautifulSoup

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.document_loaders import PyPDFLoader

from ..schemas import GraphState
from ..config import llm
from ..prompts import (
    REWRITE_PROMPT,
    ROUTER_PROMPT_TEMPLATE,
    WEB_SUMMARY_PROMPT_TEMPLATE,
    ARXIV_SUMMARY_PROMPT_TEMPLATE,
)
from ..tools.web_search_tool import Web_Searcher_Tool
from ..tools.arxiv_search_tool import Arxiv_Search_Tool

web_search_tool = Web_Searcher_Tool()
arxiv_search_tool = Arxiv_Search_Tool()

def rewrite_query_node(state: GraphState) -> dict:
    """Rewrites the initial user query for search efficiency."""
    result = llm.invoke([REWRITE_PROMPT, HumanMessage(state['user_query'])])
    return {'rewritten_query': result.content}

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
    return {"processed_web_results": summaries}

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
            docs = loader.load()[:7]
            context = " ".join([doc.page_content for doc in docs])
            prompt = ARXIV_SUMMARY_PROMPT_TEMPLATE.invoke({'context': context, 'query': user_query})
            summary = llm.invoke(prompt).content
            summaries.append(summary)
        except Exception as e:
            print(f"[WARN] Failed to process arXiv PDF {pdf_url}: {e}")
    return {"processed_arxiv_results": summaries}

def conditional_router(state: GraphState) -> Literal["web_search_branch", "arxiv_search_branch"]:
    """Determines the execution path based on the routing decision."""
    return "arxiv_search_branch" if state['routing_decision']['route'] == 'arxiv_search' else "web_search_branch"