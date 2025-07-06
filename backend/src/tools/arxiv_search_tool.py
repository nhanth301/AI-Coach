from langchain_core.tools import BaseTool
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any



class Arxiv_Search_Tool(BaseTool):
    """A tool for searching research papers on ArXiv."""
    
    name: str = "arxiv_search"
    description: str = (
        "A wrapper around arxiv.org to search for research papers. "
        "Useful for when you need to answer questions about science, technology, "
        "machine learning, physics, and other academic topics from reliable sources. "
        "Provides titles, authors, abstracts, and links."
    )


    def _run(self, query: str, search_type: str,max_results: int = 5) -> List[Dict[str, Any]]:
        """Use the tool."""
        page_size = 25 
        base_url = "https://arxiv.org/search/"
        results = []
        start = 0

        clamped_max_results = min(max_results, 50) 

        while len(results) < clamped_max_results:
            params = {
                "searchtype": search_type,
                "query": query,
                "abstracts": "show",
                "order": "-announced_date_first",
                "size": str(page_size),
                "start": str(start)
            }

            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status() 
                soup = BeautifulSoup(response.content, 'html.parser')

                papers = soup.find_all("li", class_="arxiv-result")
                if not papers:
                    break 

                for paper in papers:
                    if len(results) >= clamped_max_results:
                        break

                    title = paper.find("p", class_="title").text.strip()
                    authors_p = paper.find("p", class_="authors")
                    authors = re.sub(r'^Authors:\s*', '', authors_p.text).strip()
                    
                    abstract_span = paper.find("span", class_="abstract-full")
                    abstract = abstract_span.text.replace("△ Less", "").strip()
                    
                    link_tag = paper.find("p", class_="list-title").find("a")
                    link = link_tag["href"] if link_tag else "No link found"

                    results.append({
                        "title": title,
                        "authors": authors,
                        "abstract": abstract,
                        "link": link
                    })

                start += page_size

            except requests.RequestException as e:
                raise e

        return results[:clamped_max_results]

