from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate

REWRITE_PROMPT = SystemMessage(
    """
    You are an expert query optimizer. Rewrite the user's query to be concise and keyword-focused for a search engine, preserving the original intent. Remove all conversational fillers. Return only the optimized query.
    """
)

ROUTER_PROMPT_TEMPLATE = PromptTemplate.from_template(
    """
    You are an intelligent routing agent. Classify the user's query for either 'web_search' (general topics) or 'arxiv_search' (scientific/academic research). For 'arxiv_search', specify the field: 'title', 'author', 'abstract', or 'all'.
    Query: {query}
    Respond in JSON format: {{"route": "web_search" or "arxiv_search", "arxiv_field": "all" | "title" | "author" | "abstract" | null}}
    """
)

WEB_SUMMARY_PROMPT_TEMPLATE = PromptTemplate.from_template(
    """
    You are an information writer. Your task is to compose a clear, self-contained paragraph in Vietnamese that answers the user's query using only the provided context. This paragraph will be used for a sentence-by-sentence translation exercise.
    Guidelines:
    1. Directly answer the user's query using information found in the context.
    2. Structure the answer into a paragraph containing at least 4 complete sentences.
    3. Crucially, DO NOT refer to the source context. Avoid phrases like "The article says," or "According to the website,".
    4. Write in clear, standard Vietnamese and do not add any external information.
    5. Keep the paragraph under 110 words.
    Query: {query}
    Context: {context}
    Vietnamese paragraph (must answer the query and contain at least 4 sentences):
    """
)

ARXIV_SUMMARY_PROMPT_TEMPLATE = PromptTemplate.from_template(
    """
    You are a research assistant. Your task is to write an informative paragraph in Vietnamese that summarizes the provided academic text, focusing specifically on how it relates to the user's query. This paragraph will be used for a sentence-by-sentence translation exercise.
    Guidelines:
    1. Analyze the User's Query to understand their specific area of interest.
    2. Focus the summary on information in the Context that directly addresses the Query.
    3. Structure the summary into a paragraph containing at least 4 complete sentences.
    4. Crucially, DO NOT use meta-phrases like "This paper introduces".
    5. Keep the paragraph under 110 words.
    User Query: {query}
    Context: {context}
    Vietnamese paragraph (focused on the query, at least 4 sentences):
    """
)