from langchain_core.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchResults


class Web_Searcher_Tool(BaseTool):
    """A tool for searching the web using DuckDuckGo."""
    name: str = "web_searcher"
    description: str = "Useful for when you need to answer questions about current events or look up information on the web."
    
    def _run(self, query: str):
        """Use the tool."""
        searcher = DuckDuckGoSearchResults(output_format="list", num_results=3)
        return searcher.invoke(query)

