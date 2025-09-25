from crewai import LLM
import agentops
from firecrawl import FirecrawlApp
from tavily import TavilyClient
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.rate_limiters import InMemoryRateLimiter

from config import CONFIG

from functools import lru_cache

# This decorator ensures the function is only run once.
# The result is cached and returned on all subsequent calls.
@lru_cache(maxsize=None)
def get_llm_main() -> LLM:
    """Initializes and returns a shared LLM instance."""
    print("--- Initializing LLM Client (This will run only once) deepseek r1---")
    
    try:
        llm = LLM(
            model="deepseek-ai/deepseek-r1",
            base_url = "https://integrate.api.nvidia.com/v1",
            api_key=CONFIG['NVIDIA_API_KEY'],
            temperature=0
        )
        return llm
    except Exception as e:
        print(f"ERROR initializing LLM: {str(e)}")
        raise




@lru_cache(maxsize=None)
def get_LangGraph_model():
    """Initializes and returns a shared LLM instance."""
    print("--- Initializing LLM Client (This will run only once) LLama 3 from Nvidia NIM---")

    try:


        rate_limiter = InMemoryRateLimiter(
                requests_per_second= 40 / 60,  # since I'm using Nvidia NIM here so I'm getting 40 RPM max 
                check_every_n_seconds=0.1,  
                max_bucket_size=1
            )

        model = ChatNVIDIA(
            model="meta/llama-3.3-70b-instruct",
            model_provider="langchain-nvidia-ai-endpoints",
            base_url = "https://integrate.api.nvidia.com/v1",
            temperature = 0,
            nvidia_api_key = CONFIG['NVIDIA_API_KEY'],
            rate_limiter = rate_limiter
        )

        return model

    except Exception as e:

        print(f"ERROR initializing LLM: {str(e)} : Nvidia from Langgraph")
        raise




@lru_cache(maxsize=None)
def get_llm_sec() -> LLM:
    """Initializes and returns a shared LLM instance."""
    print("--- Initializing LLM Client (This will run only once) LLama 3 from cerebras---")
    
    try:
        llm = LLM(
            model="cerebras/llama-3.3-70b",
            api_key=CONFIG['CEREBRAS_API_KEY'],
            temperature=0
        )
        return llm
    except Exception as e:
        print(f"ERROR initializing LLM: {str(e)}")
        raise

@lru_cache(maxsize=None)
def get_llm_with_tool_use() -> LLM:
    """Initializes and returns a shared LLM instance."""
    print("--- Initializing LLM Client (This will run only once) llama-3.3-70b-instruct from Nvidia NIM---")
    
    try:
        llm = LLM(
            model="meta/llama-3.3-70b-instruct",
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

# @lru_cache(maxsize=None)
# def get_llm_search() -> LLM:
#     """Initializes and returns a shared LLM instance."""
#     print("--- Initializing LLM Client (This will run only once) llama-3.1-8b-instant ---")
    
#     try:
#         llm = LLM(
#             model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
#             api_key=CONFIG['GROQ_API_KEY'],
#             temperature=0
#         )
#         return llm
#     except Exception as e:
#         print(f"ERROR initializing LLM: {str(e)}")
#         raise

@lru_cache(maxsize=None)
def get_search_client() -> TavilyClient:
    """Initializes and returns a shared TavilyClient instance."""
    print("--- Initializing Tavily Client (This will run only once) ---")
    return TavilyClient(api_key=CONFIG['TAVILY_API_KEY'])


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