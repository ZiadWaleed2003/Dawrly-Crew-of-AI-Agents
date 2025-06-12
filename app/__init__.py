from crewai import LLM
import agentops
from tavily import TavilyClient
from scrapegraph_py import Client

import os



agentops.init(
    api_key=os.environ['AGENTOPS_API_KEY'],
    skip_auto_end_session=True,
    default_tags=['crewai']
)

deepseek_r1 = LLM(
    model="openrouter/deepseek/deepseek-r1-0528:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ['OPENROUTER_API_KEY'],
    temperature=0
)
search_client = TavilyClient(api_key=os.environ['TAVILY_API_KEY'])
scrape_client = Client(api_key=os.environ['SCRAPEGRAPH_API_KEY'])
