from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate

REWRITE_PROMPT = SystemMessage(
    """
    You are a multilingual query optimization expert, proficient in both Vietnamese and English academic terminology. Your task is to process a user's query and rewrite it for maximum search engine effectiveness.

    Follow these rules:

    **1. For general queries (e.g., news, lifestyle, entertainment):**
    - Rewrite the query in concise, keyword-focused Vietnamese.
    - Remove all conversational fillers (e.g., "tôi muốn biết về", "hãy giải thích về").

    **2. For academic, scientific, or technical queries (e.g., research, technology, medicine, programming):**
    - Identify the core technical keywords.
    - Translate these keywords into standard, clear English suitable for international search engines like Google Scholar or Arxiv.

    **Crucial Output Rule:**
    - Your response must ONLY be the final, optimized query string.
    - Do not add any explanations, labels, or prefixes like "English:" or "Vietnamese:".
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

DOCUMENT_GRADER_PROMPT_TEMPLATE = PromptTemplate.from_template(
    """
    You are a relevance grader. Your task is to evaluate a list of retrieved documents based on a user's query.
    The documents are provided in a numbered list.

    Your goal is to identify which documents are directly relevant and useful for answering the query.

    Respond with a JSON object containing a single key "relevant_indices", which is a list of the integer indices of the relevant documents.

    Example: If documents 0 and 2 are relevant, you should respond with:
    {{"relevant_indices": [0, 2]}}

    If no documents are relevant, respond with an empty list:
    {{"relevant_indices": []}}

    Do not provide any explanation or preamble. Only return the JSON object.

    ---
    USER QUERY:
    {query}

    ---
    DOCUMENTS:
    {documents}
    """
)

STEP_DESCRIPTIONS = {
    "rewrite_query": "✍️ Optimizing query...",
    "retrieve_from_db": "🔎 Searching internal knowledge base...",
    "grade_documents": "⚖️ Grading document relevance...", 
    "final_results": "✅ Preparing final answer...", 
    "router": "🧭 Analyzing and routing for external search...",
    "web_search": "🌐 Searching the web...",
    "arxiv_search": "🔬 Searching ArXiv...",
    "setup_loop": "⚙️ Preparing to process new information...",
    "summarize_item": "📄 Summarizing new information...",
    "add_to_db": "💾 Saving new information to database...",
}


TRANSLATION_FEEDBACK_PROMPT = PromptTemplate.from_template(
    """
    You are a meticulous English language examiner providing feedback on a user's translation from Vietnamese to English.

    **Your Goal:** Analyze the user's English translation of a Vietnamese sentence. You must provide a score (0-100) and detailed, categorized feedback.
    **CRITICAL INSTRUCTION: All textual analysis in the "feedback" field MUST be written in VIETNAMESE to help the user understand their mistakes.**
    **Evaluation Criteria:**
    1.  **Grammar:** Is the English sentence grammatically correct?
    2.  **Vocabulary:** Is the word choice accurate and appropriate?
    3.  **Nuance & Style:** Does the translation capture the tone and nuance of the original? Does it sound natural to a native English speaker?

    **Crucial Output Format:** You MUST respond ONLY with a valid JSON object. Do not add any text before or after the JSON. The structure must be exactly as follows:
    {{
      "score": number,
      "categorized_feedback": {{
        "grammar": "string",
        "vocabulary": "string",
        "nuance": "string"
      }},
      "suggestions": ["string"]
    }}

    - "score": Your numerical score from 0-100.
    - "categorized_feedback":
        - "grammar": Provide feedback on grammar in Vietnamese. If there are no issues, state "No grammar issues found."
        - "vocabulary": Provide feedback on vocabulary in Vietnamese. If there are no issues, state "No vocabulary issues found."
        - "nuance": Provide feedback on style and naturalness in Vietnamese. If there are no issues, state "The translation captures the nuance well."
    - "suggestions": Provide a list containing one or more improved or alternative English translations.

    ---
    **Original Vietnamese Passage (for context):**
    {original_passage}

    ---
    **Original Vietnamese Sentence:**
    {current_sentence}

    ---
    **User's English Translation:**
    {user_translation}

    ---
    **Your JSON Response:**
    """
)