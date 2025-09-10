from crewai.tools import tool
from app.clients import get_search_client 


@tool
def tavily_search_engine_tool(query: str):
    """Useful for search-based queries. Use this to find current information about any query related pages using a search engine"""

    tavliy_search_client = get_search_client()
    return tavliy_search_client.search(query)