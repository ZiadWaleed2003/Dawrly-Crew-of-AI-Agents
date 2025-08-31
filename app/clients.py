from crewai import LLM
import agentops
from firecrawl import FirecrawlApp
from tavily import TavilyClient
from scrapegraph_py import Client
from config import CONFIG


from functools import lru_cache

# This decorator ensures the function is only run once.
# The result is cached and returned on all subsequent calls.
@lru_cache(maxsize=None)
def get_llm_main() -> LLM:
    """Initializes and returns a shared LLM instance."""
    print("--- Initializing LLM Client (This will run only once) deepseek---")
    
    try:
        llm = LLM(
            model="deepseek-ai/deepseek-v3.1",
            base_url = "https://integrate.api.nvidia.com/v1",
            api_key=CONFIG['NVIDIA_API_KEY'],
            temperature=0
        )
        return llm
    except Exception as e:
        print(f"ERROR initializing LLM: {str(e)}")
        raise

# @lru_cache(maxsize=None)
# def get_llm_main() -> LLM:
#     """Initializes and returns a shared LLM instance."""
#     print("--- Initializing LLM Client (This will run only once) deepseek from openrouter---")
    
#     try:
#         llm = LLM(
#             model="openrouter/deepseek/deepseek-r1-0528:free",
#             base_url = "https://openrouter.ai/api/v1",
#             api_key=CONFIG['OPENROUTER_API_KEY'],
#             temperature=0
#         )
#         return llm
#     except Exception as e:
#         print(f"ERROR initializing LLM: {str(e)}")
#         raise



@lru_cache(maxsize=None)
def get_llm_sec() -> LLM:
    """Initializes and returns a shared LLM instance."""
    print("--- Initializing LLM Client (This will run only once) Qwen 3---")
    
    try:
        llm = LLM(
            model="nvidia_nim/qwen/qwen3-235b-a22b",
            base_url = "https://integrate.api.nvidia.com/v1",
            api_key=CONFIG['NVIDIA_API_KEY'],
            temperature=0
        )
        return llm
    except Exception as e:
        print(f"ERROR initializing LLM: {str(e)}")
        raise

@lru_cache(maxsize=None)
def get_llm_with_tool_use() -> LLM:
    """Initializes and returns a shared LLM instance."""
    print("--- Initializing LLM Client (This will run only once) Kimi-k2---")
    
    try:
        llm = LLM(
            model="moonshotai/kimi-k2-instruct",
            base_url = "https://integrate.api.nvidia.com/v1",
            api_key=CONFIG['NVIDIA_API_KEY'],
            temperature=0
        )
        return llm
    except Exception as e:
        print(f"ERROR initializing LLM: {str(e)}")
        raise


@lru_cache(maxsize=None)
def get_llm_search() -> LLM:
    """Initializes and returns a shared LLM instance."""
    print("--- Initializing LLM Client (This will run only once) Gemini 2.0 flash ---")
    
    try:
        llm = LLM(
            model="gemini/gemini-2.0-flash",
            api_key=CONFIG['GEMINI_API_KEY'],
            temperature=0
        )
        return llm
    except Exception as e:
        print(f"ERROR initializing LLM: {str(e)}")
        raise

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

@lru_cache(maxsize=None)
def get_fire_crawl_client() ->FirecrawlApp:
    """Initializes and returns a shared FireCrawl Client instance."""
    print("--- Initializing FireCrawl Client (This will run only once) ---")

    return FirecrawlApp(
        api_key=CONFIG['FIRECRAWL_API_KEY']
    )


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