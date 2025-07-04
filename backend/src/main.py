from tools.web_search_tool import Web_Searcher_Tool
from tools.arxiv_search_tool import Arxiv_Search_Tool

tool = Arxiv_Search_Tool()

res = tool.invoke("image style transfer")
for r in res:
    print(r['title'])
