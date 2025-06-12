from crewai import LLM
import agentops
from tavily import TavilyClient
from scrapegraph_py import Client
from config import CONFIG


import os
from functools import lru_cache

# This decorator ensures the function is only run once.
# The result is cached and returned on all subsequent calls.
@lru_cache(maxsize=None)
def get_llm() -> LLM:
    """Initializes and returns a shared LLM instance."""
    print("--- Initializing LLM Client (This will run only once) ---")
    return LLM(
        model="openrouter/deepseek/deepseek-r1-0528:free",
        base_url="https://openrouter.ai/api/v1",
        api_key=CONFIG['OPENROUTER_API_KEY'],
        temperature=0
    )

@lru_cache(maxsize=None)
def get_search_client() -> TavilyClient:
    """Initializes and returns a shared TavilyClient instance."""
    print("--- Initializing Tavily Client (This will run only once) ---")
    return TavilyClient(api_key=CONFIG['TAVILY_API_KEY'])

@lru_cache(maxsize=None)
def get_scrape_client() -> Client:
    """Initializes and returns a shared ScrapeGraph Client instance."""
    print("--- Initializing ScrapeGraph Client (This will run only once) ---")
    return Client(api_key=CONFIG['SCRAPEGRAPH_API_KEY'])

def initialize_agentops():
    """Initializes AgentOps. This doesn't need to return anything."""
    print("--- Initializing AgentOps (This will run only once) ---")
    # Using a simple flag to ensure it's not re-initialized
    if not getattr(initialize_agentops, "has_run", False):
        agentops.init(
            api_key=CONFIG['AGENTOPS_API_KEY'],
            skip_auto_end_session=True,
            default_tags=['crewai']
        )
        setattr(initialize_agentops, "has_run", True)