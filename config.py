import os
from dotenv import load_dotenv

load_dotenv()  

os.environ['AGENTOPS_API_KEY'] = os.getenv("AGENTOPS_API_KEY")
os.environ['OPENROUTER_API_KEY'] = os.getenv("OPENROUTER_API_KEY")
os.environ['TAVILY_API_KEY'] = os.getenv("TAVILY_API_KEY")
os.environ['SCRAPEGRAPH_API_KEY'] = os.getenv("SCRAPEGRAPH_API_KEY")