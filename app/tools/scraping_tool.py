from crewai.tools import tool
from app.clients import get_scrape_client , get_fire_crawl_client
from app.models import SingleJobData
import json

@tool
def web_scraping_tool(page_url : str):
    """
    An AI Tool to help an agent to scrape a web page

    Example:
    web_scraping_tool(
        page_url="https://www.indeed.com/viewjob?jk=013dfb26c48a8ecd"
    )
    """
    scraper = get_scrape_client()
    
    details = scraper.smartscraper(
        website_url= page_url,
        user_prompt= "Extract ```json\n" + json.dumps(SingleJobData.model_json_schema()) + "```\n From the web page"
    )

    return {
        "Page URL" : page_url,
        "Details" : details
    }

@tool
def web_scraping_firecrawl(page_url : str):
    """
    An AI Tool using FireCrawl to help an agent to scrape a web page

    Example:
    web_scraping_firecrawl(
        page_url="https://www.indeed.com/viewjob?jk=013dfb26c48a8ecd"
    )
    """
    scraper = get_fire_crawl_client()

    results = scraper.scrape_url(
        url=page_url,
        formats=['markdown']   
    )

    return{
        "Page URL" : page_url,
        "Details"  : results
    }