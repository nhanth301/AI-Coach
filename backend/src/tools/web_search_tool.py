from langchain_core.tools import BaseTool
from googlesearch import search
import requests
from bs4 import BeautifulSoup


def google_scrape(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except:
        return None
    soup = BeautifulSoup(response.content, "html.parser")
    return soup.title.text if soup.title is not None else None

class Web_Searcher_Tool(BaseTool):
    """A tool for searching the web using DuckDuckGo."""
    name: str = "web_searcher"
    description: str = "Useful for when you need to answer questions about current events or look up information on the web."
    
    def _run(self, query: str):
        """Use the tool."""
        done = 0
        results = []
        for url in search(query, num_results=100):
            res = google_scrape(url)
            if res:
                results.append({'url': url, 'title': res})
                done += 1
            if done == 5:
                break
        return results

