import os
from dotenv import load_dotenv
from typing import Dict

def load_environment() -> Dict[str, str]:
    """Load and validate all required environment variables"""
    load_dotenv()  
    
    required_vars = {
        'AGENTOPS_API_KEY': 'AgentOps API key',
        'OPENROUTER_API_KEY': 'OpenRouter API key',
        'TAVILY_API_KEY': 'Tavily API key',
        'FIRECRAWL_API_KEY' : 'FireCrawl API key',
        'CEREBRAS_API_KEY' : 'Cerebas Api key',
        'NVIDIA_API_KEY':'Nvidia NIM key',
        'GEMINI_API_KEY':'Gemini API key'
    }
    
    config = {}
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Missing required environment variable: {var} ({description})")
        config[var] = value
    
    return config

# Initialize and export all configs
try:
    CONFIG = load_environment()
except ValueError as e:
    print(f"Configuration error: {str(e)}")
    raise