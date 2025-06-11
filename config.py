import os
from dotenv import load_dotenv

load_dotenv()  

AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SCRAPEGRAPH_API_KEY = os.getenv("SCRAPEGRAPH_API_KEY")


print(AGENTOPS_API_KEY)